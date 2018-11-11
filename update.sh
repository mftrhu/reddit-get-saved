#!/bin/bash
## User variables
saved_filename="saved.jsonl" # Where to put the items
backup_old=true # Are we to backup the old items before merging?

## "Internal" variables
# There should be no particular need to modify these
new_filename="$(date +"%Y-%m-%d").jsonl" # Where to put the new items
max_save="${MAX_SAVED:-100}" # How many items to get, default 100

## Grab all the items from our saved JSON feed
# We'll take care of removing duplicates in a later step
printf "** Downloading items...\n" >&2
if [ -r "${saved_filename}" ]; then
  ## Ensure that the newly downloaded items will be removed on exit
  trap 'rm "${new_filename}"' EXIT
  MAX_SAVED="${max_save}" ./redsaved.py > "${new_filename}"
else
  ## No old saved items; this is a fresh download
  MAX_SAVED="${max_save}" ./redsaved.py > "${saved_filename}"
  printf "** Done.\n" >&2
  exit 0
fi

## Make a "backup" of our old saved posts
if "${backup_old}"; then
  printf "** Backing up ${saved_filename}\n" >&2
  cp -f "${saved_filename}" "${saved_filename}.old"
fi

## Merge the newly downloaded saved items with the old ones
printf "** Merging items...\n" >&2
./merge.py "${new_filename}" "${saved_filename}" | sponge "${saved_filename}"

printf "** Done.\n" >&2
