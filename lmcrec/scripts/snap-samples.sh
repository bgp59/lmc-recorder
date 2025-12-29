#! /bin/bash --noprofile

this_script=${0##*/}

security_key_file=
n_samples=5
interval=5
if [[ -z "$LMCREC_RUNTIME" ]]; then
    export LMCREC_RUNTIME="$HOME/runtime/lmcrec"
fi
output_dir_root="$LMCREC_RUNTIME/samples"
compressed="no"
url=

request_headers_file="request-headers"
response_headers_file="response-headers"
response_body_file="response-body"

usage="
Usage: $this_script [-k SECURITY_KEY_FILE] [-n N_SAMPLES] [-i INTERVAL] [-o OUT_DIR] [-z] URL

Collect N_SAMPLES from URL and store them under OUT_DIR/TIMESTAMP dir.

Args:
    -k SECURITY_KEY_FILE
        Read security from this file, empty if no security key is needed. 
        Default: \`$security_key_file'

    -n N_SAMPLES
        The number of samples to collect. Default: $n_samples

    -i INTERVAL
        The interval, in seconds, between samples. Default: $interval

    -o OUTPUT_DIR_ROOT
        Output dir root; the samples will placed under
            OUTPUT_DIR_ROOT/HOST:PORT/PATH/YYYY-MM-DDTHH:MM:SS±HHMM
        directory. HOST:PORT/PATH is derived from the URL
        http[s]://HOST:PORT/PATH with the http[s]:// removed. The full
        path of the actual dir will be displayed to stdout at the end
        of the run and it is recommended to capture it in a shell variable

            samples_dir=\`$this_script ARGS...\`
        
        Each response will create 2 files, OUT_DIR/$response_body_file.K
        and OUT_DIR/$response_headers_file.K where K=1..N_SAMPLES.
        Default: \`$output_dir_root'

    -z
        Request compressed data (deflate). Default: $compressed

    URL
        The URL for the request, mandatory
"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--h*) echo >&2 "$usage"; exit 1;;
        -k) shift; security_key_file="$1";;
        -n) shift; n_samples=$1;;
        -i) shift; interval=$1;;
        -o) shift; output_dir_root=$1;;
        -z) compressed=yes;;
        *) url="$1";;
    esac
    shift
done

if [[ -z "$url" ]]; then
    echo >&2 "$usage"
    echo >&2 "$this_script: missing mandatory URL"
    exit 1
fi

set -e

if [[ -n "$security_key_file" ]]; then
    security_key=$(cat $security_key_file)
else
    security_key=
fi

samples_dir=$output_dir_root/$(echo "$url" | sed -e 's|http[s]*://||' -e 's|/*$||')/$(date +%Y-%m-%dT%H:%M:%S%z)

mkdir -p $samples_dir
cd $samples_dir

# Prevent unauthorized access to the request header file  while the script is
# running since it may contain the secret key:
touch $request_headers_file
chmod 0600 $request_headers_file
(
    if [[ -n "$security_key" ]]; then echo "Security-Key: $security_key"; fi
    if [[ "$compressed" == "yes" ]]; then echo "Accept-Encoding: deflate"; fi
) >> $request_headers_file

# Remove the request header file upon exit since it may contain the secret key:
trap "rm -rf $request_headers_file" 0 INT TERM

k=0
for ((i=1; i<=$n_samples; i++)); do
    if [[ $i -gt 1 ]]; then (set -x; exec sleep $interval); fi
    (set -x; exec curl -k -s -S -H @$request_headers_file -D $response_headers_file.$i -o $response_body_file.$i $url)
    chmod -w $response_headers_file.$i $response_body_file.$i # to prevent accidental alteration
    k=$(($k + 1))
done

echo $samples_dir # to be captured in samples_dir=`...`
echo >&2 "$this_script: $k sample(s) saved under $samples_dir" # info


