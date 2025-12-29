// Logger for the recorder

package recorder

import (
	"github.com/bgp59/logrusx"
)

// Abstract the logger interface needed by the parser such that both logrus
// *Logger or *Entry can be used:
type RecorderLogger interface {
	Debug(...any)
	Debugf(string, ...any)
	Info(...any)
	Infof(string, ...any)
	Warn(...any)
	Warnf(string, ...any)
	Error(...any)
	Errorf(string, ...any)
	Fatal(...any)
	Fatalf(string, ...any)
}

// Create the root logger:
var RootLogger = logrusx.NewCollectableLogger()

func init() {
	RootLogger.AddCallerSrcPathPrefix(1)
}
