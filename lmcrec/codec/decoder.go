// Decoder for LMC recorder
package codec

import (
	"bufio"
	"compress/gzip"
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"strings"

	"time"
)

type LmcrecDecoder interface {
	NextRecord() (nextRecord any, err error)
}

type LmcrecClassInfo struct {
	ClassId uint32
	Name    string
}

type LmcrecInstInfo struct {
	ClassId      uint32
	InstId       uint32
	ParentInstId uint32
	Name         string
}

type LmcrecVarInfo struct {
	ClassId    uint32
	VarId      uint32
	LmcVarType uint32
	Name       string
}

type LmcrecSetInstId struct {
	InstId uint32
}

type LmcrecVarVal struct {
	VarId uint32
	Value any
}

type LmcrecDeleteInstId struct {
	InstId uint32
}

type LmcrecScanTally struct {
	ScanInByteCount int
	ScanInInstCount int
	ScanInVarCount  int
	ScanOutVarCount int
}

type LmcrecTimestampUsec struct {
	Value time.Time
}

type LmcrecDurationUsec struct {
	Value time.Duration
}

type LmcrecEOR struct {
}

type ReadByteReader interface {
	ReadByte() (byte, error)
	Read([]byte) (int, error)
}

type CodecLmcrecDecoder struct {
	reader ReadByteReader

	// Remember most recent classId and restId, as set by the relevant record
	// type:
	mostRecentClassId uint32
	mostRecentInstId  uint32

	// Buffers for decoding:
	lmcrecClassInfo      *LmcrecClassInfo
	lmcrecInstInfo       *LmcrecInstInfo
	lmcrecVarInfo        *LmcrecVarInfo
	lmcrecSetInstId      *LmcrecSetInstId
	lmcrecVarVal         *LmcrecVarVal
	lmcrecDeleteInstId   *LmcrecDeleteInstId
	lmcrecScanTally      *LmcrecScanTally
	lmcScanTallyFieldPtr []*int
	lmcrecTimestampUsec  *LmcrecTimestampUsec
	lmcrecDurationUsec   *LmcrecDurationUsec
	lmcrecEOR            *LmcrecEOR
	stringBytes          []byte
}

type CodecLmcrecFileDecoder struct {
	CodecLmcrecDecoder
	zReader    *gzip.Reader
	fileReader *os.File
}

func NewCodecLmcrecDecoder(reader ReadByteReader) *CodecLmcrecDecoder {
	decoder := &CodecLmcrecDecoder{
		reader:              reader,
		lmcrecClassInfo:     &LmcrecClassInfo{},
		lmcrecInstInfo:      &LmcrecInstInfo{},
		lmcrecVarInfo:       &LmcrecVarInfo{},
		lmcrecSetInstId:     &LmcrecSetInstId{},
		lmcrecVarVal:        &LmcrecVarVal{},
		lmcrecDeleteInstId:  &LmcrecDeleteInstId{},
		lmcrecScanTally:     &LmcrecScanTally{},
		lmcrecTimestampUsec: &LmcrecTimestampUsec{},
		lmcrecDurationUsec:  &LmcrecDurationUsec{},
		lmcrecEOR:           &LmcrecEOR{},
		stringBytes:         make([]byte, 0),
	}
	decoder.lmcScanTallyFieldPtr = []*int{
		&decoder.lmcrecScanTally.ScanInByteCount,
		&decoder.lmcrecScanTally.ScanInInstCount,
		&decoder.lmcrecScanTally.ScanInVarCount,
		&decoder.lmcrecScanTally.ScanOutVarCount,
	}
	return decoder
}

func NewCodecLmcrecFileDecoder(fileName string, bufSize int) (*CodecLmcrecFileDecoder, error) {
	fileReader, err := os.Open(fileName)
	if err != nil {
		return nil, fmt.Errorf("NewCodecLmcrecFileDecoder(): %v", err)
	}

	var (
		zReader     *gzip.Reader
		ioReader    io.Reader
		bufioReader *bufio.Reader
	)

	if strings.HasSuffix(fileName, GZIP_FILE_SUFFIX) {
		zReader, err = gzip.NewReader(fileReader)
		if err != nil {
			return nil, fmt.Errorf("NewCodecLmcrecFileDecoder(): %v", err)
		}
		ioReader = zReader
	} else {
		ioReader = fileReader
	}

	if bufSize <= 0 {
		bufioReader = bufio.NewReader(ioReader)
	} else {
		bufioReader = bufio.NewReaderSize(ioReader, bufSize)
	}

	return &CodecLmcrecFileDecoder{
		CodecLmcrecDecoder: *NewCodecLmcrecDecoder(bufioReader),
		zReader:            zReader,
		fileReader:         fileReader,
	}, nil
}

