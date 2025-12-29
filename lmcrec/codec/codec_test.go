// Unit tests for encoder / decoder

package codec

import (
	"bytes"
	"compress/gzip"
	"fmt"
	"os"
	"path"
	"reflect"
	"regexp"
	"strings"
	"testing"
	"time"

	"github.com/go-test/deep"
)

const (
	CODEC_TEST_FILES_DIR = "../../local/testdata/lmcrec/codec" // local/ being git ignored

	DECODER_TEST_SCAN_INTERVAL = 5 * time.Second
)

type EncoderDecoderTestCase struct {
	Name        string
	Description string
	WantRecords []any
}

type MockWriter struct {
	callCount        int
	errorAtCallCount int // <= 0, no error
	err              error
}

func (m *MockWriter) Write(b []byte) (int, error) {
	m.callCount += 1
	if m.errorAtCallCount > 0 && m.callCount >= m.errorAtCallCount {
		return 0, m.err
	}
	return len(b), nil
}

type EncoderErrTestCase struct {
	Name        string
	Description string
	// *Lmcrec... from decoder:
	Record any
	// WriteErrAtCallCount
	//  < 0: The error is due to other factors, like incompatible args.
	//       It should contain the string in WantErr
	//  == 0: The error is is due to already closed condition
	//   > 0: The error will occur at #WriteErrAtCallCount call
	WriteErrAtCallCount int
	// The error message should contain the following string, used only when
	// WriteErrAtCallCount < 0.
	WantErr string
}

type EncoderInfoTestData struct {
	Timestamp       time.Time
	ScanInByteCount int
	ScanInInstCount int
	ScanInVarCount  int
	ScanOutVarCount int
	DoFlush         bool
}

type EncoderInfoTestCase struct {
	Name         string
	Description  string
	Version      string
	PrevFileName string
	TestData     []EncoderInfoTestData
}

type TestIndexData struct {
	TargetOffset int64
	Timestamp    time.Time
}

type EncoderIndexTestCase struct {
	Name        string
	Description string
	// IndexData should be sorted in ascending order by TargetOffset; each
	// offset should be at least +16 from the previous one:
	IndexData []*TestIndexData
}

func makeTestLmcrecFileName(testName string, fileDir string) string {
	re := regexp.MustCompile(`[^/a-zA-Z0-9._-]`)
	return path.Join(fileDir, re.ReplaceAllString(testName, "_")+LMCREC_FILE_SUFFIX)
}

func testEncoderDecoder(t *testing.T, tc *EncoderDecoderTestCase, fileDir string, compress bool) {
	var (
		buf      *bytes.Buffer
		decoder  LmcrecDecoder
		encoder  LmcrecEncoder
		err      error
		fileName string
	)

	if tc.Description != "" {
		t.Log(tc.Description)
	}

	if fileDir == "" {
		buf = &bytes.Buffer{}
		encoder = NewCodecLmcrecEncoder(buf)
	} else {
		fileName = makeTestLmcrecFileName(t.Name(), fileDir)
		bufSize, compressionLvl := USE_DEFAULT_BUFIO_SIZE, gzip.NoCompression
		if compress {
			compressionLvl = DEFAULT_COMPRESSION_LEVEL
		}
		dirPath := path.Dir(fileName)
		if err = os.MkdirAll(dirPath, os.ModePerm); err != nil {
			t.Fatal(err)
		}
		if encoder, err = NewCodecLmcrecFileEncoder(fileName, bufSize, compressionLvl, false, "", ""); err != nil {
			t.Fatal(err)
		}
		fileName = encoder.(*CodecLmcrecFileEncoder).GetFileName()
		t.Logf("using file: %s", fileName)
	}

	for _, record := range tc.WantRecords {
		if err := encoder.Record(record); err != nil {
			t.Fatalf("unexpected encoder error: %v", err)
		}
	}

	if fileName == "" {
		if want, got := int64(buf.Len()), encoder.(*CodecLmcrecEncoder).byteCount; want != got {
			t.Errorf("byteCount: want: %d, got: %d", want, got)
		}
		decoder = NewCodecLmcrecDecoder(buf)
	} else {
		if err = encoder.(*CodecLmcrecFileEncoder).Close(); err != nil {
			t.Fatal(err)
		}
		if decoder, err = NewCodecLmcrecFileDecoder(fileName, USE_DEFAULT_BUFIO_SIZE); err != nil {
			t.Fatal(err)
		}
	}

	for _, wantRecord := range tc.WantRecords {
		if gotRecord, err := decoder.NextRecord(); err != nil {
			t.Fatalf("unexpected decoder error: %v", err)
		} else if !reflect.DeepEqual(wantRecord, gotRecord) {
			t.Errorf(
				"unexpected record: want: %#v, got: %#v",
				wantRecord, gotRecord,
			)
		}
	}

	if fileName != "" {
		wantRecord := any(&LmcrecEOR{})
		if gotRecord, err := decoder.NextRecord(); err != nil {
			t.Fatalf("unexpected decoder error: %v", err)
		} else if !reflect.DeepEqual(wantRecord, gotRecord) {
			t.Errorf(
				"unexpected record: want: %#v, got: %#v",
				wantRecord, gotRecord,
			)
		}
		if err = decoder.(*CodecLmcrecFileDecoder).Close(); err != nil {
			t.Fatal(err)
		}
	}
}

