package recorder

import (
	"bytes"
	"compress/zlib"
	"fmt"
	"io"
	"net/http"
	"regexp"
	"runtime"
	"strconv"
	"strings"
	"time"

	"lmcrec/codec"
)

// Check if the resulted error matches the wanted one. The latter can be:
//
//		nil, false, "": no error expected
//	           true: any error expected
//	       "string": err.Error() must contain string
//	     "/regexp/": err.Error() must match regexp
func checkResultedErr(wantErr any, gotErr error, buf *bytes.Buffer) *bytes.Buffer {
	if buf == nil {
		buf = &bytes.Buffer{}
	}

	if wantErr == nil {
		wantErr = false
	}
	if e, ok := wantErr.(string); ok && e == "" {
		wantErr = false
	}

	switch err := wantErr.(type) {
	case bool:
		if err && gotErr == nil {
			fmt.Fprintf(buf, "expected error, got: %v", gotErr)
		} else if !err && gotErr != nil {
			fmt.Fprintf(buf, "unexpected error, got: %v", gotErr)
		}
	case string:
		if n := len(err); n > 2 && err[0] == '/' && err[n-1] == '/' {
			mustMatch := regexp.MustCompile(err[1 : n-1])
			if gotErr == nil || !mustMatch.Match([]byte(gotErr.Error())) {
				fmt.Fprintf(buf, "unexpected error: must match: %q, got: %v", wantErr, gotErr)
			}
		} else if gotErr == nil || !strings.Contains(gotErr.Error(), err) {
			fmt.Fprintf(buf, "unexpected error: must contain: %q, got: %v", err, gotErr)
		}
	default:
		fmt.Fprintf(buf, "invalid wantErr type: %T", wantErr)
	}
	return buf
}

type MockEncoder struct {
	calls       []string
	retVals     map[string][]error // [call][call#] -> retVal
	retValIndex map[string]int     // per call call#, 0 based, incremented at every call
}

func (m *MockEncoder) recordCall(args ...any) error {
	caller := "NA"
	if pc, _, _, ok := runtime.Caller(1); ok {
		if fn := runtime.FuncForPC(pc); fn != nil {
			caller = fn.Name()
			if i := strings.LastIndex(caller, "."); i > 0 {
				caller = caller[i+1:]
			}
		}
	}
	call := caller + "("
	for i, arg := range args {
		if i > 0 {
			call += ", "
		}
		switch arg := arg.(type) {
		case string:
			call += fmt.Sprintf("%#v", arg)
		default:
			call += fmt.Sprintf("%v", arg)
		}
	}
	call += ")"
	m.calls = append(m.calls, call)

	if m.retVals != nil {
		if m.retValIndex == nil {
			m.retValIndex = make(map[string]int)
		}
		retValIndex := m.retValIndex[call]
		m.retValIndex[call]++
		callRetvals := m.retVals[call]
		if callRetvals != nil && retValIndex < len(callRetvals) {
			return callRetvals[retValIndex]
		}
	}
	return nil
}

func (m *MockEncoder) ClassInfo(name string, classId uint32) error {
	return m.recordCall(name, classId)
}

func (m *MockEncoder) InstInfo(name string, classId, instId, parentInstId uint32) error {
	return m.recordCall(name, classId, instId, parentInstId)
}

func (m *MockEncoder) VarInfo(name string, varId, classId, lmcVarType uint32) error {
	return m.recordCall(name, varId, classId, lmcVarType)
}

func (m *MockEncoder) SetInstId(instId uint32) error {
	return m.recordCall(instId)
}

func (m *MockEncoder) DeleteInstId(instId uint32) error {
	return m.recordCall(instId)
}

func (m *MockEncoder) VarValue(varId uint32, value any) error {
	return m.recordCall(varId, value)
}

func (m *MockEncoder) ScanTally(scanInNumBytes, scanInInstCount, scanInVarCount, scanOutVarCount int) error {
	return m.recordCall(scanInNumBytes, scanInInstCount, scanInVarCount, scanOutVarCount)
}

func (m *MockEncoder) TimestampUsec(ts time.Time) error {
	return m.recordCall(ts)
}

func (m *MockEncoder) DurationUsec(d time.Duration) error {
	return m.recordCall(d)
}

func (m *MockEncoder) EOR() error {
	return m.recordCall()
}

func (m *MockEncoder) Record(record any) error {
	return m.recordCall(record)
}

func (m *MockEncoder) HasCall(call string) bool {
	for _, gotCall := range m.calls {
		if gotCall == call {
			return true
		}
	}
	return false
}

func (m *MockEncoder) CompareCalls(wantCalls []string, buf *bytes.Buffer) *bytes.Buffer {
	if buf == nil {
		buf = &bytes.Buffer{}
	}

	if want, got := len(wantCalls), len(m.calls); want != got {
		fmt.Fprintf(buf, "\nnum calls mismatch: want: %d, got: %d", want, got)
		m.CompareCallsAnyOrder(wantCalls, buf)
	} else {
		for i, want := range wantCalls {
			if got := m.calls[i]; want != got {
				fmt.Fprintf(buf, "\ncall[%d] mismatch:\n\twant: %s\n\t got: %s", i, want, got)
			}
		}
	}
	return buf
}

