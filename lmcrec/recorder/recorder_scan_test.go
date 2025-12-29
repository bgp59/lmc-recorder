package recorder

import (
	"fmt"
	"path"
	"sync"
	"testing"
	"time"

	logrusx_testutils "github.com/bgp59/logrusx/testutils"
)

const (
	TEST_PARSER_SCAN_RECORD_FILES_DIR         = "/lmcrec/test_parser_scan"
	TEST_PARSER_SCAN_PRIME_RECORD_FILE_SUFFIX = "prev.lmcrec"

	TEST_PARSER_SCAN_PARSE_ERROR  = "recordable parser: parse error"
	TEST_PARSER_SCAN_RECORD_ERROR = "recordable parser: encoder error"
)

const (
	TEST_PARSER_SCAN_SCENARIO_NONE = iota
	TEST_PARSER_SCAN_SCENARIO_HTTP_RESPONSE_ERROR
	TEST_PARSER_SCAN_SCENARIO_HTTP_RESPONSE_NOT_OK_ERROR
	TEST_PARSER_SCAN_SCENARIO_HTTP_NON_JSON_CONTENT_ERROR
	TEST_PARSER_SCAN_SCENARIO_PARSE_ERROR
	TEST_PARSER_SCAN_SCENARIO_RECORD_ERROR
	TEST_PARSER_SCAN_SCENARIO_ALWAYS_FLUSH
	TEST_PARSER_SCAN_SCENARIO_INTERVAL_FLUSH
	TEST_PARSER_SCAN_SCENARIO_NEW_ENCODER_FLUSH
	TEST_PARSER_SCAN_SCENARIO_CHECKPOINT
	TEST_PARSER_SCAN_SCENARIO_INTERVAL_ROLLOVER
	TEST_PARSER_SCAN_SCENARIO_MIDNIGHT_ROLLOVER
	TEST_PARSER_SCAN_SCENARIO_PROCESS_CHANGED
)

type RecorderScanTestCase struct {
	Name        string
	Description string

	Scenario int // TEST_PARSER_SCAN_SCENARIO_...

	HttpContentLength int

	ScanInInstCount int
	ScanInVarCount  int
	OutNumVarCount  int
	CurrIndex       int

	ParseErrorGauge     int
	ParseErrorThreshold int

	StartTs      time.Time
	ScanDuration time.Duration

	// Whether the new encoder call, if invoked, should return an error
	NewEncoderErr bool

	// Expected return value:
	WantScanRetVal bool

	// Expected calls made to the current encoder:
	WantEncoderCalls []string
}

