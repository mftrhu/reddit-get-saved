#!/bin/sh
# Called with "args": ["title", "author", "permalink", "created_utc", "text"]
available () {
  command -v "$1" > /dev/null 2>&1
}
ctrl_c () {
  available xclip && xclip -i -selection clipboard && return $?
  printf "Error: xclip not available, clipping to /tmp\n" >&2
  cat >"/tmp/$USER.clipboard"
}
{
  printf "* /u/%s on [%s]\n" "$2" "$(date +"%Y-%m-%d %H:%M" --date="@$4")"
  printf ":PROPERTIES:\n"
  printf ":Permalink: %s\n" "$3"
  printf ":END:\n\n"
  pandoc -f markdown -t org --wrap=none <<<"$5"
} | ctrl_c
