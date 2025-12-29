// Encoder for LMC recorder
package codec

import (
	"bufio"
	"compress/gzip"
	"compress/zlib"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"path"
	"strings"
	"time"
)

type LmcrecType uint32

const (
	LMCREC_TYPE_UNDEFINED = LmcrecType(iota)
	LMCREC_TYPE_CLASS_INFO
	LMCREC_TYPE_INST_INFO
	LMCREC_TYPE_VAR_INFO
	LMCREC_TYPE_SET_INST_ID
	LMCREC_TYPE_VAR_BOOL_FALSE
	LMCREC_TYPE_VAR_BOOL_TRUE
	LMCREC_TYPE_VAR_UINT_VAL
	LMCREC_TYPE_VAR_SINT_VAL
	LMCREC_TYPE_VAR_ZERO_VAL
	LMCREC_TYPE_VAR_STRING_VAL
	LMCREC_TYPE_VAR_EMPTY_STRING
	LMCREC_TYPE_DELETE_INST_ID
	LMCREC_TYPE_SCAN_TALLY
	LMCREC_TYPE_TIMESTAMP_USEC
	LMCREC_TYPE_DURATION_USEC
	LMCREC_TYPE_EOR
)

const (
	INFO_FILE_STATE_UNINITIALIZED = byte(iota)
	INFO_FILE_STATE_ACTIVE
	INFO_FILE_STATE_CLOSED

	INFO_FILE_NO_OF_VARINT_FIELDS = 9 // (see: Info File in docs/DataModel.md)
	MAX_VARINT_SIZE               = 10
	INFO_BUF_MAX_VARINT_SIZE      = int(INFO_FILE_NO_OF_VARINT_FIELDS * MAX_VARINT_SIZE)
)

const (
	USE_DEFAULT_BUFIO_SIZE    = -1
	DEFAULT_COMPRESSION_LEVEL = gzip.DefaultCompression
	LMCREC_FILE_SUFFIX        = ".lmcrec"
	GZIP_FILE_SUFFIX          = ".gz"
	INFO_FILE_SUFFIX          = ".info"
	INDEX_FILE_SUFFIX         = ".index"
)

type LmcrecEncoder interface {
	ClassInfo(name string, classId uint32) error
	InstInfo(name string, classId, instId, parentInstId uint32) error
	VarInfo(name string, varId, classId, lmcVarType uint32) error
	SetInstId(instId uint32) error
	DeleteInstId(instId uint32) error
	VarValue(varId uint32, value any) error
	ScanTally(scanInByteCount, scanInInstCount, scanInVarCount, scanOutVarCount int) error
	TimestampUsec(ts time.Time) error
	DurationUsec(d time.Duration) error
	EOR() error
	Record(record any) error
}

type LmcrecFileEncoder interface {
	LmcrecEncoder
	GetFileName() string
	Flush() error
	Checkpoint(ts time.Time) error
	Close() error
}

type CodecLmcrecEncoder struct {
	isClosed  bool
	writer    io.Writer
	byteCount int64
	buf       []byte
	// The following are needed only for file recorders:
	startTs         int64
	startTsInit     bool
	mostRecentTs    int64
	totalInNumBytes uint64
	totalInNumInst  uint64
	totalInNumVar   uint64
	totalOutNumVar  uint64
}

type WriteSeekCloser interface {
	io.WriteCloser
	io.Seeker
}

type CodecLmcrecFileEncoder struct {
	CodecLmcrecEncoder
	// The actual file name:
	fileName string
	// The writer passed to the encoder, depending upon compression being
	// enabled or not:
	zWriter        *gzip.Writer
	bufferedWriter *bufio.Writer
	// The number of bytes at the last flush:
	lastFlushByteCount int64
	// The underlying file writer:
	fileWriter io.WriteCloser
	// The info file:
	infoFileWriter WriteSeekCloser
	version        string
	prevFileName   string
	infoBuf        []byte
	infoFileState  byte
	stateOff       int
	// The index file writer, used if checkpoints are enables:
	useCheckpoint   bool
	indexFileWriter io.WriteCloser
}

