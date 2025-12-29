package recorder

import (
	"fmt"
	"io"

	"lmcrec/codec"
	"lmcrec/parser"
)

// Declare a recordable parser interface that can be replaced with a mock for testing:
type LmcParseRecorder interface {
	Parse(r io.Reader, noNewEvents bool) (processChanged bool, scanInInstCount int, scanInVarCount int, err error)
	Record(encoder codec.LmcrecEncoder, full bool) (outNumVarCount int, err error)
	GetCurrIndex() int
	SetCurrIndex(int)
	FlipCurrIndex()
}

// Real-life object implementation:
type RecordableLmcParser struct {
	parser.LmcParser
}

func NewRecordableLmcParser() LmcParseRecorder {
	return &RecordableLmcParser{
		LmcParser: *parser.NewLmcParser(),
	}
}

func (rp *RecordableLmcParser) Record(encoder codec.LmcrecEncoder, full bool) (int, error) {
	var err error

	for _, event := range rp.Events {
		switch e := event.(type) {
		case *parser.LmcParserNewClassEvent:
			err = encoder.ClassInfo(e.Name, e.Id)
		case *parser.LmcParserNewInstanceEvent:
			err = encoder.InstInfo(e.Name, e.ClassId, e.Id, e.ParentId)
		case *parser.LmcParserNewVariableEvent:
			err = encoder.VarInfo(e.Name, e.Id, e.ClassId, uint32(e.Type))
		case *parser.LmcParserInstanceDeletionEvent:
			err = encoder.DeleteInstId(e.Id)
		}
		if err != nil {
			return 0, err
		}
	}

	outVarCount := 0
	currIndex := rp.CurrIndex
	if full {
		for className, classInfo := range rp.ClassCache {
			classId := classInfo.ClassId
			if err = encoder.ClassInfo(className, classId); err != nil {
				return 0, err
			}
			for varName, varInfo := range classInfo.VariableDescription {
				if err = encoder.VarInfo(varName, varInfo.VarId, classId, uint32(varInfo.Type)); err != nil {
					return 0, err
				}
			}
		}

		for instId, inst := range rp.InstanceCache {
			parentInstId := uint32(0)
			if inst.Parent != nil {
				parentInstId = inst.Parent.InstId
			}
			if err = encoder.InstInfo(inst.Name, inst.ClassInfo.ClassId, instId, parentInstId); err != nil {
				return 0, err
			}
			for varId, value := range inst.Variables[currIndex] {
				if err = encoder.VarValue(varId, value); err != nil {
					return 0, fmt.Errorf("instance: %s: %v", inst.Name, err)
				}
				outVarCount++
			}
		}
	} else {
		for instId, inst := range rp.InstanceCache {
			instIdPublished := false
			currVars, prevVars := inst.Variables[currIndex], inst.Variables[1-currIndex]
			for varId, currValue := range currVars {
				if currValue != prevVars[varId] {
					if !instIdPublished {
						if err = encoder.SetInstId(instId); err != nil {
							return 0, err
						}
						instIdPublished = true
					}
					if err = encoder.VarValue(varId, currValue); err != nil {
						return 0, err
					}
					outVarCount++
				}
			}
		}
	}
	return outVarCount, nil
}

func (rp *RecordableLmcParser) GetCurrIndex() int { return rp.CurrIndex }

func (rp *RecordableLmcParser) SetCurrIndex(currIndex int) { rp.CurrIndex = currIndex }

func (rp *RecordableLmcParser) FlipCurrIndex() { rp.CurrIndex = 1 - rp.CurrIndex }