func (m *MockEncoder) CompareCallsAnyOrder(wantCalls []string, buf *bytes.Buffer) *bytes.Buffer {
	if buf == nil {
		buf = &bytes.Buffer{}
	}

	wantCallsCnt := make(map[string]int)
	for _, call := range wantCalls {
		wantCallsCnt[call] += 1
	}

	gotCallsCnt := make(map[string]int)
	for _, call := range m.calls {
		gotCallsCnt[call] += 1
	}

	header := "Missing calls"
	for call, want := range wantCallsCnt {
		if got := gotCallsCnt[call]; want > got {
			if header != "" {
				fmt.Fprintf(buf, "\n%s", header)
				header = ""
			}
			fmt.Fprintf(buf, "\n\t%s count: want: %d, got: %d", call, want, got)
		}
	}

	header = "Unexpected calls"
	for call, got := range gotCallsCnt {
		if want := wantCallsCnt[call]; got > want {
			if header != "" {
				fmt.Fprintf(buf, "\n%s", header)
				header = ""
			}
			fmt.Fprintf(buf, "\n\t%s count: want: %d, got: %d", call, want, got)
		}
	}
	return buf
}

type MockFileEncoder struct {
	MockEncoder
	fileName       string
	bufSize        int
	compressionLvl int
	useCheckpoint  bool
	version        string
	prevFileName   string
}

func (m *MockFileEncoder) GetFileName() string {
	return m.fileName
}

func (m *MockFileEncoder) Flush() error {
	return m.recordCall()
}

func (m *MockFileEncoder) Checkpoint(ts time.Time) error {
	return m.recordCall(ts)
}

func (m *MockFileEncoder) Close() error {
	return m.recordCall()
}

func NewMockFileEncoder(fileName string, bufSize, compressionLvl int, useCheckpoint bool, prevFileName string, version string) (codec.LmcrecFileEncoder, error) {
	encoder := &MockFileEncoder{
		fileName:       fileName,
		bufSize:        bufSize,
		compressionLvl: compressionLvl,
		useCheckpoint:  useCheckpoint,
		version:        version,
		prevFileName:   prevFileName,
	}
	return encoder, nil
}

func NewMockFileEncoderErr(fileName string, bufSize, compressionLvl int, useCheckpoint bool, prevFileName string, version string) (codec.LmcrecFileEncoder, error) {
	return nil, fmt.Errorf("file encoder error")
}

const (
	HTTP_CLIENT_DOER_MOCK_RESPONSE_OK = iota
	HTTP_CLIENT_DOER_MOCK_RESPONSE_ERROR
	HTTP_CLIENT_DOER_MOCK_RESPONSE_NOT_OK
	HTTP_CLIENT_DOER_MOCK_NON_JSON_CONTENT_ERROR
	HTTP_CLIENT_DOER_MOCK_COMPRESSED_BODY
	HTTP_CLIENT_DOER_MOCK_COMPRESSION_ERROR
)

type HttpClientDoerMock struct {
	RespBody      string
	RespCtl       int
	ContentLength int
}

func (m *HttpClientDoerMock) Do(req *http.Request) (*http.Response, error) {
	if m.RespCtl == HTTP_CLIENT_DOER_MOCK_RESPONSE_ERROR {
		return nil, fmt.Errorf("HTTP error")
	}

	header := http.Header{}
	body := []byte(m.RespBody)

	status, jsonContent, contentLength := http.StatusOK, true, m.ContentLength

	switch m.RespCtl {
	case HTTP_CLIENT_DOER_MOCK_RESPONSE_NOT_OK:
		status = http.StatusNotFound
	case HTTP_CLIENT_DOER_MOCK_NON_JSON_CONTENT_ERROR:
		jsonContent = false
	case HTTP_CLIENT_DOER_MOCK_COMPRESSED_BODY:
		header.Add("Content-Encoding", "deflate")
		compressedBody := &bytes.Buffer{}
		zWriter := zlib.NewWriter(compressedBody)
		zWriter.Write(body)
		zWriter.Close()
		body = compressedBody.Bytes()
	case HTTP_CLIENT_DOER_MOCK_COMPRESSION_ERROR:
		header.Add("Content-Encoding", "deflate")
		body = make([]byte, 16) // should fail zlib header
	}
	if contentLength == 0 {
		contentLength = len(body)
	}
	header.Add("Content-Length", strconv.Itoa(contentLength))
	if jsonContent {
		header.Add("Content-Type", "application/json; charset=UTF-8")
	}
	resp := &http.Response{
		StatusCode: status,
		Header:     header,
		Body:       io.NopCloser(bytes.NewBuffer(body)),
	}
	return resp, nil
}

type TimeNowMock struct {
	retVals []time.Time
	lastVal time.Time
	indx    int
}

func (m *TimeNowMock) Now() time.Time {
	if m.indx < len(m.retVals) {
		m.lastVal = m.retVals[m.indx]
		m.indx++
	}
	return m.lastVal
}

type RecordableParserMock struct {
	ProcessChanged       bool
	ScanInInstCount      int
	ScanInVarCount       int
	OutNumVarCount       int
	ParseErr             error
	RecordParserCacheErr error
	CurrIndex            int
}

func (m *RecordableParserMock) Parse(r io.Reader, noNewEvents bool) (bool, int, int, error) {
	return m.ProcessChanged, m.ScanInInstCount, m.ScanInVarCount, m.ParseErr
}

func (m *RecordableParserMock) Record(encoder codec.LmcrecEncoder, full bool) (int, error) {
	return m.OutNumVarCount, m.RecordParserCacheErr
}

func (m *RecordableParserMock) GetCurrIndex() int { return m.CurrIndex }

func (m *RecordableParserMock) SetCurrIndex(currIndex int) { m.CurrIndex = currIndex }

func (m *RecordableParserMock) FlipCurrIndex() { m.CurrIndex = 1 - m.CurrIndex }
