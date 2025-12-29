# Installation Guide

## Prerequisites

* 64 bit Linux
* [curl](https://curl.se/docs/manpage.html) and [jq](https://jqlang.org/manual/) packages installed (RPMs available for all major distro's). While they are not required for normal operation, they are needed for the preliminary steps.
* Python >= 3.10
* a writable directory to serve as lmcrec runtime root; set its path into the `LMCREC_RUNTIME` env var. If not set, `LMCREC_RUNTIME` will default to `$HOME/runtime/lmcrec`
* LSEG components configured w/ the REST interface on
* if LSEG components are configured w/ `securityKey` then place the clear text in an owner only access file, for instance `$HOME/.lmcrec/security-key` (this is similar to a ssh private key). Note that the clear text can be recovered from the encrypted form by running:

    ```bash
    dacsObfuscatePassword -d ENCRYPTED_SECURITY_KEY
    ```

    In practice there may be a security key for each (type of) environment: `prod`, `qa`, `dev`, etc., therefore multiple files may be required: `$HOME/.lmcrec/security-key.prod`, `$HOME/.lmcrec/security-key.qa`, etc.

    **IMPORTANT!** Pretty much like ssh private keys, the file(s) should be accessible only to the owner:

    ```bash
    chmod 0600 $HOME/.lmcrec/security*
    ```

## Software

* download the recorder archive and the playback Python wheel from the [latest
  release](https://github.com/bgp59/lmc-recorder/releases) page
* extract the archive to a convenient location, e.g. `/usr/local`. The archive
  contains both the versioned path for the release and a symlink to it.

    ```bash
    cd /usr/local
    tar xvf /tmp/lmcrec-linux-amd64-v0.0.1.tgz
    ```

    will create:

    ```text
    /usr/local/lmcrec-linux-amd64 -> lmcrec-linux-amd64-v0.0.1
    /usr/local/lmcrec-linux-amd64-v0.0.1/bin
                                        /reference
                                        relnotes.txt
                                        /scripts
    ```

* add `scripts` location to `PATH` in the shell's initialization file. For
  instance for `bash` add to `~/.bashrc`:

    ```bash
    lmcrec_path=/usr/local/lmcrec-linux-amd64/scripts
    case "$PATH" in
        $lmcrec_path|$lmcrec_path:*|*:$lmcrec_path|*:$lmcrec_path:*) : ;;
        *) export PATH="$lmcrec_path${PATH:+:}$PATH";;
    esac
    ```

* install the Python package, potentially under a virtual environment:

    ```bash
    # Optional virtual environment steps:
    python3 -m venv $HOME/venv/lmcrec
    . $HOME/venv/lmcrec/bin/activate
    

    pip3 install --upgrade /tmp/lmcrec-0.0.1-py3-none-any.whl
    ```

## Preliminary Steps

Before proceeding with the configuration and the deployment, it may be useful to run a few sanity checks:

1. Use [snap-samples.sh](RecordingToolsCatalogue.md#snap-samplessh) to collect a
   few REST samples from each relevant type and configuration of LSEG component:
   adh, ads, etc. Upon completion the command will print the location where the
   samples were collected to both stdout and stderr, collect the stdout for
   further use:

    ```bash
    samples_dir=`snap-samples.sh -k $HOME/.lmcrec/security-key -z http://lseg1:8180/sharedmem`
    ```

    E.g. output:

    ```text
    snap-samples.sh: 5 sample(s) saved under .../runtime/lmcrec/samples/lseg1:8180/sharedmem/2025-12-09T23:19:05+0000
    ```

1. Make that location the current directory:

    ```bash
    cd $samples_dir
    ```

1. Run a basic validation of the response(s) using
   [lmcrec-check-response](PlaybackToolsCatalogue.md#lmcrec-check-response):

    ```bash
    lmcrec-check-response response-body.*
    ```

    The check may raise some warnings, for instance `ADH 3.8` has duplicate variables:

    ```text
    *******************
    * response-body.1 *
    *******************

    Duplicate Variables (they should be avoided at playback)
    ========================================================

    Class           Variable(s)    Instance(s)
    --------------  -------------  -------------------------------------------------------------------------------------------------
    DataStreamSrc6  updateRate     lseg1.1.adh.1.sourceThread.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages
                    refreshRate    lseg1.1.adh.1.sourceThread.rrmpConsumer.aggregate.outgoingMessages
                                   lseg1.1.adh.2.sourceThread.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages
                                   lseg1.1.adh.2.sourceThread.rrmpConsumer.aggregate.outgoingMessages
                                   lseg1.1.adh.3.sourceThread.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages
                                   lseg1.1.adh.3.sourceThread.rrmpConsumer.aggregate.outgoingMessages
                                   lseg1.1.adh.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages
                                   lseg1.1.adh.rrmpConsumer.aggregate.outgoingMessages
    --------------  -------------  -------------------------------------------------------------------------------------------------

    Totals
    ======

    Tally               Total
    ----------------  -------
    Inst                  246
    Var                  5012
    Duplicate Inst          0
    Inconsistent Var        0
    Duplicate Var          16
    ```

    `ADS 3.8` comes out clean.

    To inspect one or more responses inflate them (if the reply was compressed)
    with [lmcrec-inflate](PlaybackToolsCatalogue.md#lmcrec-inflate) and pipe the
    result through `jq` to convert single line `JSON` into multiline line one:

    ```bash
    mkdir json
    lmcrec-inflate response-body.1 | jq > json/response-body.1.json
    ```

    Indeed `json/response-body.1.json` shows the duplicated variables:

    ```json
        {
            "Instance": "lseg1.1.adh.1.sourceThread.rrmpConsumer.DF_LEV_ONE.261.outgoingMessages",
            "Class": "DataStreamSrc6",
            "Variables": [
                {
                    "Name": "updateRate",
                    "Type": "Numeric",
                    "Value": 0
                },
                {
                    "Name": "refreshRate",
                    "Type": "Numeric",
                    "Value": 0
                },
                ...
                {
                    "Name": "updateRate",
                    "Type": "Numeric",
                    "Value": 10
                },
                {
                    "Name": "refreshRate",
                    "Type": "Numeric",
                    "Value": 0
                },                       
            ]
        },
    ```

    In case of repeated variables the recorder will use the last one, so if that
    happens to be populated (as seen above) then it may be usable, but it should
    be considered unreliable.

1. Use [lmcrec-from-samples](RecordingToolsCatalogue.md#lmcrec-from-samples) to
   generate a record file out of the samples and verify that the latter is
   consistent with the former via
   [lmcrec-check-consistency](PlaybackToolsCatalogue.md#lmcrec-check-consistency):

    ```bash
    lmcrec-from-samples .
    ```

    Sample output:

    ```text
    time="2025-12-10T00:11:16Z" level=info comp=recorder file="recorder/recorder.go:361" inst=sampleLmcrec msg="URL="
    ...
    time="2025-12-10T00:11:16Z" level=info comp=recorder file="recorder/recorder.go:384" inst=sampleLmcrec msg="record_files_dir=."
    time="2025-12-10T00:11:16Z" level=info comp=recorder file="recorder/recorder.go:390" inst=sampleLmcrec msg="compression_level=-1 (default compression)"
    time="2025-12-10T00:11:16Z" level=info comp=recorder file="recorder/recorder.go:307" inst=sampleLmcrec msg="samples.lmcrec.gz opened"
    time="2025-12-10T00:11:16Z" level=info comp=recorder file="recorder/sample_recorder.go:211" inst=sampleLmcrec msg="Force checkpoint at sample# 3, file response-body.3"
    samples.lmcrec.gz created
    ```

    ```bash
    lmcrec-check-consistency .
    ```

    Sample output:

    ```text
    Using recorder file 'samples.lmcrec.gz'

    Load sample#1 from 'response-body.1'
    Apply next scan to the state cache
    Check consistency
    OK

    ...

    Load sample#5 from 'response-body.5'
    Apply next scan to the state cache
    Check consistency
    OK

    All OK
    ```

## Configuration

The configuration file is in [YAML](https://yaml.org/spec/1.2.2/) format. The
reason for the choice is that, unlike [JSON](https://www.json.org/json-en.html),
it supports comment sections. For people who like JSON better, YAML parsers
support the latter too, in a more relaxed form.
`lmcrec-linux-amd64/reference/config` provides config primers in both formats
(see source under [reference/config](../reference/config)). It is recommended to
keep the `.yaml` suffix because syntax aware editors, upon opening a `.json`
file, will assume the stricter JSON syntax and they will flag constructs that
the YAML parser supports.

To start at configuration file, e.g. `lmcrec-config.yaml`, prime it from
`lmcrec-reference.yaml` file under `lmcrec-linux-amd64/reference` and add to the
`recorders` section the relevant information: inst (see
[Instances](Internals.md#instances)) and URL. If needed, add the security key
file as well (env var supported). e.g.

```yaml
# The default section provides values applicable to all recorders, unless
# specified in the the specific section:
default:
...
# SecurityKey for authentication. It may take one the following forms:
#
#   "file:FILE_PATH": it will be read from FILE_PATH. The path may contain <ID> 
#                     placeholder, which will be replaced with the actual ID
#                     and $ENV_VAR's which will be expanded
#                     e.g. file:$HOME/.lmcrec/security-key
#
#      "env:ENV_VAR": it will be read from environment ENV_VAR
#
#     "SECURITY_KEY": verbatim, not recommended since the config
#                     is most likely publicly readable
security_key: "file:$LMCREC_SECURITY_KEY_FILE"
...
# The next section describes parameters for specific recorders. All the
# parameters from the default section may also appear here in order to override
# their values on a per recorder basis. The INST is matched against the command
# line argument passed via -inst INST option. Typically only `inst' and `url'
# should be specified in the next section.
recorders:
- inst: lseg1.1.adh
  url: http://lseg1:8180/sharedmem
- inst: lseg2.1.ads
  url: http://lseg2:8080/sharedmem
```

## Deployment

### Environment Variables

| Name | Role | Obs |
| ---- | ---- | --- |
| LMCREC_RUNTIME | The root directory for all runtime generated files: recordings, logs, reports | If not defined then $HOME/runtime/lmcrec is used |
| LMCREC_CONFIG | The full path of the config file | Used if no `-config CONFIG_FILE` command line arg is provided |
| LMCREC_SECURITY_KEY_FILE | The full path of the security key file | Need only if referred as such in the config file |

### lmcrec Handling Scripts

They are all located under `lmcrec-linux-amd64/scripts` which should be part of `PATH`. All scripts expect the [instance](Internals.md#instances) `INST` as the first argument (no `-inst` required); the rest of the arguments are passed verbatim to [lmcrec](RecordingToolsCatalogue.md#lmcrec).

| Script         | Role                                                                         | Example                    |
| -------------- | ---------------------------------------------------------------------------- | -------------------------- |
| start-lmcrec   | Start lmcrec in the background, unless already running                       | `start-lmcrec lseg1.1.adh` |
| run-lmcrec     | Run lmcrec in the foreground, unless already running                         | `run-lmcrec lseg2.1.ads`   |
| stop-lmcrec    | Stop lmcrec if running: send `TERM` signal and wait for the  process to exit | `stop-lmcrec lseg1.1.adh`  |
| flush-lmcrec   | lmcrec may use buffering and compression; as such new records are not<br>immediately written to disk. This script sends `USR1` signal to lmcrec to force<br>an immediate flush instead of waiting for the configured, periodic one. This may<br>be need in order to playback very recent data | `flush-lmcrec lseg2.1.ads` |
| rollover-lmcrec | lmcrec may (and should) be configured to periodically start a new recording<br>file. This script sends `USR2` signal to lmcrec to force an immediate rollover<br>to a new file. This may be useful if the current file needs to sent right away<br>to a 3rd party | `rollover-lmcrec lseg1.1.adh` |

### Runtime Directory Structure

If the configuration file follows the reference file, all the runtime files will
placed under subdirectories of `$LMCREC_RUNTIME` (if the latter is not set, it
will default to `$HOME/runtime/lmcrec`). The subdirectories will be created on the
fly, as needed. Playback commands too will use `$LMCREC_RUNTIME` as a root
directory by default. The general structure of a subdirectory path is:
`CATEGORY/INST/TIMESTAMP_OR_TIME_WINDOW`, where timestamp or time window use ISO
8601: `YYYY-MM-DDTHH:MM:SS±HH:MM`

```text

$LMCREC_RUNTIME
    |
    +- log/INST/lmcrec.log
    |
    +- out/INST/lmcrec.{out, err}
    |
    +- rec/INST/YYYY-MM-DD/HH:MM:SS±HH:MM.lmcrec[.gz]
    |                      HH:MM:SS±HH:MM.lmcrec[.gz].index
    |                      HH:MM:SS±HH:MM.lmcrec[.gz].info
    |                     
    + inventory/INST/YYYY-MM-DDTHH:MM:SS±HH:MM--YYY-MM-DDTHH:MM:SS±HH:MM/inventory.txt
    |                                                                    lmcrec-schema.yaml
    |
    + samples/INST/HOST:PORT/YYYY-MM-DDTHH:MM:SS±HHMM/response-body.N
    |                                                 response-header.N
    |
    + query/INST/YYYY-MM-DDTHH:MM:SS±HH:MM--YYY-MM-DDTHH:MM:SS±HH:MM/QUERY_NAME/
    |
    + export/INST/YYYY-MM-DDTHH:MM:SS±HH:MM--YYY-MM-DDTHH:MM:SS±HH:MM
    |
    + report/INST/ORG--COMP--YYYY-MM-DDTHH:MM:SS±HH:MM--YYY-MM-DDTHH:MM:SS±HH:MM.tgz
```
