// LMC REST JSON Parser

package parser

import (
	"encoding/json"
	"fmt"
	"io"
	"strconv"
)

// In order to reduce the size of the recording, names (of instances, classes or
// variables) are mapped into numeric IDs.
//
// Instance and class IDs start from 1, 0 being reserved for
// un-initialized/un-assigned.
//
// Variable IDs start from 0 and they are assigned in the order of discovery,
// 0..N-1, where N is the maximum number of variables in a class.
//
// Instances belonging to a given class may have only a sub-set of fields; for
// that reason the variable values are cached in 2 parallel maps, each indexed
// by the variable ID: current and previous. The 2 maps are flipped with every
// scan.

type LmcVarType uint32

const (
	// LMC Variable Type Enumeration:
	LMC_VAR_TYPE_UNDEFINED = LmcVarType(iota)
	LMC_VAR_TYPE_BOOLEAN
	LMC_VAR_TYPE_BOOLEAN_CONFIG
	LMC_VAR_TYPE_COUNTER
	LMC_VAR_TYPE_GAUGE
	LMC_VAR_TYPE_GAUGE_CONFIG
	LMC_VAR_TYPE_NUMERIC
	LMC_VAR_TYPE_LARGE_NUMERIC
	LMC_VAR_TYPE_NUMERIC_RANGE
	LMC_VAR_TYPE_NUMERIC_CONFIG
	LMC_VAR_TYPE_STRING
	LMC_VAR_TYPE_STRING_CONFIG
)

func (t LmcVarType) String() string {
	typeName := map[LmcVarType]string{
		LMC_VAR_TYPE_UNDEFINED:      "LMC_VAR_TYPE_UNDEFINED",
		LMC_VAR_TYPE_BOOLEAN:        "LMC_VAR_TYPE_BOOLEAN",
		LMC_VAR_TYPE_BOOLEAN_CONFIG: "LMC_VAR_TYPE_BOOLEAN_CONFIG",
		LMC_VAR_TYPE_COUNTER:        "LMC_VAR_TYPE_COUNTER",
		LMC_VAR_TYPE_GAUGE:          "LMC_VAR_TYPE_GAUGE",
		LMC_VAR_TYPE_GAUGE_CONFIG:   "LMC_VAR_TYPE_GAUGE_CONFIG",
		LMC_VAR_TYPE_NUMERIC:        "LMC_VAR_TYPE_NUMERIC",
		LMC_VAR_TYPE_LARGE_NUMERIC:  "LMC_VAR_TYPE_LARGE_NUMERIC",
		LMC_VAR_TYPE_NUMERIC_RANGE:  "LMC_VAR_TYPE_NUMERIC_RANGE",
		LMC_VAR_TYPE_NUMERIC_CONFIG: "LMC_VAR_TYPE_NUMERIC_CONFIG",
		LMC_VAR_TYPE_STRING:         "LMC_VAR_TYPE_STRING",
		LMC_VAR_TYPE_STRING_CONFIG:  "LMC_VAR_TYPE_STRING_CONFIG",
	}
	return fmt.Sprintf("%s (%d)", typeName[t], t)
}

// Map LMC REST -> parser type:
var LmcVarTypeMap = map[string]LmcVarType{
	"Boolean":        LMC_VAR_TYPE_BOOLEAN,
	"Boolean Config": LMC_VAR_TYPE_BOOLEAN_CONFIG,
	"Counter":        LMC_VAR_TYPE_COUNTER,
	"Gauge":          LMC_VAR_TYPE_GAUGE,
	"Gauge Config":   LMC_VAR_TYPE_GAUGE_CONFIG,
	"Numeric":        LMC_VAR_TYPE_NUMERIC,
	"Large Numeric":  LMC_VAR_TYPE_LARGE_NUMERIC,
	"Numeric Range":  LMC_VAR_TYPE_NUMERIC_RANGE,
	"Numeric Config": LMC_VAR_TYPE_NUMERIC_CONFIG,
	"String":         LMC_VAR_TYPE_STRING,
	"String Config":  LMC_VAR_TYPE_STRING_CONFIG,
}