// Pseudo-record to use in tests for passing args to encoder VarValue methods:
type LmcVarValueArgs struct {
	VarId      uint32
	LmcVarType uint32
	Value      any
}

func (t LmcrecType) String() string {
	typeName := map[LmcrecType]string{
		LMCREC_TYPE_UNDEFINED:      "LMCREC_TYPE_UNDEFINED",
		LMCREC_TYPE_CLASS_INFO:     "LMCREC_TYPE_CLASS_INFO",
		LMCREC_TYPE_INST_INFO:      "LMCREC_TYPE_INST_INFO",
		LMCREC_TYPE_VAR_INFO:       "LMCREC_TYPE_VAR_INFO",
		LMCREC_TYPE_SET_INST_ID:    "LMCREC_TYPE_SET_INST_ID",
		LMCREC_TYPE_VAR_BOOL_FALSE: "LMCREC_TYPE_VAR_BOOL_FALSE",
		LMCREC_TYPE_VAR_BOOL_TRUE:  "LMCREC_TYPE_VAR_BOOL_TRUE",
		LMCREC_TYPE_VAR_UINT_VAL:   "LMCREC_TYPE_VAR_UINT_VAL",
		LMCREC_TYPE_VAR_SINT_VAL:   "LMCREC_TYPE_VAR_SINT_VAL",
		LMCREC_TYPE_VAR_STRING_VAL: "LMCREC_TYPE_VAR_STRING_VAL",
		LMCREC_TYPE_DELETE_INST_ID: "LMCREC_TYPE_DELETE_INST_ID",
		LMCREC_TYPE_TIMESTAMP_USEC: "LMCREC_TYPE_TIMESTAMP_USEC",
		LMCREC_TYPE_DURATION_USEC:  "LMCREC_TYPE_DURATION_USEC",
		LMCREC_TYPE_EOR:            "LMCREC_TYPE_EOR",
	}
	return fmt.Sprintf("%s (%d)", typeName[t], t)
}

func NewCodecLmcrecEncoder(writer io.Writer) *CodecLmcrecEncoder {
	return &CodecLmcrecEncoder{
		writer: writer,
		buf:    make([]byte, 0),
	}
}

// Create a file based encoder.
func NewCodecLmcrecFileEncoder(
	fileName string,
	bufSize, compressionLvl int,
	useCheckpoint bool,
	prevFileName string,
	version string,
) (*CodecLmcrecFileEncoder, error) {
	var (
		bufferedWriter *bufio.Writer
		zWriter        *gzip.Writer
		writer         io.Writer
	)

	compressed := strings.HasSuffix(fileName, GZIP_FILE_SUFFIX) || compressionLvl != zlib.NoCompression
	if compressed && !strings.HasSuffix(fileName, GZIP_FILE_SUFFIX) {
		fileName += GZIP_FILE_SUFFIX
	}

	if err := os.MkdirAll(path.Dir(fileName), os.ModePerm); err != nil {
		return nil, fmt.Errorf("NewCodecLmcrecFileEncoder(): %v", err)
	}

	fileWriter, err := os.Create(fileName)
	if err != nil {
		return nil, fmt.Errorf("NewCodecLmcrecFileEncoder(): %v", err)
	}

	if !compressed {
		if bufSize == USE_DEFAULT_BUFIO_SIZE {
			bufferedWriter = bufio.NewWriter(fileWriter)
		} else if bufSize > 0 {
			bufferedWriter = bufio.NewWriterSize(fileWriter, bufSize)
		}
		if bufferedWriter != nil {
			writer = bufferedWriter
		} else {
			writer = fileWriter
		}
	} else {
		zWriter, err = gzip.NewWriterLevel(fileWriter, compressionLvl)
		if err != nil {
			return nil, fmt.Errorf("NewCodecLmcrecFileEncoder(): %v", err)
		}
		writer = zWriter
	}

	return &CodecLmcrecFileEncoder{
		CodecLmcrecEncoder: CodecLmcrecEncoder{
			writer: writer,
			buf:    make([]byte, 0),
		},
		fileName:       fileName,
		bufferedWriter: bufferedWriter,
		zWriter:        zWriter,
		fileWriter:     fileWriter,
		version:        version,
		prevFileName:   prevFileName,
		infoFileState:  INFO_FILE_STATE_UNINITIALIZED,
		useCheckpoint:  useCheckpoint,
	}, nil
}

