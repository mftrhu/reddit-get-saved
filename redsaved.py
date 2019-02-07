#!/usr/bin/env python3
import urllib.request, time, json, sys, os

FEED_URL = "https://www.reddit.com/user/{user}/saved.json?feed={feed}&user={user}&after={after}"
MAX_SAVED = int(os.environ.get("MAX_SAVED", 1000))
DELAY = int(os.environ.get("DELAY", 2))
HEADERS = {
    "User-Agent": "linux:get-saved-comments:0.1.0 (by /u/mftrhu)"
}

# Load configuration file w. secret data
try:
    with open("config.json", "r") as config_file:
        user_data = json.load(config_file)
except FileNotFoundError:
    print("Error: no config.json file found", file=sys.stderr)
    sys.exit(2)

after, saved = "null", 0
while saved < MAX_SAVED:
    print("Getting next chunk...", file=sys.stderr)
    # This might be frail
    r = urllib.request.Request(url=FEED_URL.format(after=after, **user_data))
    for k, v in HEADERS.items():
        r.add_header(k, v)
    with urllib.request.urlopen(r) as response:
        data = response.read()
        j = json.loads(data.decode())
    # 429 means we made too many requests - wait it out
    if j.get("error") == 429:
        print("Warning: Downloader rate-limited for the next {} seconds".format(
            r.headers["X-Ratelimit-Reset"]), file=sys.stderr)
        time.sleep(float(r.headers["X-Ratelimit-Reset"]))
    # We have our items; do something with them
    for item in j["data"]["children"]:
        print(json.dumps(item["data"]))
        saved += 1
    # Get ready to get the next batch
    after = j["data"]["after"]
    if saved < MAX_SAVED:
        time.sleep(DELAY)
