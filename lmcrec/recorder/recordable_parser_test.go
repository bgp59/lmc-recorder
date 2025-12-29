// Prompt: .github/prompts/recordable_parser_test.go.prompt.md
// Model: Claude Sonnet 4.5

package recorder

import (
	"bytes"
	"fmt"
	"lmcrec/parser"
	"testing"
)

type RecordableParserTestCase struct {
	Name             string
	Description      string
	ClassCache       map[string]*parser.LmcClassInfo
	InstanceCache    map[uint32]*parser.LmcInstanceCacheEntry
	CurrIndex        int
	Events           []any
	Full             bool
	WantOutNumVars   int
	WantErr          any
	WantEncoderCalls []string
	EncoderRetVals   map[string][]error
}

func testRecordableParser(t *testing.T, tc *RecordableParserTestCase) {
	if tc.Description != "" {
		t.Log(tc.Description)
	}

	// Setup parser
	rp := &RecordableLmcParser{
		LmcParser: parser.LmcParser{
			InstanceCache: tc.InstanceCache,
			CurrIndex:     tc.CurrIndex,
			Events:        tc.Events,
			ClassCache:    tc.ClassCache,
		},
	}

	// Handle special case for parent-child test
	if tc.Name == "FullRecordWithParentChild" {
		parent := rp.InstanceCache[1]
		rp.InstanceCache[2] = &parser.LmcInstanceCacheEntry{
			Name:      "child1",
			InstId:    2,
			Parent:    parent,
			ClassInfo: &parser.LmcClassInfo{ClassId: 2},
			Variables: [2]map[uint32]any{
				{0: int64(10)},
				{},
			},
		}
	}

	// Setup mock encoder
	encoder := &MockEncoder{
		retVals: tc.EncoderRetVals,
	}

	// Execute
	gotOutNumVars, gotErr := rp.Record(encoder, tc.Full)

	// Check error
	buf := &bytes.Buffer{}
	checkResultedErr(tc.WantErr, gotErr, buf)

	// Only check output and calls if both errors are nil
	if tc.WantErr == nil && gotErr == nil {
		if tc.WantOutNumVars != gotOutNumVars {
			fmt.Fprintf(buf, "\noutNumVars: want: %d, got: %d", tc.WantOutNumVars, gotOutNumVars)
		}

		encoder.CompareCallsAnyOrder(tc.WantEncoderCalls, buf)
	}

	if buf.Len() > 0 {
		t.Errorf("%s", buf.String())
	}
}

func TestRecordableParser(t *testing.T) {
	for _, tc := range RecordableParserTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testRecordableParser(t, tc) },
		)
	}
}
