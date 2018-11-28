#!/bin/bash

hilite () {
  sed -e 's|\[.\]:\?|'"\x1b[34m"'&'"\x1b[0m"'|g' \
      -e 's|`'"[^']*'|\x1b[36m"'&'"\x1b[0m"'|g' \
      -e 's|^Usage:|'"\x1b[1m"'&'"\x1b[0m"'|g' \
      -e 's|^Requires:|'"\x1b[1m"'&'"\x1b[0m"'|g' \
      -e 's|:\([A-Z_]\{2,\}\):|'"\x1b[1m"'\1'"\x1b[0m"'|g'
}

## If invoked with no parameters, or `-h', show the help
if [ -z "$1" ]; then
  echo "Usage: $(basename $0) INFILE [OUTFILE]" | hilite
  exit 1
elif [ "$1" = "-h" ]; then
  echo "Usage: $(basename $0) :INFILE: [:OUTFILE:]" | hilite
  echo "Requires: jq" | hilite
  cat <<'EOM' | fmt -w $COLUMNS | hilite

  Converts a JSON reddit dump (as created by my reddit backup
  script[1]) to a JSON lines file, sorted by `created_utc'.
  
  [1]: Basically, unsorted `ID': `comment data' dictionary
EOM
  exit 0
fi

## Grab the parameters
in_file="${1}"
out_file="${2}"

## If OUTFILE is absent, generate it from INFILE
if [ -z "${2}" ]; then
  out_file="${in_file%%.json}.jl"
fi

## Make the dictionary into an array and sort it
# HACK: this is a fairly ridiculous way to go about it, but it works
jq -c '[.[] | values] | sort_by(.created) | reverse | .[]' \
  "${in_file}" > "${out_file}"