func (encoder *CodecLmcrecFileEncoder) GetFileName() string {
	return encoder.fileName
}

func (encoder *CodecLmcrecFileEncoder) flush() error {
	if encoder.isClosed {
		return fmt.Errorf("flush(): encoder is already closed")
	}
	if encoder.lastFlushByteCount == encoder.byteCount {
		return nil
	}

	var err error
	if encoder.bufferedWriter != nil {
		err = encoder.bufferedWriter.Flush()
	} else if encoder.zWriter != nil {
		err = encoder.zWriter.Flush()
	}
	if err != nil {
		return fmt.Errorf("flush(): %v", err)
	}
	encoder.lastFlushByteCount = encoder.byteCount
	return nil
}

func (encoder *CodecLmcrecFileEncoder) updateInfoBuf() (int, int) {
	infoBuf, writeOff := encoder.infoBuf, encoder.stateOff
	if infoBuf == nil {
		versionBuf := []byte(encoder.version)
		prevFileNameBuf := []byte(encoder.prevFileName)
		bufLen, vLen, pfnLen := 0, len(versionBuf), len(prevFileNameBuf)
		infoBuf = make([]byte, INFO_BUF_MAX_VARINT_SIZE+vLen+pfnLen)
		bufLen += binary.PutUvarint(infoBuf[bufLen:], uint64(vLen))
		bufLen += copy(infoBuf[bufLen:], versionBuf)
		bufLen += binary.PutUvarint(infoBuf[bufLen:], uint64(pfnLen))
		bufLen += copy(infoBuf[bufLen:], prevFileNameBuf)
		bufLen += binary.PutVarint(infoBuf[bufLen:], encoder.startTs)
		if encoder.startTsInit && encoder.infoFileState == INFO_FILE_STATE_UNINITIALIZED {
			encoder.infoFileState = INFO_FILE_STATE_ACTIVE
		}
		encoder.infoBuf = infoBuf
		encoder.stateOff = bufLen
		writeOff = 0
	}
	infoBuf[encoder.stateOff] = encoder.infoFileState
	bufLen := encoder.stateOff + 1
	bufLen += binary.PutVarint(infoBuf[bufLen:], encoder.mostRecentTs)
	bufLen += binary.PutUvarint(infoBuf[bufLen:], encoder.totalInNumBytes)
	bufLen += binary.PutUvarint(infoBuf[bufLen:], encoder.totalInNumInst)
	bufLen += binary.PutUvarint(infoBuf[bufLen:], encoder.totalInNumVar)
	bufLen += binary.PutUvarint(infoBuf[bufLen:], encoder.totalOutNumVar)
	return bufLen, writeOff
}

func (encoder *CodecLmcrecFileEncoder) updateInfo() error {
	var err error
	bufLen, writeOff := encoder.updateInfoBuf()
	infoFileWriter := encoder.infoFileWriter
	if infoFileWriter == nil {
		infoFileWriter, err = os.Create(encoder.fileName + INFO_FILE_SUFFIX)
		if err != nil {
			return fmt.Errorf("updateInfo(): %v", err)
		}
		encoder.infoFileWriter = infoFileWriter
	}
	if _, err = infoFileWriter.Seek(int64(writeOff), io.SeekStart); err != nil {
		return fmt.Errorf("updateInfo(): %v", err)
	}
	if _, err = infoFileWriter.Write(encoder.infoBuf[writeOff:bufLen]); err != nil {
		return fmt.Errorf("updateInfo(): %v", err)
	}
	return nil
}

