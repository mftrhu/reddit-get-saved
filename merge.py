#!/usr/bin/env python3
# merge.py -- merge json lines files, keeping the order of the objects
# and dropping duplicates based on the `id` property
# Usage: merge.py FILE...
import fileinput, json

if __name__ == "__main__":
    ids = set()
    for line in fileinput.input():
        obj = json.loads(line)
        if obj["id"] not in ids:
            ids.add(obj["id"])
            print(line, end="")
        else:
            continue