func testRecorderScan(t *testing.T, tc *RecorderScanTestCase) {
	logger := logrusx_testutils.NewTestCollectableLogger(t, RootLogger, nil)
	defer logger.RestoreLog()

	if tc.Description != "" {
		t.Log(tc.Description)
	}

	startTs := tc.StartTs
	time.Local = startTs.Location()
	timeNowMock := &TimeNowMock{
		retVals: []time.Time{startTs, startTs.Add(tc.ScanDuration)},
	}

	newEncoderFunc, expectNilEncoder := NewMockFileEncoder, false
	if tc.NewEncoderErr {
		newEncoderFunc = NewMockFileEncoderErr
		expectNilEncoder = true
	}

	httpClient := &HttpClientDoerMock{
		RespCtl:       HTTP_CLIENT_DOER_MOCK_RESPONSE_OK,
		ContentLength: tc.HttpContentLength,
	}
	recordableParser := &RecordableParserMock{
		ScanInInstCount: tc.ScanInInstCount,
		ScanInVarCount:  tc.ScanInVarCount,
		OutNumVarCount:  tc.OutNumVarCount,
		CurrIndex:       tc.CurrIndex,
	}
	recorder := &Lmcrec{
		logger:                   recorderLogger.WithField("inst", "test"),
		lck:                      &sync.Mutex{},
		httpClient:               httpClient,
		flushInterval:            -1,
		parseErrorGauge:          tc.ParseErrorGauge,
		parseErrorThreshold:      tc.ParseErrorThreshold,
		recordFilesDir:           TEST_PARSER_SCAN_RECORD_FILES_DIR,
		recordableParser:         recordableParser,
		timeNowFunc:              timeNowMock.Now,
		newLmcrecFileEncoderFunc: newEncoderFunc,
	}

	primeEncoder, expectPrimedEncoderClose := true, false
	switch tc.Scenario {
	case TEST_PARSER_SCAN_SCENARIO_HTTP_RESPONSE_ERROR:
		httpClient.RespCtl = HTTP_CLIENT_DOER_MOCK_RESPONSE_ERROR
		expectPrimedEncoderClose, expectNilEncoder = true, true
	case TEST_PARSER_SCAN_SCENARIO_HTTP_RESPONSE_NOT_OK_ERROR:
		httpClient.RespCtl = HTTP_CLIENT_DOER_MOCK_RESPONSE_NOT_OK
		expectPrimedEncoderClose, expectNilEncoder = true, true
	case TEST_PARSER_SCAN_SCENARIO_HTTP_NON_JSON_CONTENT_ERROR:
		httpClient.RespCtl = HTTP_CLIENT_DOER_MOCK_NON_JSON_CONTENT_ERROR
		expectPrimedEncoderClose, expectNilEncoder = true, true
	case TEST_PARSER_SCAN_SCENARIO_PARSE_ERROR:
		recordableParser.ParseErr = fmt.Errorf("%s", TEST_PARSER_SCAN_PARSE_ERROR)
		expectPrimedEncoderClose, expectNilEncoder = true, true
	case TEST_PARSER_SCAN_SCENARIO_RECORD_ERROR:
		recordableParser.RecordParserCacheErr = fmt.Errorf("%s", TEST_PARSER_SCAN_RECORD_ERROR)
		expectPrimedEncoderClose, expectNilEncoder = true, true
	case TEST_PARSER_SCAN_SCENARIO_ALWAYS_FLUSH:
		recorder.flushInterval = 0
	case TEST_PARSER_SCAN_SCENARIO_INTERVAL_FLUSH:
		recorder.flushInterval = 5 * time.Minute
		recorder.lastFlushTs = startTs.Add(-recorder.flushInterval - 1*time.Second)
	case TEST_PARSER_SCAN_SCENARIO_NEW_ENCODER_FLUSH:
		primeEncoder = false
	case TEST_PARSER_SCAN_SCENARIO_CHECKPOINT:
		recorder.checkpointInterval = 1 * time.Hour
		recorder.lastCheckpointTs = startTs.Add(-recorder.checkpointInterval - 1*time.Second)
	case TEST_PARSER_SCAN_SCENARIO_INTERVAL_ROLLOVER:
		recorder.rolloverInterval = 6 * time.Hour
		recorder.lastRolloverTs = startTs.Add(-recorder.rolloverInterval - 1*time.Second)
		expectPrimedEncoderClose = true
	case TEST_PARSER_SCAN_SCENARIO_MIDNIGHT_ROLLOVER:
		y, m, d := startTs.Date()
		recorder.midnightTs = time.Date(y, m, d, 0, 0, 0, 0, startTs.Location())
		recorder.midnightRollover = true
		expectPrimedEncoderClose = true
	case TEST_PARSER_SCAN_SCENARIO_PROCESS_CHANGED:
		recordableParser.ProcessChanged = true
		expectPrimedEncoderClose = true
	}

	var encoderPrimer *MockFileEncoder
	if primeEncoder {
		encoderPrimer = &MockFileEncoder{
			fileName: path.Join(TEST_PARSER_SCAN_RECORD_FILES_DIR, TEST_PARSER_SCAN_PRIME_RECORD_FILE_SUFFIX),
		}
		recorder.encoder = encoderPrimer
		recorder.recordFileNameSuffix = TEST_PARSER_SCAN_PRIME_RECORD_FILE_SUFFIX
	}

	scanRetVal := recorder.Scan()

	if tc.WantScanRetVal != scanRetVal {
		t.Fatalf("scanRetVal: want: %v, got: %v", tc.WantScanRetVal, scanRetVal)
	}

	if expectPrimedEncoderClose {
		if !encoderPrimer.HasCall("Close()") {
			t.Error("encoderPrimer Close() not called")
		}
	}

	encoder := recorder.encoder
	if encoder != nil {
		encoder := encoder.(*MockFileEncoder)
		if buf := encoder.CompareCalls(tc.WantEncoderCalls, nil); buf.Len() > 0 {
			t.Error("encoder calls:", buf)
		}
	} else if !expectNilEncoder {
		t.Error("unexpected nil encoder")
	}
}

func TestRecorderScan(t *testing.T) {
	for _, tc := range RecorderScanTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testRecorderScan(t, tc) },
		)
	}
}