func (encoder *CodecLmcrecFileEncoder) Flush() error {
	if err := encoder.flush(); err != nil {
		return fmt.Errorf("Flush(): %v", err)
	}
	if err := encoder.updateInfo(); err != nil {
		return fmt.Errorf("Flush(): %v", err)
	}
	return nil
}

func (encoder *CodecLmcrecFileEncoder) Checkpoint(ts time.Time) error {
	var err error

	if encoder.isClosed {
		return fmt.Errorf("Checkpoint(): encoder is already closed")
	}
	if !encoder.useCheckpoint {
		return nil
	}

	indexFileWriter := encoder.indexFileWriter
	if indexFileWriter == nil {
		indexFileWriter, err = os.Create(encoder.fileName + INDEX_FILE_SUFFIX)
		if err != nil {
			return fmt.Errorf("Checkpoint(): %v", err)
		}
		encoder.indexFileWriter = indexFileWriter
	}

	// Force flush to ensure that all data till now was successfully written:
	if err := encoder.Flush(); err != nil {
		return fmt.Errorf("Checkpoint(): %v", err)
	}
	// Write the index in one call to ensure atomicity in case of concurrent
	// read; either all fields are there or none is:
	buf := encoder.buf[:0]
	buf = binary.AppendVarint(buf, ts.UnixMicro())
	buf = binary.AppendVarint(buf, encoder.byteCount)
	if _, err := indexFileWriter.Write(buf); err != nil {
		return fmt.Errorf("Checkpoint(): %v", err)
	}
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecFileEncoder) Close() error {
	if encoder.isClosed {
		return nil
	}

	defer encoder.ForceClose()

	if err := encoder.EOR(); err != nil {
		return fmt.Errorf("Close(): %v", err)
	}
	if err := encoder.flush(); err != nil {
		return fmt.Errorf("Close(): %v", err)
	}
	if encoder.startTsInit {
		encoder.infoFileState = INFO_FILE_STATE_CLOSED
		if err := encoder.updateInfo(); err != nil {
			return fmt.Errorf("Close(): %v", err)
		}
	}
	if encoder.zWriter != nil {
		if err := encoder.zWriter.Close(); err != nil {
			return fmt.Errorf("Close(): zWriter.Close(): %v", err)
		}
		encoder.zWriter = nil
	}

	if encoder.fileWriter != nil {
		if err := encoder.fileWriter.Close(); err != nil {
			return fmt.Errorf("Close(): %v", err)
		}
		encoder.fileWriter = nil
	}

	if encoder.infoFileWriter != nil {
		if err := encoder.infoFileWriter.Close(); err != nil {
			return fmt.Errorf("Close(): %v", err)
		}
		encoder.infoFileWriter = nil
	}

	if encoder.indexFileWriter != nil {
		if err := encoder.indexFileWriter.Close(); err != nil {
			return fmt.Errorf("Close(): indexFileWriter.Close(): %v", err)
		}
		encoder.indexFileWriter = nil
	}
	return nil
}

func (encoder *CodecLmcrecFileEncoder) ForceClose() {
	if encoder.zWriter != nil {
		encoder.zWriter.Close()
		encoder.zWriter = nil
	}
	if encoder.fileWriter != nil {
		encoder.fileWriter.Close()
		encoder.fileWriter = nil
	}
	if encoder.infoFileWriter != nil {
		encoder.infoFileWriter.Close()
		encoder.infoFileWriter = nil
	}
	if encoder.indexFileWriter != nil {
		encoder.indexFileWriter.Close()
		encoder.indexFileWriter = nil
	}
	encoder.isClosed = true
}

