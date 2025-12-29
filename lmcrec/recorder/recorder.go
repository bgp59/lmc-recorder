package recorder

import (
	"bytes"
	"compress/zlib"
	"context"
	"crypto/tls"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"os"
	"path"
	"strconv"
	"strings"
	"sync"
	"time"

	"golang.org/x/sys/unix"

	"lmcrec/codec"
)

const (
	SECURITY_KEY_FILE_PREFIX     = "file:"
	SECURITY_KEY_ENV_PREFIX      = "env:"
	RECORD_FILES_DIR_LOCK        = ".lck"
	RECORD_FILE_NAME_TIME_FORMAT = "2006-01-02/15:04:05-07:00" // i.e. yyyy-mm-dd/HH:MM:SS±HH:MM

	// Log consecutive identical HTTP error messages only so often:
	REPEAT_HTTP_ERROR_MSG_INTERVAL = 1 * time.Minute
)

const (
	SCAN_NO_ERR = iota
	SCAN_NON_PARSE_ERR
	SCAN_PARSE_ERR
	SCAN_FATAL_ERR
)

// List of HTTP response OK status codes:
var HttpRespStatusCodeOk = map[int]bool{
	http.StatusOK: true,
}

// Declare some interfaces implemented by the real objects to be able to replace
// them w/ mocks for testing:
type HttpClientDoer interface {
	Do(req *http.Request) (*http.Response, error)
}

type Lmcrec struct {
	// The instance of the recorder:
	Inst string

	// Scan interval:
	ScanInterval time.Duration

	// Flush interval:
	//	 < 0: disable flush
	//  == 0: always flush at the end of the scan
	//   > 0: flush at/after interval since last flush
	flushInterval time.Duration

	// When the last flush occurred:
	lastFlushTs time.Time

	// Checkpoint interval:
	//  <= 0: disabled
	//   > 0: checkpoint at/after interval since last checkpoint
	checkpointInterval time.Duration

	// When the last checkpoint occurred:
	lastCheckpointTs time.Time

	// Rollover interval:
	// <= 0: disabled
	//  > 0: rollover to a new files at/after interval since last rollover
	rolloverInterval time.Duration

	// When the last rollover occurred:
	lastRolloverTs time.Time

	// Whether to rollover at midnight local time or not:
	midnightRollover bool

	// Midnight timestamp, determined when the record file is opened:
	midnightTs time.Time

	// Parse error threshold: when the parseErrorGauge reaches this value, stop
	// the recorder.
	parseErrorThreshold int

	// Parse error gauge: incremented at parse error, decremented, 0 floored,
	// otherwise.
	parseErrorGauge int

	// Needed for REST API:
	url            string        // needed for config logging
	tcpConnTimeout time.Duration // needed for config logging
	tcpKeepAlive   any           // needed for config logging (it may be not set)
	httpClient     HttpClientDoer
	httpRequest    *http.Request
	// If the remote process is down then connection refused error messages
	// would be logged with every scan, filling the logs. Keep track of the last
	// message and its occurrence count and log it only so often.
	lastHttpErrMsg   string
	httpErrMsgCount  int
	lastHttpErrMsgTs time.Time

	// The encoder:
	recordFilesDir       string
	recordFilesDirLock   string
	recordFilesDirLockFh *os.File
	bufSize              int
	compressionLevel     int
	// recordFileNameSuffix is passed as an arg to new encoder function. If
	// non-empty then it will signify that the current file is continuation
	// rollover of the previous one. recordFileNameSuffix will be set to empty in
	// case of error.
	recordFileNameSuffix string
	encoder              codec.LmcrecFileEncoder

	// The recordableParser:
	recordableParser LmcParseRecorder

	// The logger:
	logger       RecorderLogger
	configLogged bool // used to trigger config logging at 1st scan

	// Needed for config logging:

	// Concurrent operations lock:
	lck *sync.Mutex

	// Needed for testing:
	timeNowFunc              func() time.Time
	newLmcrecFileEncoderFunc func(fileName string, bufSize, compressionLvl int, useCheckpoint bool, prevFileName string, version string) (codec.LmcrecFileEncoder, error)
}

var recorderLogger = RootLogger.NewCompLogger("recorder")

