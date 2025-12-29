package main

import (
	"fmt"
	"time"

	"lmcrec/codec"
)

const INDENT = "    "
const INDENT2 = INDENT + INDENT

var preamble = `
from lmcrec.playback.codec.info_decoder import (
    LmcrecInfo,
	LmcrecInfoState,
)

`

type LmcrecInfoTestCase struct {
	version         string
	prevFileName    string
	startTs         time.Time
	state           byte
	mostRecentTs    time.Time
	totalInNumBytes uint64
	totalInNumInst  uint64
	totalInNumVar   uint64
	totalOutNumVar  uint64
}

func makeInfo(name string, tcList []*LmcrecInfoTestCase) {
	fmt.Printf("%s = [", name)
	for _, tc := range tcList {
		startTs := tc.startTs.UnixMicro()
		mostRecentTs := tc.mostRecentTs.UnixMicro()
		buf := codec.BuildLmcrecInfoBuf(
			tc.version,
			tc.prevFileName,
			startTs,
			tc.state,
			mostRecentTs,
			tc.totalInNumBytes,
			tc.totalInNumInst,
			tc.totalInNumVar,
			tc.totalOutNumVar,
		)
		fmt.Printf("\n%s(bytes([", INDENT)
		for i, b := range buf {
			if i&15 == 0 {
				fmt.Printf("\n%s", INDENT2)
			}
			fmt.Printf("0x%02x,", b)
		}
		fmt.Printf("\n%s]), LmcrecInfo(", INDENT)
		fmt.Printf("\n%sversion=%q,", INDENT2, tc.version)
		fmt.Printf("\n%sprev_file_name=%q,", INDENT2, tc.prevFileName)
		fmt.Printf("\n%sstart_ts=%.06f,", INDENT2, float64(startTs)/1_000_000.)
		fmt.Printf("\n%sstate=LmcrecInfoState(%d),", INDENT2, tc.state)
		fmt.Printf("\n%smost_recent_ts=%.06f,", INDENT2, float64(mostRecentTs)/1_000_000.)
		fmt.Printf("\n%stotal_in_num_bytes=%d,", INDENT2, tc.totalInNumBytes)
		fmt.Printf("\n%stotal_in_num_inst=%d,", INDENT2, tc.totalInNumInst)
		fmt.Printf("\n%stotal_in_num_var=%d,", INDENT2, tc.totalInNumVar)
		fmt.Printf("\n%stotal_out_num_var=%d,", INDENT2, tc.totalOutNumVar)
		fmt.Printf("\n%s)),", INDENT)
	}
	fmt.Print("\n]\n\n")
}

func main() {
	fmt.Print(preamble)

	makeInfo(
		"test_cases",
		[]*LmcrecInfoTestCase{
			{
				"",
				"",
				time.Unix(0, 0),
				codec.INFO_FILE_STATE_UNINITIALIZED,
				time.Unix(0, 0),
				111213,
				1112,
				110,
				93,
			},
			{
				"v1.2.3",
				"prev_file",
				time.Date(2025, 1, 2, 3, 4, 5, 0, time.UTC),
				codec.INFO_FILE_STATE_ACTIVE,
				time.Date(2025, 1, 2, 8, 9, 10, 11, time.UTC),
				1111213,
				11112,
				1110,
				193,
			},
			{
				"v4.5.6",
				"prev_file",
				time.Date(2025, 10, 12, 3, 4, 5, 0, time.UTC),
				codec.INFO_FILE_STATE_CLOSED,
				time.Date(2025, 11, 12, 18, 19, 30, 44, time.UTC),
				2111213,
				21112,
				210,
				293,
			},
		},
	)
}
