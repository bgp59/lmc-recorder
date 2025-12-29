package recorder

import (
	"fmt"
	"io"
	"os"
	"reflect"
	"strings"
	"sync"
	"time"

	"github.com/bgp59/logrusx"
	"gopkg.in/yaml.v3"

	"lmcrec/codec"
)

const (
	RECORDER_INST_PLACEHOLDER = "<INST>"

	COMPRESSED_REQUESTS_REMOTE_ONLY = "remote_only"

	RECORDER_CONFIG_LOG_FILE_DEFAULT = "$LMCREC_RUNTIME/log/" + RECORDER_INST_PLACEHOLDER + "/lmcrec.log"

	RECORDER_CONFIG_SCAN_INTERVAL_DEFAULT          = 5 * time.Second
	RECORDER_CONFIG_FLUSH_INTERVAL_DEFAULT         = 5 * time.Minute
	RECORDER_CONFIG_CHECKPOINT_INTERVAL_DEFAULT    = 30 * time.Minute
	RECORDER_CONFIG_ROLLOVER_INTERVAL_DEFAULT      = 6 * time.Hour
	RECORDER_CONFIG_MIDNIGHT_ROLLOVER_DEFAULT      = true
	RECORDER_CONFIG_PARSE_ERROR_THRESHOLD_DEFAULT  = 5
	RECORDER_CONFIG_URL_DEFAULT                    = "http://localhost:8080/sharedmem"
	RECORDER_CONFIG_SECURITY_KEY_DEFAULT           = ""
	RECORDER_CONFIG_IGNORE_TLS_VERIFY_DEFAULT      = false
	RECORDER_CONFIG_COMPRESSED_REQUESTS_DEFAULT    = COMPRESSED_REQUESTS_REMOTE_ONLY
	RECORDER_CONFIG_TCP_CONNECTION_TIMEOUT_DEFAULT = 1 * time.Second
	RECORDER_CONFIG_REQUEST_TIMEOUT_DEFAULT        = 2 * time.Second
	RECORDER_CONFIG_RECORD_FILES_DIR_DEFAULT       = "$LMCREC_RUNTIME/rec/" + RECORDER_INST_PLACEHOLDER
	RECORDER_CONFIG_RECORD_BUFSIZE_DEFAULT         = codec.USE_DEFAULT_BUFIO_SIZE
	RECORDER_CONFIG_COMPRESSION_LEVEL_DEFAULT      = codec.DEFAULT_COMPRESSION_LEVEL
)

