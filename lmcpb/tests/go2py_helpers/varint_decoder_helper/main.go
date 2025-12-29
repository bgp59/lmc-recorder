// Generate varint testcases for python varint decoder

package main

import (
	"encoding/binary"
	"fmt"
	"math"
)

const INDENT = "    "

var preamble = `
`

func generateTestCases[T uint64 | int64](name string, testCases []T, varintFunc func([]byte, T) int) {
	buf := make([]byte, 16)
	fmt.Printf("%s = [\n", name)
	for _, u := range testCases {
		n := varintFunc(buf, u)
		fmt.Printf("%s(bytes([", INDENT)
		for i := range n {
			if i > 0 {
				fmt.Printf(", ")
			}
			fmt.Printf("0x%02x", buf[i])
		}
		fmt.Printf("]), %d),\n", u)
	}
	fmt.Printf("]\n\n")
}

func main() {
	uvarintTestCases := []uint64{}
	for k := 0; k < 64; k += 7 {
		v := uint64(1 << k)
		uvarintTestCases = append(uvarintTestCases, v-1, v, v+1)

	}
	uvarintTestCases = append(uvarintTestCases, math.MaxUint64)

	varintTestCases := []int64{}
	for k := 0; k < 63; k += 7 {
		v := int64(1 << k)
		if v != 1 {
			varintTestCases = append(varintTestCases, -v-1, -v, -v+1, v-1, v, v+1)
		} else {
			varintTestCases = append(varintTestCases, -v-1, -v, v-1, v, v+1)
		}
	}
	varintTestCases = append(varintTestCases, math.MinInt64, math.MaxInt64)

	fmt.Print(preamble)

	generateTestCases("uvarint_test_cases", uvarintTestCases, binary.PutUvarint)
	generateTestCases("varint_test_cases", varintTestCases, binary.PutVarint)
}
