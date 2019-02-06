# reddit-get-saved

> An unimaginatively named set of Python scripts to download *and* visualize one's Reddit saved items

## Screenshots

![List view](screenshots/list_view.png?raw=true)

![Entry view](screenshots/entry_view.png?raw=true)

## Usage

**First run:**

```
$ ./redsaved.py > saved.jsonl
```

**Subsequent runs:**

```
$ MAX_SAVED=100 ./update.sh
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

### `update.sh`

**Usage:** `update.sh`

`update.sh` takes care of invoking `redsaved.py` to download any new saved items to a temporary file, and of calling `merge.py` to merge them with the items that were saved previously.

Its behaviour can be partly configured by modifying its "user variables" section.  It will default to downloading one hundred items per run, but that number can be modified by setting the `MAX_SAVED` environment variable.

### `merge.py`

**Usage:** `merge.py FILE...`

`merge.py` merges files in JSON lines format, keeping the order and dropping duplicates based on the `id` property of each object.

### `viewer.py`

**Usage:** `viewer.py FILE`

`viewer.py` is a curses-based viewer for JSON lines-formatted files.

#### Columns

The columns displayed in the list view can be specified in the config file, in the `columns` object.  It must be a list of objects, each containing a numeric `width`, the `title` of the column, and the `key` to be displayed.

`width` should be the width of the columns, in characters, when the display is a standard 80x25.  The actual width will be calculated against the width of the screen when `viewer.py` is launched.

Each column will be displayed offset by one character from the previous one, so the sum of the `width`s **should not** be equal to 80.

The default configuration is

``` json
"columns": [
    {"width": 58, "title": "Title", "key": "title"},
    {"width": 20, "title": "Subreddit", "key": "subreddit"}
]
```

#### Keybindings

`viewer.py` has two main "modes", with slightly different keybindings: the list view, and the entry view.  The former displays a list of all the items in the JSON lines file, while the latter shows a single entry in detail.

##### List view

- `<up>`: move the cursor one entry up.
- `<down>`: move the cursor one entry down.
- `<page_up>`: move the cursor one screenful of entries up.
- `<page_down>`: move the cursor one screenful of entries down.
- `q`: exit `viewer.py`
- `/`: enter filter mode until `<return>` is pressed.  Only entries containing the entered text in one of their fields will be displayed until the filter is cleared with `<escape>`.
- `<return>`: enter entry view for the currently selected entry.

##### Entry view

- `<up>`: scroll the text of the entry one line up.
- `<down>`: scroll the text of the entry one line down.
- `<page_up>`: scroll the text of the entry one screenful of lines up.
- `<page_down>`: scroll the text of the entry one screenful of lines down.
- `<left>`, `h`: move to the previous entry.
- `<right>`, `l`: move to the next entry.
- `q`: quit entry view.
- `o`: open the permalink of the currently selected entry in the browser.

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