func testEncoderErr(t *testing.T, tc *EncoderErrTestCase) {
	if tc.Description != "" {
		t.Log(tc.Description)
	}

	mockWriter := &MockWriter{
		errorAtCallCount: tc.WriteErrAtCallCount,
	}
	encoder := NewCodecLmcrecEncoder(mockWriter)

	wantErr := ""
	if tc.WriteErrAtCallCount < 0 {
		wantErr = tc.WantErr
	} else if tc.WriteErrAtCallCount == 0 {
		wantErr = "already closed"
		encoder.isClosed = true
	} else {
		mockWriter.err = fmt.Errorf("error at call# %d", tc.WriteErrAtCallCount)
		wantErr = mockWriter.err.Error()
	}

	err := encoder.Record(tc.Record)
	if err == nil || !strings.Contains(err.Error(), wantErr) {
		t.Errorf("unexpected error: want: %q, got: %v", wantErr, err)
	}
}

func testEncoderInfo(t *testing.T, tc *EncoderInfoTestCase, fileDir string) {
	if fileDir == "" {
		t.Error("Empty fileDir")
	}

	if tc.Description != "" {
		t.Log(tc.Description)
	}
	fileName := makeTestLmcrecFileName(t.Name(), fileDir)
	t.Logf("using file: %s", fileName)
	encoder, err := NewCodecLmcrecFileEncoder(fileName, USE_DEFAULT_BUFIO_SIZE, 0, false, tc.PrevFileName, tc.Version)
	if err != nil {
		t.Fatal(err)
	}

	infoFileName := encoder.GetFileName() + INFO_FILE_SUFFIX

	wantLmcrecInfo := &LmcrecInfo{Version: tc.Version, PrevFileName: tc.PrevFileName, State: INFO_FILE_STATE_ACTIVE}
	for i, td := range tc.TestData {
		wantLmcrecInfo.MostRecentTs = td.Timestamp
		if i == 0 {
			wantLmcrecInfo.StartTs = wantLmcrecInfo.MostRecentTs
		}
		if err = encoder.TimestampUsec(td.Timestamp); err != nil {
			t.Fatal(err)
		}
		if err = encoder.ScanTally(td.ScanInByteCount, td.ScanInInstCount, td.ScanInVarCount, td.ScanOutVarCount); err != nil {
			t.Fatal(err)
		}
		wantLmcrecInfo.TotalInNumBytes += uint64(td.ScanInByteCount)
		wantLmcrecInfo.TotalInNumInst += uint64(td.ScanInInstCount)
		wantLmcrecInfo.TotalInNumVar += uint64(td.ScanInVarCount)
		wantLmcrecInfo.TotalOutNumVar += uint64(td.ScanOutVarCount)
		if td.DoFlush {
			if err = encoder.Flush(); err != nil {
				t.Fatal(err)
			}
			gotLmcrecInfo, err := LoadLmcrecInfoFile(infoFileName)
			if err != nil {
				t.Fatal(err)
			}
			if diff := deep.Equal(wantLmcrecInfo, gotLmcrecInfo); len(diff) > 0 {
				t.Fatal("\n\t" + strings.Join(diff, "\n\t"))
			}
		}
	}
	if err = encoder.Close(); err != nil {
		t.Fatal(err)
	}
	wantLmcrecInfo.State = INFO_FILE_STATE_CLOSED
	gotLmcrecInfo, err := LoadLmcrecInfoFile(infoFileName)
	if err != nil {
		t.Fatal(err)
	}
	if diff := deep.Equal(wantLmcrecInfo, gotLmcrecInfo); len(diff) > 0 {
		t.Fatal("\n\t" + strings.Join(diff, "\n\t"))
	}
}

