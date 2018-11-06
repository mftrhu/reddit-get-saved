# reddit-get-saved

> An unimaginatively named set of Python scripts to download *and* visualize one's Reddit saved items

## Usage

**First run:**

```
$ ./redsaved.py > saved.jsonl
```

**Subsequent runs:**

```
$ MAX_SAVED=100 ./redsaved.py > $(date +"%Y-%m-%d").jsonl
$ ./merge.py $(date +"%Y-%m-%d").jsonl saved.jsonl | sponge saved.jsonl
```

### `redsaved.py`

`redsaved` takes care of downloading the items in your saved list.  As it uses Reddit's private user feeds, it doesn't need to be authenticated, but it needs the hash for your JSON private feed: it can be found under Preferences/RSS feeds.

Put your username and hash inside a `config.json` file in the folder from where you'll launch the script:

```json
{
    "user": "<YOUR USERNAME HERE>",
    "feed": "<JSON SAVED LINKS HASH>"
}
```

`redsaved` will, by default, try to download all your saved items, but this can be changed by setting the `MAX_SAVED` environment variable while calling it.  It will output them to standard output, in JSON lines format.

### `merge.py`

**Usage:** `merge.py FILE...`

`merge.py` merges files in JSON lines format, keeping the order and dropping duplicates based on the `id` property of each object.