// The following variables should have the value converted to integer; their ar
// being parsed as string due to JSON decoder.UseNumber(), otherwise they would
// be parsed as float64.
var NumericValueVarType = map[LmcVarType]bool{
	LMC_VAR_TYPE_COUNTER:        true,
	LMC_VAR_TYPE_GAUGE:          true,
	LMC_VAR_TYPE_GAUGE_CONFIG:   true,
	LMC_VAR_TYPE_NUMERIC:        true,
	LMC_VAR_TYPE_LARGE_NUMERIC:  true,
	LMC_VAR_TYPE_NUMERIC_RANGE:  true,
	LMC_VAR_TYPE_NUMERIC_CONFIG: true,
}

// The main function of the parser is to populate the value cache. However in
// the process it may detect other events, such as new instance, class, variable
// mapping or instance deletion that also need to be recorded.
type LmcParserNewClassEvent struct {
	Name string
	Id   uint32
}

type LmcParserNewVariableEvent struct {
	Name    string
	Type    LmcVarType
	Id      uint32
	ClassId uint32
}

type LmcParserNewInstanceEvent struct {
	Name     string
	Id       uint32
	ParentId uint32
	ClassId  uint32
}

type LmcParserInstanceDeletionEvent struct {
	Id uint32
}

// JSON data model:
type LmcVariable struct {
	Name  string
	Type  string
	Value any
}

type LmcInstance struct {
	Instance  string
	Class     string
	Variables []*LmcVariable
	Children  []*LmcInstance
}

type LmcVariableInfo struct {
	Type  LmcVarType
	VarId uint32
}

type LmcClassInfo struct {
	ClassId uint32
	// Variable description is indexed by name:
	VariableDescription map[string]*LmcVariableInfo
}

type LmcInstanceCacheEntry struct {
	Name      string
	InstId    uint32
	Parent    *LmcInstanceCacheEntry
	ClassInfo *LmcClassInfo
	// Dual variable value cache: [CurrIndex][varId]
	Variables [2]map[uint32]any
	// Instances may be deleted, in that they no longer appear in the scan. To
	// keep track of deletions each scan will have a scan# incremented (with
	// rollover). At the end of the scan all instances whose scan# doesn't match
	// the global one will be deleted.
	scanNum uint8
}

// The double buffer approach for variables relies upon the fact that
// consecutive scans are for the *same* process. However the process may be
// restarted in-between scans with such a timing that the REST requests are not
// impacted. The parser should check if such condition occurs by comparing
// certain variables of certain classes against the previous run; if no
// differences are detected then the new scan belongs to the same process.
// Obvious candidates are the PID and the start time.
//
// The following map lists such variable names on a per-class basis:
var ProcessCheckClassAndVariables = map[string]map[string]bool{
	"ManagedProcess.SrcDist":  {"processID": true, "time": true},
	"ManagedProcess.SinkDist": {"processID": true, "time": true},
}

type LmcParser struct {
	// The public instance cache, indexed by ID for faster iteration:
	InstanceCache map[uint32]*LmcInstanceCacheEntry

	// The current index for the double buffer variable set:
	CurrIndex int

	// The list of *LmcParser...Event:
	Events []any

	// The class cache, indexed by class name:
	ClassCache map[string]*LmcClassInfo

	// The private instance cache, indexed by name for parser lookup:
	instanceCacheByName map[string]*LmcInstanceCacheEntry

	// Persistent instance name -> ID mapping, in case an instance reappears:
	persistInstNameId map[string]uint32

	// The scan#:
	scanNum uint8

	// The reusable structure for JSON decoding:
	lmcInstanceList []*LmcInstance

	// Counters for the number of instances and variables found:
	numInstances int
	numVariables int

	// Process signature, used for same process detection:
	processSig map[string]any // ["INSTANCE:VARIABLE"] = VALUE
}

func NewLmcParser() *LmcParser {
	return &LmcParser{
		InstanceCache:       make(map[uint32]*LmcInstanceCacheEntry),
		CurrIndex:           0,
		Events:              nil,
		ClassCache:          make(map[string]*LmcClassInfo),
		instanceCacheByName: make(map[string]*LmcInstanceCacheEntry),
		persistInstNameId:   make(map[string]uint32),
		scanNum:             0,
		lmcInstanceList:     make([]*LmcInstance, 0),
	}
}