func NewLmcrec(config *LmcrecConfig, loop *TaskLoop) (*Lmcrec, error) {
	dialer := &net.Dialer{
		Timeout: *config.TcpConnTimeout,
	}
	if config.TcpKeepAlive != nil {
		dialer.KeepAlive = *config.TcpKeepAlive
	}
	transport := &http.Transport{
		DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
			if conn, err := dialer.DialContext(ctx, network, addr); err == nil {
				if tcpConn, ok := conn.(*net.TCPConn); ok {
					tcpConn.SetLinger(0) // Set linger to 0 to force immediate RST on close
				}
				return conn, nil
			} else {
				return nil, err
			}
		},
		DisableKeepAlives: true,
	}
	if *config.IgnoreTlsVerify {
		transport.TLSClientConfig = &tls.Config{
			InsecureSkipVerify: true,
		}
	}
	parsedUrl, err := url.Parse(*config.URL)
	if err != nil {
		return nil, err
	}
	req := &http.Request{
		Method: http.MethodGet,
		URL:    parsedUrl,
	}

	isRemote := !strings.HasPrefix(strings.ToLower(parsedUrl.Host), "localhost") && !strings.HasPrefix(parsedUrl.Host, "127.")
	if *config.CompressedRequests == COMPRESSED_REQUESTS_REMOTE_ONLY && isRemote ||
		len(*config.CompressedRequests) > 0 && strings.HasPrefix("true", strings.ToLower(*config.CompressedRequests)) {
		if req.Header == nil {
			req.Header = http.Header{}
		}
		req.Header.Add("Accept-Encoding", "deflate")
	}

	inst := *config.Inst
	if inst == "" {
		normalizedHost := strings.ReplaceAll(
			strings.ToLower(parsedUrl.Host),
			":", "-",
		)
		inst = path.Join(normalizedHost, parsedUrl.Path)
	}

	if config.SecurityKey != nil && *config.SecurityKey != "" {
		securityKey := *config.SecurityKey

		if strings.HasPrefix(securityKey, SECURITY_KEY_FILE_PREFIX) {
			securityKeyFile := expandInstEnv(securityKey[len(SECURITY_KEY_FILE_PREFIX):], inst)
			if f, err := os.Open(securityKeyFile); err != nil {
				return nil, err
			} else {
				defer f.Close()
				if b, err := io.ReadAll(f); err != nil {
					return nil, err
				} else {
					securityKey = strings.TrimSpace(string(b))
				}
			}
		} else if strings.HasPrefix(securityKey, SECURITY_KEY_ENV_PREFIX) {
			securityKey = os.Getenv(securityKey[len(SECURITY_KEY_ENV_PREFIX):])
		}

		if securityKey != "" {
			if req.Header == nil {
				req.Header = http.Header{}
			}
			req.Header.Add("Security-Key", securityKey)
		}
	}

	if loop != nil && loop.Ctx != nil {
		req = req.WithContext(loop.Ctx)
	}

	logger := recorderLogger.WithField("inst", inst)
	recordFilesDir := expandInstEnv(*config.RecordFilesDir, inst)
	bufSize := *config.BufSize
	compressionLevel := *config.CompressionLevel

	if err = os.MkdirAll(recordFilesDir, os.ModePerm); err != nil {
		return nil, err
	}
	recordFilesDirLock := path.Join(recordFilesDir, RECORD_FILES_DIR_LOCK)
	recordFilesDirLockFh, err := os.Create(recordFilesDirLock)
	if err != nil {
		return nil, err
	} else if err = unix.Flock(int(recordFilesDirLockFh.Fd()), unix.LOCK_EX|unix.LOCK_NB); err != nil {
		return nil, fmt.Errorf("fail to acquire record dir lock on %s: %v", recordFilesDirLock, err)
	}

	recorder := &Lmcrec{
		Inst:               inst,
		ScanInterval:       *config.ScanInterval,
		flushInterval:      *config.FlushInterval,
		checkpointInterval: *config.CheckpointInterval,
		rolloverInterval:   *config.RolloverInterval,
		// Hardcode midnight rollover since the record file is under a
		// yyyy-mm-dd sub-dir. It makes sense to keep all the records belonging
		// to one day under the same dir.
		midnightRollover:    true, // *config.MidnightRollover,
		parseErrorThreshold: *config.ParseErrorThreshold,
		url:                 *config.URL,
		tcpConnTimeout:      *config.TcpConnTimeout,
		httpClient: &http.Client{
			Transport: transport,
			Timeout:   *config.RequestTimeout,
		},
		httpRequest:          req,
		logger:               logger,
		lck:                  &sync.Mutex{},
		recordFilesDir:       recordFilesDir,
		recordFilesDirLock:   recordFilesDirLock,
		recordFilesDirLockFh: recordFilesDirLockFh,
		bufSize:              bufSize,
		compressionLevel:     compressionLevel,
		recordableParser:     NewRecordableLmcParser(),
		timeNowFunc:          time.Now,
		newLmcrecFileEncoderFunc: func(fileName string, bufSize, compressionLvl int, useCheckpoint bool, prevFileName string, version string) (codec.LmcrecFileEncoder, error) {
			// Simply for return type conversion, this should be inlined if the compiler is half decent:
			return codec.NewCodecLmcrecFileEncoder(fileName, bufSize, compressionLvl, useCheckpoint, prevFileName, version)
		},
	}

	return recorder, nil
}

