package parser

import (
	"bytes"
	"fmt"
	"strings"
	"testing"
)

type ParserTestCase struct {
	Name               string
	Description        string
	PrimeJsonData      string
	JsonData           string
	NoNewEvents        bool
	WantVariables      map[string]map[uint32]any
	WantEvents         []any
	WantProcessChanged bool
	WantNumInstances   int
	WantNumVariables   int
	WantErrStr         string
}

func testParserCmpEvents(ref, with []any) *bytes.Buffer {
	buf := &bytes.Buffer{}

	makeEventMap := func(events []any) map[any]bool {
		eventMap := map[any]bool{}
		for _, event := range events {
			switch e := event.(type) {
			case *LmcParserNewClassEvent:
				eventMap[*e] = true
			case *LmcParserNewVariableEvent:
				eventMap[*e] = true
			case *LmcParserNewInstanceEvent:
				eventMap[*e] = true
			case *LmcParserInstanceDeletionEvent:
				eventMap[*e] = true
			}
		}
		return eventMap
	}

	refMap, withMap := makeEventMap(ref), makeEventMap(with)

	for event := range refMap {
		if withMap[event] {
			delete(refMap, event)
			delete(withMap, event)
		}
	}

	if len(refMap) > 0 {
		fmt.Fprintf(buf, "\nMissing event(s):")
		for event := range refMap {
			fmt.Fprintf(buf, "\n\t%v", event)
		}
	}

	if len(withMap) > 0 {
		fmt.Fprintf(buf, "\nUnexpected event(s):")
		for event := range withMap {
			fmt.Fprintf(buf, "\n\t%v", event)
		}
	}
	return buf
}

func testParser(tc *ParserTestCase, t *testing.T) {
	if tc.Description != "" {
		t.Log(tc.Description)
	}
	parser := NewLmcParser()

	if tc.PrimeJsonData != "" {
		if _, _, _, err := parser.Parse(strings.NewReader(tc.PrimeJsonData), true); err != nil {
			t.Fatal(err)
		}
	}

	gotProcessChanged, gotNumInstances, gotNumVariables, gotErr := parser.Parse(
		strings.NewReader(tc.JsonData), tc.NoNewEvents,
	)

	if tc.WantErrStr != "" && (gotErr == nil || !strings.Contains(gotErr.Error(), tc.WantErrStr)) ||
		tc.WantErrStr == "" && gotErr != nil {
		t.Fatalf("err: want: %q, got: %v", tc.WantErrStr, gotErr)
	}

	if tc.WantErrStr != "" {
		return
	}

	if tc.WantNumInstances != gotNumInstances {
		t.Errorf("numInstances: want: %d, got: %d", tc.WantNumInstances, gotNumInstances)
	}
	if tc.WantNumVariables != gotNumVariables {
		t.Errorf("numVariables: want: %d, got: %d", tc.WantNumVariables, gotNumVariables)
	}
	if tc.WantProcessChanged != gotProcessChanged {
		t.Errorf("processChanged: want: %v, got: %v", tc.WantProcessChanged, gotProcessChanged)
	}

	currIndex := parser.CurrIndex
	for instanceName, wantVariables := range tc.WantVariables {
		instanceCacheEntry, ok := parser.instanceCacheByName[instanceName]
		if !ok {
			t.Errorf("parser.InstanceCache[%q] not found", instanceName)
			continue
		}
		gotVariables := instanceCacheEntry.Variables[currIndex]

		for varId, want := range wantVariables {
			if got, ok := gotVariables[varId]; !ok {
				t.Errorf("instance %q: var[%d]: missing", instanceName, varId)
			} else if want != got {
				t.Errorf("instance %q: var[%d]: want: %v, got: %v", instanceName, varId, want, got)
			}
		}

		for varId, val := range gotVariables {
			if _, ok := wantVariables[varId]; !ok {
				t.Errorf("instance %q: unexpected var[%d] = %v", instanceName, varId, val)
			}
		}
	}

	if len(tc.WantEvents) != len(parser.Events) {
		t.Errorf(
			"len(Events): want: %d, got: %d", len(tc.WantEvents), len(parser.Events),
		)
	} else {
		if buf := testParserCmpEvents(tc.WantEvents, parser.Events); buf.Len() > 0 {
			t.Error(buf)
		}
	}
}

func TestParser(t *testing.T) {
	for _, tc := range ParserTestCases {
		t.Run(
			tc.Name,
			func(t *testing.T) { testParser(tc, t) },
		)
	}
}
