#!/bin/bash

# Script for displaying the Olson timezone on Linux (see:
# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones). 
#
# Based on:
# https://unix.stackexchange.com/questions/451705/get-current-timezone-as-region-city/451925#451925


# Display user's setting, if any:
if [[ "${TZ+x}" == "x" ]]; then
    echo "TZ=$TZ"
else
    echo "TZ not set"
fi

# Assume that /etc/localtime is a symlink to a ../zoneinfo.*/Canonical/Name:
filename=$(readlink -f /etc/localtime)
if [[ "$filename" != "/etc/localtime" ]]; then
    timezone=${filename#*zoneinfo*/}
    if [[ $timezone != "$filename" && ( \
            $timezone =~ ^[^/]+/[^/]+$ || $timezone =~ ^GMT ) ]]; then
        echo "System timezone: $timezone"
        exit 0
    fi
fi

# Next compare files by contents:
timezones=$(
    find /usr/share/zoneinfo/ \
        -type f \
        '!' -regex ".*/Etc/.*" \
        -exec cmp -s '{}' /etc/localtime ';' -print \
        | sed -e 's@.*/zoneinfo/@@' | sort -u
)
if [[ -n "$timezones" ]]; then
    echo "Matching system timezone(s):"
    echo "$timezones"
    exit 0
fi

# Fallback, it may be inferred from the UTC offset and abbreviation below:
(
    unset TZ # to pick up the OS timezone, not user's, if any
    date +"date: %z %Z"
)