func (r *Lmcrec) newEncoder(ts time.Time) error {
	ts = ts.Local()
	encoder, err := r.newLmcrecFileEncoderFunc(
		path.Join(
			r.recordFilesDir,
			ts.Format(RECORD_FILE_NAME_TIME_FORMAT)+codec.LMCREC_FILE_SUFFIX,
		),
		r.bufSize,
		r.compressionLevel,
		r.checkpointInterval > 0,
		r.recordFileNameSuffix,
		Version,
	)
	if err != nil {
		return err
	}
	r.encoder = encoder
	// To store the file name suffix retrieve the name from the encoder, since
	// it may have added some suffix.
	recordFileNameSuffix := encoder.GetFileName()
	if r.recordFilesDir != "" {
		recordFileNameSuffix = recordFileNameSuffix[len(r.recordFilesDir)+1:]
	}
	r.recordFileNameSuffix = recordFileNameSuffix
	r.lastRolloverTs = ts
	y, m, d := ts.Date()
	r.midnightTs = time.Date(y, m, d, 0, 0, 0, 0, ts.Location()).Add(24 * time.Hour)
	r.lastCheckpointTs = ts
	r.lastFlushTs = ts
	if r.logger != nil {
		r.logger.Infof("%s opened", r.encoder.GetFileName())
	}
	return nil
}

func (r *Lmcrec) flushEncoder() error {
	if encoder := r.encoder; encoder != nil {
		if err := encoder.Flush(); err != nil {
			return fmt.Errorf("error flushing %s: %v", r.encoder.GetFileName(), err)
		}
	}
	return nil
}

func (r *Lmcrec) closeEncoder() error {
	if encoder := r.encoder; encoder != nil {
		logger := r.logger
		fileName := encoder.GetFileName()
		if err := encoder.Close(); err != nil {
			return fmt.Errorf("error closing %s: %v", fileName, err)
		} else if logger != nil {
			logger.Infof("%s closed", fileName)
		}
		r.encoder = nil
	}
	return nil
}

func (r *Lmcrec) reportError(err any, errType int) bool {
	logger, parseErrorThreshold := r.logger, r.parseErrorThreshold

	if errType == SCAN_PARSE_ERR {
		r.parseErrorGauge++
		if parseErrorThreshold > 0 && r.parseErrorGauge >= parseErrorThreshold {
			err = fmt.Sprintf("%v: parse error threshold %d reached", err, parseErrorThreshold)
			errType = SCAN_FATAL_ERR
		}
	}
	if err != nil && logger != nil {
		logger.Error(err)
	}
	if err = r.closeEncoder(); err != nil && logger != nil {
		logger.Error(err)
		errType = SCAN_FATAL_ERR
	}

	r.recordFileNameSuffix = ""

	return errType != SCAN_FATAL_ERR // continue running for non fatal error
}

func (r *Lmcrec) logConfig() {
	logger := r.logger
	if logger != nil {
		logger.Infof("URL=%s", r.url)
		if r.httpRequest != nil {
			for hdr, hdrVals := range r.httpRequest.Header {
				vals := strings.Join(hdrVals, ", ")
				if hdr == "Security-Key" {
					vals = "xxxxx"
				}
				logger.Infof("header=%s: %s", hdr, vals)
			}
		}
		if httpClient, ok := r.httpClient.(*http.Client); ok {
			logger.Infof("request_timeout=%s", httpClient.Timeout)
			logger.Infof("tcp_conn_timeout=%s", r.tcpConnTimeout)
			if r.tcpKeepAlive != nil {
				logger.Infof("tcp_keep_alive=%s", r.tcpKeepAlive)
			}
		}
		logger.Infof("scan_interval=%s", r.ScanInterval)
		logger.Infof("flush_interval=%s", r.flushInterval)
		logger.Infof("checkpoint_interval=%s", r.checkpointInterval)
		logger.Infof("rollover_interval=%s", r.rolloverInterval)
		logger.Infof("midnight_rollover=%v", r.midnightRollover)
		logger.Infof("parse_error_threshold=%d", r.parseErrorThreshold)
		logger.Infof("record_files_dir=%s", r.recordFilesDir)
		if r.compressionLevel != 0 {
			explanation := ""
			if r.compressionLevel == zlib.DefaultCompression {
				explanation = " (default compression)"
			}
			logger.Infof("compression_level=%d%s", r.compressionLevel, explanation)
		} else {
			explanation := ""
			if r.bufSize < 0 {
				explanation = " (default iobuf)"
			} else if r.bufSize == 0 {
				explanation = " (no buffering)"
			}
			logger.Infof("buf_size=%d%s", r.bufSize, explanation)
		}
	}
}

