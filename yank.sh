#!/bin/sh
# Called with "args": ["title", "permalink", "author"]
available () {
  command -v "$1" > /dev/null 2>&1
}
ctrl_c () {
  available xclip && xclip -i -selection clipboard && return $?
  printf "Error: xclip not available, clipping to /tmp\n" >&2
  cat > "/tmp/$USER.clipboard"
}
{
  printf "[%s](%s) (by /u/%s)" \
    "$(echo "$1" | sed -e 's/\[//g' -e 's/\]//g')" \
    "$(echo "$2" | sed -e 's/(/\\(/g' -e 's/)/\\)/g')" \
    "$3"
} | ctrl_c