func (p *LmcParser) processInstanceList(lmcInstanceList []*LmcInstance, parent *LmcInstanceCacheEntry, noNewEvents bool) error {
	currIndex := p.CurrIndex
	p.numInstances += len(lmcInstanceList)
	for _, lmcInstance := range lmcInstanceList {
		// Instance:
		instName := lmcInstance.Instance
		inst, existentInst := p.instanceCacheByName[instName]
		if !existentInst {
			className := lmcInstance.Class
			// Class info:
			classInfo := p.ClassCache[className]
			if classInfo == nil {
				// Assign new class ID:
				classInfo = &LmcClassInfo{
					ClassId:             uint32(len(p.ClassCache) + 1), // reserve 0 for uninitialized
					VariableDescription: make(map[string]*LmcVariableInfo),
				}
				p.ClassCache[lmcInstance.Class] = classInfo
				if !noNewEvents {
					p.Events = append(p.Events,
						&LmcParserNewClassEvent{className, classInfo.ClassId},
					)
				}
			}
			instId, ok := p.persistInstNameId[instName]
			if !ok {
				instId = uint32(len(p.persistInstNameId) + 1) // reserve 0 for root
				p.persistInstNameId[instName] = instId
			}
			inst = &LmcInstanceCacheEntry{
				Name:      instName,
				InstId:    instId,
				Parent:    parent,
				ClassInfo: classInfo,
				Variables: [2]map[uint32]any{make(map[uint32]any), make(map[uint32]any)},
			}
			p.InstanceCache[instId] = inst
			p.instanceCacheByName[instName] = inst
			if !noNewEvents {
				parentInstId := uint32(0)
				if parent != nil {
					parentInstId = parent.InstId
				}
				p.Events = append(p.Events,
					&LmcParserNewInstanceEvent{instName, instId, parentInstId, classInfo.ClassId},
				)
			}
		} else if inst.scanNum == p.scanNum {
			return fmt.Errorf("duplicate inst: %q", lmcInstance.Instance)
		}

		// Mark instance as found in this scan:
		inst.scanNum = p.scanNum

		// Process variables:
		classInfo := inst.ClassInfo
		p.numVariables += len(lmcInstance.Variables)
		for _, lmcVariable := range lmcInstance.Variables {
			variableDescription := classInfo.VariableDescription[lmcVariable.Name]
			if variableDescription == nil {
				lmcEncoderVarType, ok := LmcVarTypeMap[lmcVariable.Type]
				if !ok {
					return fmt.Errorf(
						"invalid variable type %q for inst: %q, class: %q, var: %q",
						lmcVariable.Type, lmcInstance.Instance, lmcInstance.Class, lmcVariable.Name,
					)
				}
				variableDescription = &LmcVariableInfo{
					Type:  lmcEncoderVarType,
					VarId: uint32(len(classInfo.VariableDescription)),
				}
				classInfo.VariableDescription[lmcVariable.Name] = variableDescription
				if !noNewEvents {
					p.Events = append(p.Events,
						&LmcParserNewVariableEvent{lmcVariable.Name, variableDescription.Type, variableDescription.VarId, classInfo.ClassId},
					)
				}
			} else if !existentInst {
				// First time instance, check variable consistency:
				lmcEncoderVarType, ok := LmcVarTypeMap[lmcVariable.Type]
				if !ok {
					return fmt.Errorf(
						"invalid variable type %q for inst: %q, class: %q, var: %q",
						lmcVariable.Type, lmcInstance.Instance, lmcInstance.Class, lmcVariable.Name,
					)
				}
				if variableDescription.Type != lmcEncoderVarType {
					return fmt.Errorf(
						"inconsistent variable type %q for inst: %q, class: %q, var: %q: want: %s, got: %s",
						lmcVariable.Type, lmcInstance.Instance, lmcInstance.Class, lmcVariable.Name, variableDescription.Type, lmcEncoderVarType,
					)
				}
			}
			varIndex := variableDescription.VarId

			// Store the value:
			if NumericValueVarType[variableDescription.Type] {
				// LMC numeric types do not provide information whether they are
				// signed or unsigned. Since Go is a strong type language, be
				// prepared with 2 types of underlying variable and use
				// heuristics to decide which one is appropriate. Using just one
				// type could result in parsing errors, for negative numbers
				// forced into uint or positive values > max int. First the
				// numbers will be extracted as strings, then the 1st character
				// will be inspected for `-' and based on that the appropriate
				// underlying destination for the conversion will be decided.
				var (
					sintValue int64
					uintValue uint64
					value     any
					err       error
				)

				switch v := lmcVariable.Value.(type) {
				case json.Number:
					s := v.String()
					if len(s) > 1 && s[0] == '-' {
						value, err = strconv.ParseInt(s, 10, 64)
					} else {
						value, err = strconv.ParseUint(s, 10, 64)
					}
				case string:
					// Must be range "N (MIN..MAX)", use Sscanf since it gracefully stops after N:
					if len(v) > 1 && v[0] == '-' {
						_, err = fmt.Sscanf(v, "%d", &sintValue)
						value = sintValue
					} else {
						_, err = fmt.Sscanf(v, "%d", &uintValue)
						value = uintValue
					}
				default:
					err = fmt.Errorf("incompatible with %s", variableDescription.Type)
				}
				if err != nil {
					return fmt.Errorf("error parsing inst: %q, var: %#v: %v", instName, lmcVariable, err)
				}
				inst.Variables[currIndex][varIndex] = value
			} else {
				inst.Variables[currIndex][varIndex] = lmcVariable.Value
			}
		}

		// Process the children:
		if len(lmcInstance.Children) > 0 {
			err := p.processInstanceList(lmcInstance.Children, inst, noNewEvents)
			if err != nil {
				return err
			}
		}
	}
	return nil
}

