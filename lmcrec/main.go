package main

import (
	"os"

	"lmcrec/recorder"
)

func main() {
	// Seed version from buildinfo.go:
	recorder.Version = Version
	os.Exit(recorder.Run())
}