func (decoder *CodecLmcrecFileDecoder) Close() error {
	if decoder.zReader != nil {
		if err := decoder.zReader.Close(); err != nil &&
			err != io.EOF && err != io.ErrUnexpectedEOF {
			return fmt.Errorf("Close(): zReader.Close(): %v", err)
		}
	}
	if err := decoder.fileReader.Close(); err != nil {
		return fmt.Errorf("Close(): %v", err)
	}
	return nil
}

func (decoder *CodecLmcrecDecoder) readString() (string, error) {
	r := decoder.reader

	uvarint, err := binary.ReadUvarint(r)
	if err != nil {
		return "", err
	}
	stringBytesSz := int(uvarint)

	stringBytes := decoder.stringBytes
	if cap(stringBytes) < stringBytesSz {
		stringBytes = make([]byte, stringBytesSz)
		decoder.stringBytes = stringBytes
	} else {
		stringBytes = stringBytes[:stringBytesSz]
	}
	for pos, n := 0, 0; pos < stringBytesSz; pos += n {
		if n, err = r.Read(stringBytes[pos:stringBytesSz]); err != nil {
			return "", err
		}
	}
	return string(stringBytes), nil
}

func (decoder *CodecLmcrecDecoder) NextRecord() (nextRecord any, err error) {
	defer func() {
		if err != nil {
			err = fmt.Errorf("NextRecord(): %v", err)
		}
	}()

	var (
		uvarint uint64
		varint  int64
	)

	r := decoder.reader
	if uvarint, err = binary.ReadUvarint(r); err != nil {
		return
	}
	recType := LmcrecType(uvarint)

	switch recType {
	case LMCREC_TYPE_CLASS_INFO:
		record := decoder.lmcrecClassInfo
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.ClassId = uint32(uvarint)
		if record.Name, err = decoder.readString(); err == nil {
			decoder.mostRecentClassId = record.ClassId
			nextRecord = record
		}

	case LMCREC_TYPE_INST_INFO:
		record := decoder.lmcrecInstInfo
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.ClassId = uint32(uvarint)
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.InstId = uint32(uvarint)
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.ParentInstId = uint32(uvarint)
		if record.Name, err = decoder.readString(); err == nil {
			decoder.mostRecentInstId = record.InstId
			nextRecord = record
		}

	case LMCREC_TYPE_VAR_INFO:
		record := decoder.lmcrecVarInfo
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.ClassId = uint32(uvarint)
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.VarId = uint32(uvarint)
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.LmcVarType = uint32(uvarint)
		if record.Name, err = decoder.readString(); err == nil {
			nextRecord = record
		}

	case LMCREC_TYPE_SET_INST_ID:
		record := decoder.lmcrecSetInstId
		if uvarint, err = binary.ReadUvarint(r); err == nil {
			record.InstId = uint32(uvarint)
			decoder.mostRecentInstId = record.InstId
			nextRecord = record
		}

	case LMCREC_TYPE_VAR_BOOL_FALSE,
		LMCREC_TYPE_VAR_BOOL_TRUE:
		record := decoder.lmcrecVarVal
		if uvarint, err = binary.ReadUvarint(r); err == nil {
			record.VarId = uint32(uvarint)
			record.Value = recType == LMCREC_TYPE_VAR_BOOL_TRUE
			nextRecord = record
		}

	case LMCREC_TYPE_VAR_UINT_VAL,
		LMCREC_TYPE_VAR_ZERO_VAL:
		record := decoder.lmcrecVarVal
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.VarId = uint32(uvarint)
		if recType == LMCREC_TYPE_VAR_ZERO_VAL {
			record.Value = uint64(0)
			nextRecord = record
		} else if record.Value, err = binary.ReadUvarint(r); err == nil {
			nextRecord = record
		}

	case LMCREC_TYPE_VAR_SINT_VAL:
		record := decoder.lmcrecVarVal
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.VarId = uint32(uvarint)
		if record.Value, err = binary.ReadVarint(r); err == nil {
			nextRecord = record
		}

	case LMCREC_TYPE_VAR_STRING_VAL,
		LMCREC_TYPE_VAR_EMPTY_STRING:
		record := decoder.lmcrecVarVal
		if uvarint, err = binary.ReadUvarint(r); err != nil {
			return
		}
		record.VarId = uint32(uvarint)
		if recType == LMCREC_TYPE_VAR_EMPTY_STRING {
			record.Value = ""
			nextRecord = record
		} else if record.Value, err = decoder.readString(); err == nil {
			nextRecord = record
		}

	case LMCREC_TYPE_DELETE_INST_ID:
		record := decoder.lmcrecDeleteInstId
		if uvarint, err = binary.ReadUvarint(r); err == nil {
			record.InstId = uint32(uvarint)
			nextRecord = record
		}

	case LMCREC_TYPE_SCAN_TALLY:
		record := decoder.lmcrecScanTally
		for _, intptr := range decoder.lmcScanTallyFieldPtr {
			if uvarint, err = binary.ReadUvarint(r); err != nil {
				break
			}
			*intptr = int(uvarint)
		}
		nextRecord = record

	case LMCREC_TYPE_TIMESTAMP_USEC:
		record := decoder.lmcrecTimestampUsec
		if varint, err = binary.ReadVarint(r); err == nil {
			record.Value = time.UnixMicro(varint).UTC()
			nextRecord = record
		}

	case LMCREC_TYPE_DURATION_USEC:
		record := decoder.lmcrecDurationUsec
		if varint, err = binary.ReadVarint(r); err == nil {
			record.Value = time.Duration(varint) * time.Microsecond
			nextRecord = record
		}

	case LMCREC_TYPE_EOR:
		nextRecord = decoder.lmcrecEOR

	default:
		err = fmt.Errorf("unknown record type: %d", recType)
	}

	return
}