// The config structure will store pointers to values. This way, when the config
// is loaded from a YAML file, fields not set will be left nil so they can be
// identified and completed from default values.
type LmcrecConfig struct {
	/////////////////////////////////////////////////
	// Recorder parameters:
	/////////////////////////////////////////////////

	// The instance of the recorder; if not set then the URL is used:
	Inst *string

	// Scan interval:
	ScanInterval *time.Duration `yaml:"scan_interval"`

	// Flush interval:
	//	 < 0: disable flush
	//  == 0: always flush at the end of the scan
	//   > 0: flush at/after interval since last flush
	FlushInterval *time.Duration `yaml:"flush_interval"`

	// Checkpoint interval.
	//  <= 0: disabled
	//   > 0: checkpoint at/after interval since last checkpoint
	CheckpointInterval *time.Duration `yaml:"checkpoint_interval"`

	// Rollover interval:
	// <= 0: disabled
	//  > 0: rollover to a new files at/after interval since last rollover
	RolloverInterval *time.Duration `yaml:"rollover_interval"`

	// Whether to force a rollover at midnight local time or not.
	MidnightRollover *bool `yaml:"midnight_rollover"`

	// Parse error threshold. There is a rest parser error gauge, incremented
	// every time an error occurs and decremented, 0 floored, otherwise. The
	// normal behavior after an error is to roll over the recording to a new
	// file. If the error conditions persist then there is a risk of filling the
	// file system with stub files that have partial data at best and the
	// threshold protects against such as scenario by stopping the scanner. Use
	// 0 to disable.
	ParseErrorThreshold *int `yaml:"parse_error_threshold"`

	/////////////////////////////////////////////////
	// REST HTTP parameters:
	/////////////////////////////////////////////////

	// REST URL:
	URL *string `yaml:"url"`

	// SecurityKey for authentication. It may take one the following forms:
	//
	//   "file:FILE_PATH": 		it will be read from FILE_PATH. The latter
	//	 						is subject to env var interpolation,
	// 							e.g. "file:$HOME/runtime/lmcrec/security_key"
	//
	//   "env:ENV_VAR":			it will be read from environment ENV_VAR
	//
	//   "SECURITY_KEY":		verbatim, not recommended since the config
	//							is most likely publicly readable
	SecurityKey *string `yaml:"security_key"`

	// Whether to request compressed response data or not. The valid values are
	// true, false and remote_only. For the last one compressed requests are
	// enabled if the host part of the URL is not "localhost" or "127.x.x.x".
	CompressedRequests *string `yaml:"compressed_requests"`

	// Request timeout:
	RequestTimeout *time.Duration `yaml:"request_timeout"`

	// Whether to allow self-signed certificates or not:
	IgnoreTlsVerify *bool `yaml:"ignore_tls_verify"`

	// TCP connection parameters:
	TcpConnTimeout *time.Duration `yaml:"tcp_conn_timeout"`
	TcpKeepAlive   *time.Duration `yaml:"tcp_keep_alive"`

	/////////////////////////////////////////////////
	// Encoder parameters:
	/////////////////////////////////////////////////

	// The record files directory. The string may contain the
	// RECORDER_INST_PLACEHOLDER which will be replaced with the actual instance
	// and $var environment variables which will be interpolated.
	RecordFilesDir *string `yaml:"record_files_dir"`

	// The buffer size for buffered, non-compressed writes:
	BufSize *int `yaml:"buf_size"`

	// The compression level:
	CompressionLevel *int `yaml:"compression_level"`
}

// A YAML loadable structure for the actual config file:
type LmcrecFileConfig struct {
	Default      *LmcrecConfig         `yaml:"default"`
	Recorders    []*LmcrecConfig       `yaml:"recorders"`
	LoggerConfig *logrusx.LoggerConfig `yaml:"logger"`
}

// The recorder may handle multiple sources in the future, so multiple calls to
// LoadLmcrecConfig(configFile...) with the same configFile may be made. Cache
// the 1st load for efficiency.
type LmcrecConfigFromFileCache struct {
	// Cache indexed by file path:
	fileConfig map[string]*LmcrecFileConfig
	// Concurrent access protection:
	lck *sync.Mutex
}

var lmcrecConfigFromFileCache = &LmcrecConfigFromFileCache{
	fileConfig: make(map[string]*LmcrecFileConfig),
	lck:        &sync.Mutex{},
}

func DefaultRecorderConfig() *LmcrecConfig {
	scanInterval := RECORDER_CONFIG_SCAN_INTERVAL_DEFAULT
	flushInterval := RECORDER_CONFIG_FLUSH_INTERVAL_DEFAULT
	checkpointInterval := RECORDER_CONFIG_CHECKPOINT_INTERVAL_DEFAULT
	rolloverInterval := RECORDER_CONFIG_ROLLOVER_INTERVAL_DEFAULT
	midnightRollover := RECORDER_CONFIG_MIDNIGHT_ROLLOVER_DEFAULT
	parseErrorThreshold := RECORDER_CONFIG_PARSE_ERROR_THRESHOLD_DEFAULT
	URL := RECORDER_CONFIG_URL_DEFAULT
	securityKey := RECORDER_CONFIG_SECURITY_KEY_DEFAULT
	compressedRequests := RECORDER_CONFIG_COMPRESSED_REQUESTS_DEFAULT
	requestTimeout := RECORDER_CONFIG_REQUEST_TIMEOUT_DEFAULT
	ignoreTlsVerify := RECORDER_CONFIG_IGNORE_TLS_VERIFY_DEFAULT
	tcpConnTimeout := RECORDER_CONFIG_TCP_CONNECTION_TIMEOUT_DEFAULT
	recordFilesDir := RECORDER_CONFIG_RECORD_FILES_DIR_DEFAULT
	bufSize := RECORDER_CONFIG_RECORD_BUFSIZE_DEFAULT
	compressionLevel := RECORDER_CONFIG_COMPRESSION_LEVEL_DEFAULT

	return &LmcrecConfig{
		ScanInterval:        &scanInterval,
		FlushInterval:       &flushInterval,
		CheckpointInterval:  &checkpointInterval,
		RolloverInterval:    &rolloverInterval,
		MidnightRollover:    &midnightRollover,
		ParseErrorThreshold: &parseErrorThreshold,
		URL:                 &URL,
		SecurityKey:         &securityKey,
		CompressedRequests:  &compressedRequests,
		RequestTimeout:      &requestTimeout,
		IgnoreTlsVerify:     &ignoreTlsVerify,
		TcpConnTimeout:      &tcpConnTimeout,
		RecordFilesDir:      &recordFilesDir,
		BufSize:             &bufSize,
		CompressionLevel:    &compressionLevel,
	}
}

