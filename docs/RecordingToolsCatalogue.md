# Recording Tools Catalogue

<!-- TOC tocDepth:2..3 chapterDepth:2..6 -->

- [lmcrec](#lmcrec)
- [lmcrec-from-samples](#lmcrec-from-samples)
- [snap-samples.sh](#snap-samplessh)

<!-- /TOC -->

## lmcrec

```text
Usage: lmcrec [-config CONFIG_FILE] -inst INST
  -config string
     Config file (default based on $LMCREC_CONFIG, with fallback over "lmcrec-config.yaml") (default ".../lmcrec/config/lmcrec-config.yaml")
  -inst string
     Recorder INST, must match 'inst' or 'url' in 'recorders' section of the config, mandatory.
  -log-disable-src-file
     Disable the reporting of the source file:line# info
  -log-file string
     Log to a file or use stdout/stderr
  -log-file-max-backup-num int
     How many older log files to keep upon rotation (default 1)
  -log-file-max-size-mb int
     Log file max size, in MB, before rotation, use 0 to disable (default 10)
  -log-level string
     Log level name, one of [panic fatal error warning info debug trace] (default "info")
  -log-use-json
     Structure the logged record in JSON
  -version
     Display version and exit
```

## lmcrec-from-samples

```text
Usage: lmcrec-from-samples [-s START_SAMPLE_NUM] [-e END_SAMPLE_NUM] SAMPLES_DIR
  -e int
     Short flag for end-sample-num (default -1)
  -end-sample-num int
     If > 0, last sample# to use, otherwise use till last (default -1)
  -s int
     Short flag for start-sample-num (default 1)
  -start-sample-num int
     If > 1, first sample# to use, otherwise start from 1 (default 1)
  -v Short flag for version
  -version
     Display version and exit

```

## snap-samples.sh

```text

Usage: snap-samples.sh [-k SECURITY_KEY_FILE] [-n N_SAMPLES] [-i INTERVAL] [-o OUT_DIR] [-z] URL

Collect N_SAMPLES from URL and store them under OUT_DIR/TIMESTAMP dir.

Args:
    -k SECURITY_KEY_FILE
        Read security from this file, empty if no security key is needed. 
        Default: `'

    -n N_SAMPLES
        The number of samples to collect. Default: 5

    -i INTERVAL
        The interval, in seconds, between samples. Default: 5

    -o OUTPUT_DIR_ROOT
        Output dir root; the samples will placed under
            OUTPUT_DIR_ROOT/HOST:PORT/PATH/YYYY-MM-DDTHH:MM:SS±HHMM
        directory. HOST:PORT/PATH is derived from the URL
        http[s]://HOST:PORT/PATH with the http[s]:// removed. The full
        path of the actual dir will be displayed to stdout at the end
        of the run and it is recommended to capture it in a shell variable

            samples_dir=`snap-samples.sh ARGS...`
        
        Each response will create 2 files, OUT_DIR/response-body.K
        and OUT_DIR/response-headers.K where K=1..N_SAMPLES.
        Default: `.../runtime/lmcrec/samples'

    -z
        Request compressed data (deflate). Default: no

    URL
        The URL for the request, mandatory
```