type LmcrecInfo struct {
	Version         string
	PrevFileName    string
	State           byte
	StartTs         time.Time
	MostRecentTs    time.Time
	TotalInNumBytes uint64
	TotalInNumInst  uint64
	TotalInNumVar   uint64
	TotalOutNumVar  uint64
}

func LoadLmcrecInfo(r ReadByteReader) (*LmcrecInfo, error) {
	lmcrecInfo := &LmcrecInfo{}

	versionSz, err := binary.ReadUvarint(r)
	if err != nil {
		return nil, err
	}
	if versionSz > 0 {
		buf := make([]byte, versionSz)
		_, err := r.Read(buf)
		if err != nil {
			return nil, err
		}
		lmcrecInfo.Version = string(buf)
	}

	prevFileNameSz, err := binary.ReadUvarint(r)
	if err != nil {
		return nil, err
	}
	if prevFileNameSz > 0 {
		buf := make([]byte, prevFileNameSz)
		_, err := r.Read(buf)
		if err != nil {
			return nil, err
		}
		lmcrecInfo.PrevFileName = string(buf)
	}

	varint, err := binary.ReadVarint(r)
	if err != nil {
		return nil, err
	}
	lmcrecInfo.StartTs = time.UnixMicro(varint)
	if lmcrecInfo.State, err = r.ReadByte(); err != nil {
		return nil, err
	}
	varint, err = binary.ReadVarint(r)
	if err != nil {
		return nil, err
	}
	lmcrecInfo.MostRecentTs = time.UnixMicro(varint)
	if lmcrecInfo.TotalInNumBytes, err = binary.ReadUvarint(r); err != nil {
		return nil, err
	}
	if lmcrecInfo.TotalInNumInst, err = binary.ReadUvarint(r); err != nil {
		return nil, err
	}
	if lmcrecInfo.TotalInNumVar, err = binary.ReadUvarint(r); err != nil {
		return nil, err
	}
	if lmcrecInfo.TotalOutNumVar, err = binary.ReadUvarint(r); err != nil {
		return nil, err
	}
	return lmcrecInfo, nil
}

func LoadLmcrecInfoFile(fName string) (*LmcrecInfo, error) {
	f, err := os.Open(fName)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	lmcrecInfo, err := LoadLmcrecInfo(bufio.NewReader(f))
	if err != nil {
		err = fmt.Errorf("LoadLmcrecInfoFile(%q): %v", fName, err)
	}
	return lmcrecInfo, err
}

type LmcrecCheckpoint struct {
	Timestamp time.Time
	Offset    int64
}

type LmcrecCheckpointDecoder interface {
	NextCheckpoint() (*LmcrecCheckpoint, error)
}

type CodecLmcrecCheckpointDecoder struct {
	reader     io.ByteReader
	checkpoint *LmcrecCheckpoint
}

func (decoder *CodecLmcrecCheckpointDecoder) NextCheckpoint() (*LmcrecCheckpoint, error) {
	checkpoint := decoder.checkpoint
	if varint, err := binary.ReadVarint(decoder.reader); err != nil {
		return nil, err
	} else {
		checkpoint.Timestamp = time.UnixMicro(varint).UTC()
	}
	if varint, err := binary.ReadVarint(decoder.reader); err != nil {
		return nil, err
	} else {
		checkpoint.Offset = varint
	}
	return checkpoint, nil
}

func NewCodecLmcrecCheckpointDecoder(reader io.ByteReader) *CodecLmcrecCheckpointDecoder {
	return &CodecLmcrecCheckpointDecoder{
		reader:     reader,
		checkpoint: &LmcrecCheckpoint{},
	}
}

func NewCodecLmcrecCheckpointFileDecoder(fileName string) (*CodecLmcrecCheckpointDecoder, error) {
	f, err := os.Open(fileName)
	if err != nil {
		return nil, err
	}
	return NewCodecLmcrecCheckpointDecoder(bufio.NewReader(f)), err
}
