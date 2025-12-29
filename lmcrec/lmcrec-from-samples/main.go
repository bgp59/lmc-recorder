// Create LMC recording from samples captured by tools/snap-samples.sh

package main

import (
	"flag"
	"fmt"
	"os"
	"path"

	"lmcrec/recorder"
)

const (
	START_SAMPLE_NUM_SHORT_ARG_NAME = "s"
	START_SAMPLE_NUM_LONG_ARG_NAME  = "start-sample-num"
	START_SAMPLE_NUM_DEFAULT        = 1
	END_SAMPLE_NUM_SHORT_ARG_NAME   = "e"
	END_SAMPLE_NUM_LONG_ARG_NAME    = "end-sample-num"
	VERSION_SHORT_ARG_NAME          = "v"
	VERSION_LONG_ARG_NAME           = "version"
	END_SAMPLE_NUM_DEFAULT          = -1
)

func main() {
	startSampleNum, endSampleNum := START_SAMPLE_NUM_DEFAULT, END_SAMPLE_NUM_DEFAULT

	flag.IntVar(
		&startSampleNum,
		START_SAMPLE_NUM_LONG_ARG_NAME,
		START_SAMPLE_NUM_DEFAULT,
		"If > 1, first sample# to use, otherwise start from 1",
	)
	flag.IntVar(
		&startSampleNum,
		START_SAMPLE_NUM_SHORT_ARG_NAME,
		START_SAMPLE_NUM_DEFAULT,
		fmt.Sprintf("Short flag for %s", START_SAMPLE_NUM_LONG_ARG_NAME),
	)

	flag.IntVar(
		&endSampleNum,
		END_SAMPLE_NUM_LONG_ARG_NAME,
		END_SAMPLE_NUM_DEFAULT,
		"If > 0, last sample# to use, otherwise use till last",
	)
	flag.IntVar(
		&endSampleNum,
		END_SAMPLE_NUM_SHORT_ARG_NAME,
		END_SAMPLE_NUM_DEFAULT,
		fmt.Sprintf("Short flag for %s", END_SAMPLE_NUM_LONG_ARG_NAME),
	)

	displayVersion := false
	flag.BoolVar(
		&displayVersion,
		VERSION_LONG_ARG_NAME,
		false,
		"Display version and exit",
	)
	flag.BoolVar(
		&displayVersion,
		VERSION_SHORT_ARG_NAME,
		false,
		fmt.Sprintf("Short flag for %s", VERSION_LONG_ARG_NAME),
	)

	flag.Usage = func() {
		fmt.Fprintf(
			os.Stderr,
			"Usage: %s [-%s START_SAMPLE_NUM] [-%s END_SAMPLE_NUM] SAMPLES_DIR\n",
			path.Base(os.Args[0]), START_SAMPLE_NUM_SHORT_ARG_NAME, END_SAMPLE_NUM_SHORT_ARG_NAME,
		)
		flag.PrintDefaults()
	}
	flag.Parse()

	if displayVersion {
		fmt.Println(Version)
		os.Exit(0)
	}

	if len(flag.Args()) < 1 {
		fmt.Fprintf(os.Stderr, "Missing mandatory SAMPLES_DIR\n")
		os.Exit(1)
	}

	recorder.Version = Version

	recFileName, err := recorder.RecordSampleFiles(flag.Arg(0), startSampleNum, endSampleNum)
	if err != nil {
		fmt.Fprintf(os.Stderr, "%v\n", err)
		os.Exit(1)
	}

	fmt.Printf("%s created\n", recFileName)
}