func (r *Lmcrec) formatHttpResponseStatus(resp *http.Response) string {
	status := resp.Status
	if status == "" {
		status = fmt.Sprintf("%d %s", resp.StatusCode, http.StatusText(resp.StatusCode))
	}
	if r.httpRequest != nil {
		return fmt.Sprintf("%s %s: %s", r.httpRequest.Method, r.httpRequest.URL.String(), status)
	} else {
		// Fallback for mock testing:
		return fmt.Sprintf("pseudo GET %s: %s", r.url, status)
	}
}

// Perform one scan and return true/false for the task loop. Recorder errors are
// considered non-recoverable whereas parsing errors are subject error gauge /
// threshold mechanism.
func (r *Lmcrec) Scan() bool {
	r.lck.Lock()
	defer r.lck.Unlock()

	// Log config, if this this the 1st invocation:
	if !r.configLogged {
		r.logConfig()
		r.configLogged = true
	}

	// The scan duration will be measured from before the request is being made:
	startTs := r.timeNowFunc()

	// Request a scan. Close the current encoder if an error occurred to force a
	// rollover.
	resp, err := r.httpClient.Do(r.httpRequest)

	prevHttpErr := r.lastHttpErrMsg != ""
	if err != nil {
		httpErrMsg := err.Error()
		if httpErrMsg != r.lastHttpErrMsg {
			r.lastHttpErrMsg = httpErrMsg
			r.httpErrMsgCount = 1
		} else {
			r.httpErrMsgCount++
			if startTs.Sub(r.lastHttpErrMsgTs) >= REPEAT_HTTP_ERROR_MSG_INTERVAL {
				err = fmt.Errorf("%v (repeated %d times)", err, r.httpErrMsgCount)
			} else {
				err = nil
			}
		}
		if err != nil {
			r.lastHttpErrMsgTs = startTs
		}
		return r.reportError(err, SCAN_NON_PARSE_ERR)
	} else if prevHttpErr {
		r.lastHttpErrMsg = ""
	}
	defer resp.Body.Close()

	if !HttpRespStatusCodeOk[resp.StatusCode] {
		return r.reportError(fmt.Errorf("%s", r.formatHttpResponseStatus(resp)), SCAN_PARSE_ERR)
	} else if prevHttpErr {
		// Log success after error:
		if r.logger != nil {
			r.logger.Info(r.formatHttpResponseStatus(resp))
		}
	}

	// Parse the response headers looking for proper content type and whether
	// the response is compressed or not.
	isJson, isDeflated := false, false

	hasHeaderVal := func(hdrVals []string, value string) bool {
		for _, hdrVal := range hdrVals {
			if i := strings.Index(hdrVal, ";"); i > 0 {
				hdrVal = hdrVal[:i]
			}
			if hdrVal == value {
				return true
			}
		}
		return false
	}

	contentLength := 0
	for hdr, hdrVals := range resp.Header {
		switch hdr {
		case "Content-Length":
			if len(hdrVals) > 0 {
				if contentLength, err = strconv.Atoi(hdrVals[0]); err != nil {
					return r.reportError(
						fmt.Sprintf("Content-Length: %s: %v", hdrVals[0], err),
						SCAN_NON_PARSE_ERR,
					)
				}
			}
		case "Content-Type":
			isJson = hasHeaderVal(hdrVals, "application/json")
		case "Content-Encoding":
			isDeflated = hasHeaderVal(hdrVals, "deflate")
		}
	}

	if !isJson {
		return r.reportError("Non JSON content", SCAN_FATAL_ERR)
	}

	// Extract the body reader:
	body := resp.Body
	if isDeflated {
		body, err = zlib.NewReader(resp.Body)
		if err != nil {
			return r.reportError(err, SCAN_NON_PARSE_ERR)
		}
		defer body.Close()
	}

	firstTimeFlush, checkpoint, noNewEvents := false, false, false

	if r.encoder != nil {
		if r.midnightRollover && (startTs.After(r.midnightTs) || startTs.Equal(r.midnightTs)) ||
			r.rolloverInterval > 0 && startTs.Sub(r.lastRolloverTs) >= r.rolloverInterval {
			if err = r.closeEncoder(); err != nil {
				r.reportError(err, SCAN_FATAL_ERR)
			}
			noNewEvents = true
		} else if r.checkpointInterval > 0 && startTs.Sub(r.lastCheckpointTs) >= r.checkpointInterval {
			checkpoint = true
			noNewEvents = true
		}
	} else {
		noNewEvents = true
	}

	// Parse the response:
	recordableParser := r.recordableParser
	processChanged, scanInInstCount, scanInVarCount, err := recordableParser.Parse(body, noNewEvents)
	if err != nil {
		return r.reportError(fmt.Errorf("parse error: %v", err), SCAN_PARSE_ERR)
	}

	if processChanged {
		if r.logger != nil {
			r.logger.Warn("process change detected")
		}
		// Force rollover:
		if err = r.closeEncoder(); err != nil {
			return r.reportError(err, SCAN_FATAL_ERR)
		}
		r.recordFileNameSuffix = ""
		checkpoint = false
	}

	if r.encoder == nil {
		if err = r.newEncoder(startTs); err != nil {
			return r.reportError(err, SCAN_FATAL_ERR)
		}
		// Force a flush for the first scan of a new encoder to create the info file:
		firstTimeFlush = true
	} else if checkpoint {
		if err = r.encoder.Checkpoint(startTs); err != nil {
			return r.reportError(err, SCAN_FATAL_ERR)
		}
		r.lastCheckpointTs = startTs
		r.lastFlushTs = startTs
	}

	encoder := r.encoder

	// The timestamp record for the scan:
	if err = encoder.TimestampUsec(startTs); err != nil {
		return r.reportError(err, SCAN_FATAL_ERR)
	}

	scanOutVarCount, err := recordableParser.Record(encoder, noNewEvents || processChanged)
	if err != nil {
		return r.reportError(err, SCAN_FATAL_ERR)
	}

	// The tally:
	if err = encoder.ScanTally(contentLength, scanInInstCount, scanInVarCount, scanOutVarCount); err != nil {
		return r.reportError(err, SCAN_FATAL_ERR)
	}

	// The duration:
	if err := encoder.DurationUsec(r.timeNowFunc().Sub(startTs)); err != nil {
		return r.reportError(err, SCAN_FATAL_ERR)
	}

	// Adjust the parse error gauge:
	if r.parseErrorGauge > 0 {
		r.parseErrorGauge--
	}

	// Post-parse actions:
	if firstTimeFlush || r.flushInterval == 0 || r.flushInterval > 0 && startTs.Sub(r.lastFlushTs) >= r.flushInterval {
		if err := r.flushEncoder(); err != nil {
			return r.reportError(err, SCAN_FATAL_ERR)
		}
		r.lastFlushTs = startTs
	}

	// Flip the variable storage current index:
	recordableParser.FlipCurrIndex()

	return true
}

// On-demand flush:
func (r *Lmcrec) Flush() error {
	r.lck.Lock()
	defer r.lck.Unlock()
	return r.flushEncoder()
}

// On-demand close to rollover to a new file:
func (r *Lmcrec) Close() error {
	r.lck.Lock()
	defer r.lck.Unlock()
	return r.closeEncoder()
}

// Shutdown completely:
func (r *Lmcrec) Shutdown() error {
	r.lck.Lock()
	defer r.lck.Unlock()

	errBuf := &bytes.Buffer{}

	if err := r.closeEncoder(); err != nil {
		fmt.Fprintf(errBuf, "%v", err)
	}
	if r.recordFilesDirLockFh != nil {
		if err := r.recordFilesDirLockFh.Close(); err != nil {
			if errBuf.Len() > 0 {
				errBuf.WriteString(", ")
			}
			fmt.Fprintf(errBuf, "error closing %s: %v", r.recordFilesDirLock, err)

		}
		r.recordFilesDirLockFh = nil
	}
	if errBuf.Len() > 0 {
		return fmt.Errorf("%s", errBuf.String())
	}
	return nil
}
