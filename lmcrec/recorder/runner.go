package recorder

import (
	"flag"
	"fmt"
	"os"
	"os/signal"
	"path"
	"path/filepath"
	"syscall"
	"time"

	"github.com/bgp59/logrusx"
)

const (
	RUNTIME_ENV_VAR     = "LMCREC_RUNTIME"
	RUNTIME_DEFAULT     = "$HOME/runtime/lmcrec"
	CONFIG_ENV_VAR      = "LMCREC_CONFIG"
	CONFIG_FILE_DEFAULT = "lmcrec-config.yaml"

	CONFIG_FLAG  = "config"
	INST_FLAG    = "inst"
	VERSION_FLAG = "version"

	SHUTDOWN_MAX_WAIT = 2 * time.Second
)

// Version will be seeded by main:
var Version = "N/A"

var runnerLogger = RootLogger.NewCompLogger("runner")

func init() {
	if os.Getenv(RUNTIME_ENV_VAR) == "" {
		os.Setenv(RUNTIME_ENV_VAR, os.ExpandEnv(RUNTIME_DEFAULT))
		fmt.Fprintf(os.Stderr, "Warning! Using %s=%q based on internal default\n", RUNTIME_ENV_VAR, os.Getenv(RUNTIME_ENV_VAR))
	}
}

func Run() int {
	logrusx.EnableLoggerArgs()

	configFile, configFileSrc := "", ""
	flag.StringVar(
		&configFile,
		CONFIG_FLAG,
		"",
		fmt.Sprintf("Config file. If not specified then env var %s with fallback over %q", CONFIG_ENV_VAR, CONFIG_FILE_DEFAULT),
	)

	inst := ""
	flag.StringVar(
		&inst,
		INST_FLAG,
		"",
		"Recorder INST, must match 'inst' or 'url' in 'recorders' section of the config, mandatory.",
	)

	displayVer := false
	flag.BoolVar(
		&displayVer,
		VERSION_FLAG,
		false,
		"Display version and exit",
	)

	flag.Usage = func() {
		fmt.Fprintf(os.Stderr,
			"Usage: %s [-%s CONFIG_FILE] -%s INST\n",
			path.Base(os.Args[0]),
			CONFIG_FLAG, INST_FLAG,
		)
		flag.PrintDefaults()
	}

	flag.Parse()

	if displayVer {
		fmt.Println(Version)
		return 0
	}
	if inst == "" {
		runnerLogger.Errorf("Missing mandatory -%s INST", INST_FLAG)
		return 1
	}

	// Resolve config file:
	if configFile != "" {
		configFileSrc = fmt.Sprintf("command line -%s %s", CONFIG_FLAG, configFile)
	} else {
		configFile = os.Getenv(CONFIG_ENV_VAR)
		if configFile != "" {
			configFileSrc = fmt.Sprintf("env var %s=%s", CONFIG_ENV_VAR, configFile)
		} else {
			configFile = CONFIG_FILE_DEFAULT
			configFileSrc = fmt.Sprintf("built-in default=%s", configFile)
		}
	}

	configFileSrc = "Config based on " + configFileSrc

	if !filepath.IsAbs(configFile) {
		var err error
		configFile, err = filepath.Abs(configFile)
		if err != nil {
			runnerLogger.Fatalf("cannot determine abs path for config based on %s: %v", configFileSrc, err)
		}
		configFileSrc += fmt.Sprintf(", abs path=%s", configFile)
	}

	runnerLogger.Info(configFileSrc)
	config, loggerConfig, err := LoadLmcrecConfig(configFile, inst)
	if err != nil {
		runnerLogger.Error(err)
		return 1
	}

	taskLoop := NewTaskLoop()
	recorder, err := NewLmcrec(config, taskLoop)
	if err != nil {
		runnerLogger.Error(err)
		return 1
	}

	if loggerConfig != nil {
		logrusx.ApplyLoggerArgs(loggerConfig, true)
		if loggerConfig.LogFile == "" {
			loggerConfig.LogFile = RECORDER_CONFIG_LOG_FILE_DEFAULT
		}
		loggerConfig.LogFile = expandInstEnv(loggerConfig.LogFile, recorder.Inst)
		if err := RootLogger.SetLogger(loggerConfig); err != nil {
			runnerLogger.Error(err)
			return 1
		}
	}

	stopSignal := make(chan os.Signal, 3)
	flushSignal := make(chan os.Signal, 1)
	rolloverSignal := make(chan os.Signal, 1)
	signal.Notify(stopSignal, syscall.SIGINT, syscall.SIGTERM, syscall.SIGHUP)
	signal.Notify(flushSignal, syscall.SIGUSR1)
	signal.Notify(rolloverSignal, syscall.SIGUSR2)

	runnerLogger.Infof("Start %s recorder", recorder.Inst)
	// If log file is in effect, log config file resolution into it too:
	if loggerConfig.LogFile != "" {
		runnerLogger.Info(configFileSrc)
	}
	taskLoop.Start(recorder.Inst, recorder.Scan, *config.ScanInterval)

	retCode := 1
	for run := true; run; {
		select {
		case sig := <-stopSignal:
			runnerLogger.Warnf("%s received", sig)
			retCode = 0
			run = false
		case sig := <-flushSignal:
			runnerLogger.Warnf("%s received, perform flush", sig)
			if err := recorder.Flush(); err != nil {
				runnerLogger.Error(err)
				run = false
			}
		case sig := <-rolloverSignal:
			runnerLogger.Warnf("%s received, perform rollover", sig)
			if err := recorder.Close(); err != nil {
				runnerLogger.Error(err)
				run = false
			}
		case <-taskLoop.AllDone:
			run = false
		}
	}
	runnerLogger.Warnf("Shutdown %s", recorder.Inst)
	if err := taskLoop.ShutdownMaxWait(SHUTDOWN_MAX_WAIT); err != nil {
		runnerLogger.Error(err)
		retCode = 1
	}
	if err := recorder.Shutdown(); err != nil {
		runnerLogger.Error(err)
		retCode = 1
	}

	return retCode
}