func expandInstEnv(spec, inst string) string {
	return os.ExpandEnv(strings.ReplaceAll(spec, RECORDER_INST_PLACEHOLDER, inst))
}

func applyRecorderConfig(toCfg, fromCfg *LmcrecConfig) *LmcrecConfig {
	if toCfg == nil {
		toCfg = &LmcrecConfig{}
	}
	if fromCfg == nil {
		return toCfg
	}

	toValue := reflect.ValueOf(toCfg).Elem()
	fromValue := reflect.ValueOf(fromCfg).Elem()
	toType := toValue.Type()

	for i := 0; i < toValue.NumField(); i++ {
		toField := toValue.Field(i)
		fromField := fromValue.Field(i)
		fieldType := toType.Field(i)

		// Skip unexported fields
		if !fieldType.IsExported() {
			continue
		}

		// Only handle pointer fields
		if toField.Kind() == reflect.Ptr && fromField.Kind() == reflect.Ptr {
			// If target field is nil and source field is not nil, copy the value
			if toField.IsNil() && !fromField.IsNil() {
				// Create a new value of the same type as the source
				newValuePtr := reflect.New(fromField.Type().Elem())
				newValuePtr.Elem().Set(fromField.Elem())
				toField.Set(newValuePtr)
			}
		}
	}

	return toCfg
}

// Load recorder config from a given file, given its instance.
func loadLmcrecConfig(configFile string, inst string, buf []byte) (*LmcrecConfig, *logrusx.LoggerConfig, error) {
	var (
		config     *LmcrecConfig
		fileConfig *LmcrecFileConfig
	)

	if buf == nil {
		// Normal case, buf is used only for testing:
		lmcrecConfigFromFileCache.lck.Lock()
		defer lmcrecConfigFromFileCache.lck.Unlock()
		fileConfig = lmcrecConfigFromFileCache.fileConfig[configFile]
		if fileConfig == nil {
			f, err := os.Open(configFile)
			if err != nil {
				return nil, nil, err
			}
			defer f.Close()
			buf, err = io.ReadAll(f)
			if err != nil {
				return nil, nil, err
			}
			defer func() { lmcrecConfigFromFileCache.fileConfig[configFile] = fileConfig }()
		}
	}

	if fileConfig == nil {
		fileConfig = &LmcrecFileConfig{
			Default:      DefaultRecorderConfig(),
			LoggerConfig: logrusx.DefaultLoggerConfig(),
		}
		if err := yaml.Unmarshal(buf, fileConfig); err != nil {
			fileConfig = nil
			return nil, nil, err
		}
	}

	// First pass into recorders list, looking for field Inst match:
	for _, cfg := range fileConfig.Recorders {
		if cfg.Inst != nil && inst == *cfg.Inst {
			config = cfg
			break
		}
	}

	// If not found, 2nd pass looking for URL based match:
	if config == nil {
		for _, cfg := range fileConfig.Recorders {
			if cfg.URL != nil && inst == *cfg.URL {
				config = cfg
				break
			}
		}
	}

	if config == nil {
		return nil, nil, fmt.Errorf("no config match for %q", inst)
	}

	config = applyRecorderConfig(config, fileConfig.Default)

	return config, fileConfig.LoggerConfig, nil
}

func LoadLmcrecConfig(configFile string, inst string) (*LmcrecConfig, *logrusx.LoggerConfig, error) {
	return loadLmcrecConfig(configFile, inst, nil)
}