func (encoder *CodecLmcrecEncoder) ClassInfo(name string, classId uint32) error {
	if encoder.isClosed {
		return fmt.Errorf("ClassInfo(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_CLASS_INFO))
	buf = binary.AppendUvarint(buf, uint64(classId))
	stringBytes := []byte(name)
	buf = binary.AppendUvarint(buf, uint64(len(stringBytes)))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("ClassInfo(): %v", err)
	}
	encoder.byteCount += int64(nn)
	nn, err = encoder.writer.Write(stringBytes)
	if err != nil {
		return fmt.Errorf("ClassInfo(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) InstInfo(name string, classId, instId, parentInstId uint32) error {
	if encoder.isClosed {
		return fmt.Errorf("InstInfo(): encoder is already closed")
	}
	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_INST_INFO))
	buf = binary.AppendUvarint(buf, uint64(classId))
	buf = binary.AppendUvarint(buf, uint64(instId))
	buf = binary.AppendUvarint(buf, uint64(parentInstId))
	stringBytes := []byte(name)
	buf = binary.AppendUvarint(buf, uint64(len(stringBytes)))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("InstInfo(): %v", err)
	}
	encoder.byteCount += int64(nn)
	nn, err = encoder.writer.Write(stringBytes)
	if err != nil {
		return fmt.Errorf("InstInfo(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) VarInfo(name string, varId, classId, lmcVarType uint32) error {
	if encoder.isClosed {
		return fmt.Errorf("VarInfo(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_INFO))
	buf = binary.AppendUvarint(buf, uint64(classId))
	buf = binary.AppendUvarint(buf, uint64(varId))
	buf = binary.AppendUvarint(buf, uint64(lmcVarType))
	stringBytes := []byte(name)
	buf = binary.AppendUvarint(buf, uint64(len(stringBytes)))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("VarInfo(): %v", err)
	}
	encoder.byteCount += int64(nn)
	nn, err = encoder.writer.Write(stringBytes)
	if err != nil {
		return fmt.Errorf("VarInfo(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) SetInstId(instId uint32) error {
	if encoder.isClosed {
		return fmt.Errorf("SetInstId(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_SET_INST_ID))
	buf = binary.AppendUvarint(buf, uint64(instId))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("SetInstId(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) DeleteInstId(instId uint32) error {
	if encoder.isClosed {
		return fmt.Errorf("DeleteInstId(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_DELETE_INST_ID))
	buf = binary.AppendUvarint(buf, uint64(instId))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("DeleteInstId(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) VarValue(varId uint32, value any) error {
	var stringBytes []byte

	if encoder.isClosed {
		return fmt.Errorf("VarValue(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	switch v := value.(type) {
	case uint64:
		if v != 0 {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_UINT_VAL))
			buf = binary.AppendUvarint(buf, uint64(varId))
			buf = binary.AppendUvarint(buf, v)
		} else {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_ZERO_VAL))
			buf = binary.AppendUvarint(buf, uint64(varId))
		}
	case int64:
		if v != 0 {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_SINT_VAL))
			buf = binary.AppendUvarint(buf, uint64(varId))
			buf = binary.AppendVarint(buf, v)
		} else {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_ZERO_VAL))
			buf = binary.AppendUvarint(buf, uint64(varId))
		}
	case string:
		if v != "" {
			stringBytes = []byte(v)
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_STRING_VAL))
			buf = binary.AppendUvarint(buf, uint64(varId))
			buf = binary.AppendUvarint(buf, uint64(len(stringBytes)))
		} else {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_EMPTY_STRING))
			buf = binary.AppendUvarint(buf, uint64(varId))
		}
	case bool:
		if v {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_BOOL_TRUE))
		} else {
			buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_VAR_BOOL_FALSE))
		}
		buf = binary.AppendUvarint(buf, uint64(varId))
	}

	if len(buf) == 0 {
		return fmt.Errorf("VarValue(varId=%d, value=%#v): invalid value type: %T", varId, value, value)
	}

	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("VarValue(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if len(stringBytes) > 0 {
		nn, err = encoder.writer.Write(stringBytes)
		if err != nil {
			return fmt.Errorf("VarValue(): %v", err)
		}
		encoder.byteCount += int64(nn)
	}

	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) ScanTally(scanInNumBytes, scanInInstCount, scanInVarCount, scanOutVarCount int) error {
	if encoder.isClosed {
		return fmt.Errorf("ScanTally(): encoder is already closed")
	}
	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_SCAN_TALLY))
	buf = binary.AppendUvarint(buf, uint64(scanInNumBytes))
	buf = binary.AppendUvarint(buf, uint64(scanInInstCount))
	buf = binary.AppendUvarint(buf, uint64(scanInVarCount))
	buf = binary.AppendUvarint(buf, uint64(scanOutVarCount))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("ScanTally(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	encoder.totalInNumBytes += uint64(scanInNumBytes)
	encoder.totalInNumInst += uint64(scanInInstCount)
	encoder.totalInNumVar += uint64(scanInVarCount)
	encoder.totalOutNumVar += uint64(scanOutVarCount)
	return nil
}