func (p *LmcParser) checkProcessSignature() bool {
	sig, newSigLen := p.processSig, 0
	for _, lmcInstance := range p.lmcInstanceList {
		if processCheckVariables := ProcessCheckClassAndVariables[lmcInstance.Class]; processCheckVariables != nil {
			for _, lmcVariable := range lmcInstance.Variables {
				if processCheckVariables[lmcVariable.Name] {
					newSigLen++
					if sig[lmcInstance.Instance+":"+lmcVariable.Name] != lmcVariable.Value {
						return false
					}
				}
			}
		}
	}
	return len(sig) == newSigLen
}

func (p *LmcParser) computeProcessSignature() {
	sig := make(map[string]any)
	for _, lmcInstance := range p.lmcInstanceList {
		if processCheckVariables := ProcessCheckClassAndVariables[lmcInstance.Class]; processCheckVariables != nil {
			for _, lmcVariable := range lmcInstance.Variables {
				if processCheckVariables[lmcVariable.Name] {
					sig[lmcInstance.Instance+":"+lmcVariable.Name] = lmcVariable.Value
				}
			}
		}
	}
	p.processSig = sig
}

func (p *LmcParser) Parse(r io.Reader, noNewEvents bool) (bool, int, int, error) {
	decoder := json.NewDecoder(r)
	decoder.UseNumber() // least integers are converted to float.
	err := decoder.Decode(&p.lmcInstanceList)
	if err != nil {
		return false, 0, 0, err
	}

	processChanged := false
	if len(p.processSig) == 0 {
		p.computeProcessSignature()
		// First scan should be treated like a noNewEvents:
		noNewEvents = true
	} else if !p.checkProcessSignature() {
		// Process changed:
		processChanged = true
		p.computeProcessSignature()
		// Reset all data:
		p.InstanceCache = make(map[uint32]*LmcInstanceCacheEntry)
		p.ClassCache = make(map[string]*LmcClassInfo)
		p.instanceCacheByName = make(map[string]*LmcInstanceCacheEntry)
		p.persistInstNameId = make(map[string]uint32)
		p.scanNum = 0
		noNewEvents = true
	}

	p.numInstances = 0
	p.numVariables = 0
	p.Events = nil
	p.scanNum++
	err = p.processInstanceList(p.lmcInstanceList, nil, noNewEvents)
	if err != nil {
		return false, 0, 0, err
	}

	// Lock for deleted instances:
	if len(p.InstanceCache) > p.numInstances {
		for instId, inst := range p.InstanceCache {
			if inst.scanNum != p.scanNum {
				p.Events = append(p.Events, &LmcParserInstanceDeletionEvent{instId})
				delete(p.InstanceCache, instId)
				delete(p.instanceCacheByName, inst.Name)
			}
		}
	}

	return processChanged, p.numInstances, p.numVariables, nil
}
