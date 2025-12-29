package main

import (
	"bytes"
	"fmt"
	"log"

	"lmcrec/codec"
)

const INDENT = "    "

type DecoderTestCase struct {
	encoderRec any
	decoderRec string
}

func indent(lvl int) string {
	indent := ""
	for range lvl {
		indent += INDENT
	}
	return indent
}

var preamble = `
from lmcrec.playback.codec.decoder import (
    LmcRecord,
	LmcrecType,
	LmcVarType,
)

`

func main() {
	buf := &bytes.Buffer{}
	encoder := codec.NewCodecLmcrecEncoder(buf)
	fmt.Print(preamble)
	fmt.Printf("test_cases = [\n")
	for _, tc := range DecoderTestCases {
		buf.Reset()
		if err := encoder.Record(tc.encoderRec); err != nil {
			log.Fatal(err)
		}
		fmt.Printf("%s(\n", indent(1))
		fmt.Printf("%sbytes([", indent(2))
		for i, b := range buf.Bytes() {
			if i&15 == 0 {
				if i > 0 {
					fmt.Print(",")
				}
				fmt.Printf("\n%s", indent(3))
			} else {
				fmt.Printf(", ")
			}
			fmt.Printf("0x%02x", b)
		}
		fmt.Printf("\n%s]), %s\n", indent(2), tc.decoderRec)
		fmt.Printf("%s),\n", indent(1))
	}
	fmt.Printf("]\n\n")
}