func testEncoderIndexFile(t *testing.T, tc *EncoderIndexTestCase, fileDir string, compress bool) {
	if fileDir == "" {
		t.Error("Empty fileDir")
	}
	if tc.Description != "" {
		t.Log(tc.Description)
	}
	fileName := makeTestLmcrecFileName(t.Name(), fileDir)
	bufSize, compressionLvl := USE_DEFAULT_BUFIO_SIZE, gzip.NoCompression
	if compress {
		compressionLvl = DEFAULT_COMPRESSION_LEVEL
	}
	dirPath := path.Dir(fileName)
	if err := os.MkdirAll(dirPath, os.ModePerm); err != nil {
		t.Fatal(err)
	}
	encoder, err := NewCodecLmcrecFileEncoder(fileName, bufSize, compressionLvl, true, "", "")
	if err != nil {
		t.Fatal(err)
	}
	fileName = encoder.GetFileName()
	t.Logf("using file: %s", fileName)
	indexFileName := fileName + INDEX_FILE_SUFFIX
	fillerSz := int64(64)
	filler := ""
	for i := range fillerSz {
		filler += fmt.Sprintf("%d", i%10)
	}
	for _, indexData := range tc.IndexData {
		varId := uint32(0)
		needSz := indexData.TargetOffset - encoder.byteCount
		for needSz > 0 {
			//fmt.Println("> ", indexData.TargetOffset, encoder.byteCount, needSz)
			switch needSz {
			case 1:
				err = encoder.EOR()
			case 2:
				err = encoder.VarValue(varId, true)
			default:
				err = encoder.VarValue(varId, filler[:min(fillerSz, needSz-3)])
			}
			needSz = indexData.TargetOffset - encoder.byteCount
			varId = (varId + 1) & 0xf
			//fmt.Println("< ", indexData.TargetOffset, encoder.byteCount, needSz)
		}
		if needSz != 0 {
			t.Fatalf(
				"final needSz for targetOffset: %d: want: %d, got: %d",
				indexData.TargetOffset, 0, needSz,
			)
		}
		if err == nil {
			err = encoder.Checkpoint(indexData.Timestamp)
		}
		if err == nil {
			err = encoder.TimestampUsec(indexData.Timestamp)
		}
		if err != nil {
			t.Fatal(err)
		}
	}
	if err = encoder.Close(); err != nil {
		t.Fatal(err)
	}

	readSz := int64(1024)
	buf := make([]byte, readSz)
	indexDecoder, err := NewCodecLmcrecCheckpointFileDecoder(indexFileName)
	if err != nil {
		t.Fatal(err)
	}
	for _, indexData := range tc.IndexData {
		checkpoint, err := indexDecoder.NextCheckpoint()
		if err != nil {
			t.Fatalf("%v: NextCheckpoint(): %v", indexData, err)
		}
		if want, got := indexData.Timestamp, checkpoint.Timestamp.In(indexData.Timestamp.Location()); want != got {
			t.Fatalf("%v: NextCheckpoint(): want: %s, got: %s", indexData, want, got)
		}
		if want, got := indexData.TargetOffset, checkpoint.Offset; want != got {
			t.Fatalf("%v: NextCheckpoint(): want: %d, got: %d", indexData, want, got)
		}

		decoder, err := NewCodecLmcrecFileDecoder(fileName, USE_DEFAULT_BUFIO_SIZE)
		if err != nil {
			t.Fatal(err)
		}
		n := indexData.TargetOffset
		for n > 0 {
			toRead := min(n, readSz)
			if nn, err := decoder.reader.Read(buf[0:toRead]); err != nil {
				t.Fatalf("%v: %v", indexData, err)
			} else {
				n -= int64(nn)
			}
		}
		if record, err := decoder.NextRecord(); err != nil {
			t.Fatalf("%v: NextRecord(): %v", indexData, err)
		} else if ts, ok := record.(*LmcrecTimestampUsec); !ok {
			t.Fatalf("%v: NextRecord(): *LmcrecTimestampUsec, got: %T", indexData, record)
		} else if want, got := indexData.Timestamp, ts.Value; want != got {
			t.Fatalf("%v: NextRecord(): want: %s, got: %s", indexData, want, got)
		}
	}
}
func TestEncoderDecoderNoErr(t *testing.T) {
	for _, tc := range EncoderDecoderNoErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testEncoderDecoder(t, tc, "", false) },
		)
	}
}

func TestEncoderDecoderFileNoErr(t *testing.T) {
	for _, tc := range EncoderDecoderNoErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testEncoderDecoder(t, tc, CODEC_TEST_FILES_DIR, false) },
		)
	}
}

func TestEncoderDecoderGzipFileNoErr(t *testing.T) {
	for _, tc := range EncoderDecoderNoErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testEncoderDecoder(t, tc, CODEC_TEST_FILES_DIR, true) },
		)
	}
}

func TestEncoderArgsErr(t *testing.T) {
	for _, tc := range EncoderArgsErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testEncoderErr(t, tc) },
		)
	}
}

func TestEncoderClosedErr(t *testing.T) {
	for _, tc := range EncoderClosedErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testEncoderErr(t, tc) },
		)
	}
}

func TestEncoderWriteErr(t *testing.T) {
	for _, tc := range EncoderWriteErrTestCases {
		numWrites := tc.WriteErrAtCallCount
		for k := 1; k <= numWrites; k++ {
			tc.WriteErrAtCallCount = k
			t.Run(
				fmt.Sprintf("%s/err_at=%d", tc.Name, k),
				func(t *testing.T) { testEncoderErr(t, tc) },
			)
		}
	}
}

func TestEncoderInfoFileNoErr(t *testing.T) {
	for _, tc := range EncoderInfoFileNoErrTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testEncoderInfo(t, tc, CODEC_TEST_FILES_DIR) },
		)
	}
}

func TestEncoderIndexFileNoErr(t *testing.T) {
	for _, tc := range EncoderIndexFileNoErrTestCases {
		for _, compress := range []bool{false, true} {
			t.Run(
				fmt.Sprintf("%s/compress=%v", tc.Name, compress),
				func(t *testing.T) { testEncoderIndexFile(t, tc, CODEC_TEST_FILES_DIR, compress) },
			)
		}
	}
}
