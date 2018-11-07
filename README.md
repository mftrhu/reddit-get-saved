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

### `viewer.py`

**Usage:** `viewer.py FILE`

`viewer.py` is a curses-based viewer for JSON lines-formatted files.

#### Keybindings

#### Configuration file

`viewer.py` can use a configuration file, loading it either from the current folder (`.viewerrc`) or from `$XDG_CONFIG_HOME/rviewer/viewerrc` (or `~/.config`, if `$XDG_CONFIG_HOME` is unset).  The configuration file must contain JSON data.

##### `keybindings`

The configuration file **may** contain a `keybindings` object, mapping keycodes to actions to be performed by the viewer on the selected entry.

The action should be another object in turn, which **must** contain `cmd` (a string, specifying the command to be called).  It **may** contain either `pipe` (a string) or `args` (a list of strings), specifying keys into the entry to be either piped to `cmd` or passed to `cmd` as arguments.

**E.g.** to pipe the text of the selected entry to `urlview`:

```json
"keybindings": {
    "u": {
        "cmd": "urlview",
        "pipe": "text"
    }
}
```

To use `format-comment.sh` with `title`, `url` and `text` as arguments (besides the `-t org` specified in `cmd`):

```json
"keybindings": {
    "F": {
        "cmd": "format-comment.sh -t org",
        "args": ["title", "url", "text"]
    }
}
```
