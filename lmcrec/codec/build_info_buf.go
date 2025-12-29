package codec

// Utility function for testing the python decoder:
func BuildLmcrecInfoBuf(
	version string,
	prevFileName string,
	startTs int64,
	state byte,
	mostRecentTs int64,
	totalInNumBytes uint64,
	totalInNumInst uint64,
	totalInNumVar uint64,
	totalOutNumVar uint64,
) []byte {
	dummyFileEncoder := &CodecLmcrecFileEncoder{
		CodecLmcrecEncoder: CodecLmcrecEncoder{
			startTs:         startTs,
			mostRecentTs:    mostRecentTs,
			totalInNumBytes: totalInNumBytes,
			totalInNumInst:  totalInNumInst,
			totalInNumVar:   totalInNumVar,
			totalOutNumVar:  totalOutNumVar,
		},
		version:       version,
		prevFileName:  prevFileName,
		infoFileState: state,
	}

	bufLen, _ := dummyFileEncoder.updateInfoBuf()
	return dummyFileEncoder.infoBuf[:bufLen]
}