func (encoder *CodecLmcrecEncoder) TimestampUsec(ts time.Time) error {
	if encoder.isClosed {
		return fmt.Errorf("TimestampUsec(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_TIMESTAMP_USEC))
	tsUsec := ts.UnixMicro()
	buf = binary.AppendVarint(buf, tsUsec)
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("TimestampUsec(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	if !encoder.startTsInit {
		encoder.startTs = tsUsec
		encoder.startTsInit = true
	}
	encoder.mostRecentTs = tsUsec
	return nil
}

func (encoder *CodecLmcrecEncoder) DurationUsec(d time.Duration) error {
	if encoder.isClosed {
		return fmt.Errorf("DurationUsec(): encoder is already closed")
	}

	buf := encoder.buf[:0]
	buf = binary.AppendUvarint(buf, uint64(LMCREC_TYPE_DURATION_USEC))
	buf = binary.AppendVarint(buf, d.Microseconds())
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("DurationUsec(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

func (encoder *CodecLmcrecEncoder) EOR() error {
	if encoder.isClosed {
		return fmt.Errorf("EOR(): encoder is already closed")
	}

	buf := binary.AppendUvarint(encoder.buf[:0], uint64(LMCREC_TYPE_EOR))
	nn, err := encoder.writer.Write(buf)
	if err != nil {
		return fmt.Errorf("EOR(): %v", err)
	}
	encoder.byteCount += int64(nn)
	if cap(buf) > cap(encoder.buf) {
		encoder.buf = buf
	}
	return nil
}

// Write a record from a decoder struct:
func (encoder *CodecLmcrecEncoder) Record(record any) error {
	switch rec := record.(type) {
	case *LmcrecClassInfo:
		return encoder.ClassInfo(rec.Name, rec.ClassId)

	case *LmcrecInstInfo:
		return encoder.InstInfo(rec.Name, rec.ClassId, rec.InstId, rec.ParentInstId)

	case *LmcrecVarInfo:
		return encoder.VarInfo(rec.Name, rec.VarId, rec.ClassId, rec.LmcVarType)

	case *LmcrecSetInstId:
		return encoder.SetInstId(rec.InstId)

	case *LmcrecVarVal:
		return encoder.VarValue(rec.VarId, rec.Value)

	case *LmcrecDeleteInstId:
		return encoder.DeleteInstId(rec.InstId)

	case *LmcrecScanTally:
		return encoder.ScanTally(rec.ScanInByteCount, rec.ScanInInstCount, rec.ScanInVarCount, rec.ScanOutVarCount)

	case *LmcrecTimestampUsec:
		return encoder.TimestampUsec(rec.Value)

	case *LmcrecDurationUsec:
		return encoder.DurationUsec(rec.Value)

	case *LmcrecEOR:
		return encoder.EOR()

	default:
		return fmt.Errorf(
			"Record(): unsupported record type: %T", record,
		)
	}
}
