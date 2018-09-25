#!/usr/bin/env python3
import curses, textwrap, fileinput, json
import webbrowser, subprocess, string, locale

"""
Bunch of todos:
- [ ] Modify this to use Urwid/a decent widget library OR
      - [ ] Create my own widget library
            - TableWidget
            - ScrollableText
              - ScrollableANSIText
                Will require a simple ANSI escape sequences parser and converter to
                ncurses/Urwid colorpairs.
            - MessageBox
            - InputBox
            - Widgets, once created, could register keybindings to the main window
- [ ] Configurable keybindings/Vim keys
- [ ] Filter by, freeform on body text, title, username, subreddit, tags
- [ ] Filter by subreddit/user/time lapse/tags
- [ ] Write back to file (s for save, maybe)
- [ ] Archive item (shunt it to an archive file and remove it from the main one)
- [ ] Tag item
- [ ] Help window
- [ ] d(ownload|ump): downloads linked image/whatnot *or* dumps text to selected file
- [ ] Better markdown wrapper
      - Chomp lines in code blocks to max length
- [ ] Interface with an offline RES-alike (tagger, upvote counter) - maybe abook - to
      provide information about the user who wrote the current comment
      This could be bound to... [u], maybe, to show comments in collection, tag, upvotes,
      and to allow one to add/change the usertag.
- [ ] 
"""

def count(string, char, skip_whitespace=False, return_offset=False):
    i, result = 0, 0
    for i, c in enumerate(string):
        if skip_whitespace and c.isspace():
            continue
        if c in char:
            result += 1
        else:
            break
    if return_offset:
        return result, i
    return result

def md_wrap(text, width=70):
    text = text.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    lines = []
    for paragraph in text.split("\n\n"):
        if paragraph.startswith("    "):
            lines.extend(paragraph.split("\n"))
        elif paragraph.startswith(">"):
            items = paragraph.split("\n")
            for item in items:
                level, offset = count(item, ">", True, True)
                if offset < level:
                    lines.append(">" * level)
                offset = max(level, offset)
                for line in textwrap.wrap(item[offset:], width - level - 1):
                    lines.append(">" * level + " " + line)
        elif paragraph.startswith("- ") or paragraph.startswith("-\t"):
            items = paragraph.split("\n")
            for item in items:
                level, offset = count(item, "-", True, True)
                for i, line in enumerate(textwrap.wrap(
                        item[offset:], width - level*2 - 1)):
                    lines.append("  " * (level-1) + ("  ", "- ")[i == 0] + line)
                #lines.extend(textwrap.wrap(item, width))
        else:
            lines.extend(textwrap.wrap(paragraph, width))
        lines.append("")
    return lines

def img2text(url, width):
    import requests
    r = requests.get(url, stream=True)
    i = r.raw.read(-1)
    p = subprocess.Popen(["img2ansi", "-width", str(width)],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    try:
        o, e = p.communicate(i, timeout=2)
        # Blah.  Doesn't work.  img2ansi returns ANSI escape sequences, but curses
        # is already handling those and just ignores them.
        # To parse them out:
        #     \e[48;5;XXXm sets the background to XXX
        #     \e[38;5;XXXm sets the foreground to XXX
        return o.decode('cp437').splitlines()
    except subprocess.TimeoutExpired:
        p.kill()
        outs, errs = p.communicate()

def bind(value, start, end):
    return max(start, min(value, end))

class Interface(object):
    def __init__(self, stdscr, data):
        curses.use_default_colors()
        if curses.has_colors():
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
            curses.init_pair(2, 0, curses.COLOR_GREEN)
            curses.init_pair(3, curses.COLOR_BLUE, -1)
        self.data = data
        self.filter = None
        self.stdscr = stdscr
        self.Y, self.X = stdscr.getmaxyx()
        self.title  = curses.newwin(2, self.X, 0, 0)
        self.main   = curses.newwin(self.Y-2, self.X, 2, 0)
        curses.curs_set(0)
        self.show()

    def get_data(self):
        if self.filter is None:
            return self.data
        new_list = []
        for item in self.data:
            if any((type(v) is str and self.filter in v) for v in item.values()):
                new_list.append(item)
        return new_list
        return list(filter(
            lambda i: (print(i), any(self.filter in v for v in i.values()))[1],
            self.data))

    def refresh(self):
        self.stdscr.refresh()
        self.title.refresh()
        self.main.refresh()

    def show(self):
        cursor = 0
        while True:
            data = self.get_data()
            if self.filter is None:
                self.display_title(right="{}/{}".format(cursor+1, len(data)))
            else:
                self.display_title(right="[{}] {}/{}".format(
                    self.filter, cursor+1, len(data)
                ))
            self.display_list(cursor)
            self.refresh()
            k = self.stdscr.getkey()
            if k == "KEY_UP":
                cursor = (cursor - 1) if cursor > 0 else cursor
            elif k == "KEY_DOWN":
                cursor = (cursor + 1) if cursor < len(data)-1 else cursor
            elif k == "KEY_PPAGE":
                cursor = bind(cursor-(self.Y-3), 0, len(data)-1)
            elif k == "KEY_NPAGE":
                cursor = bind(cursor+(self.Y-3), 0, len(data)-1)
            elif k in ("KEY_ENTER", "\n", "\r"):
                move = self.show_entry(cursor)
                while move is not None:
                    cursor = bind(cursor + move, 0, len(data)-1)
                    move = self.show_entry(cursor)
            elif k == "q":
                break
            elif k == "/":
                if self.filter is None:
                    self.filter = ""
                while True:
                    data = self.get_data()
                    cursor = bind(cursor, 0, len(data)-1)
                    self.display_title(right="[{}] {}/{}".format(
                        self.filter, cursor+1, len(data)
                    ))
                    self.display_list(cursor)
                    self.refresh()
                    k = self.stdscr.getkey()
                    if k in ("KEY_ENTER", "\n", "\r"):
                        break
                    elif k in ("\x1b",):
                        self.filter = None
                        break
                    elif k in ("KEY_BACKSPACE", "KEY_DC"):
                        self.filter = self.filter[:-1]
                        if len(self.filter) < 1:
                            self.filter = None
                            break
                    elif k in string.printable:
                        self.filter += k
                    else:
                        break

    def display_title(self, left="q:quit h:help", right=""):
        self.title.clear()
        self.title.insstr(0, 0, "jsonl-viewer v.0.1.0 | " + left)
        if right:
            self.title.insstr(0, self.X - len(right), right)
        self.title.hline(1, 0, curses.ACS_HLINE, self.X)

    def display_list(self, cursor):
        self.main.clear()
        self.main.attrset(curses.color_pair(1))
        self.main.insstr(0, 0, " " * self.X)
        self.main.insstr(0, 0, "{:58} {:20}".format("Title", "Subreddit"))
        self.main.attrset(0)
        start, end = max(0, cursor-(self.Y-3-1)), max(self.Y-3, cursor+1)
        data = self.get_data()
        for i, item in enumerate(data):
            if not start <= i < end:
                continue
            pos = 1 + i - start
            if i == cursor:
                self.main.attrset(curses.color_pair(2))
            # BUG: this errors somewhere around my 300th comment
            self.main.insstr(pos, 0, " " * self.X)
            title = item.get("title", item.get("link_title"))[:58]
            title = "".join(filter(lambda c: c in string.printable, title))
            sub = item["subreddit"][:17]
            self.main.insstr(pos, 0, "{0:58} /r/{1:17}".format(title, sub))
            self.main.attrset(0)

    def show_entry(self, cursor):
        data = self.get_data()
        entry = data[cursor]
        if "body" in entry:
            lines, line, kind = md_wrap(entry.get("body"), self.X-2), 0, "Comment"
        elif "selftext" in entry:
            lines, line, kind = md_wrap(entry["selftext"], self.X-2), 0, "Self-post"
        #elif "thumbnail" in entry:
        #    lines, line = img2text(entry.get("thumbnail"), self.X-2), 0
        else:
            lines, line, kind = [], 0, "Link"
        while True:
            self.display_title("q:quit h:help o:browse", right="{}/{}".format(cursor+1, len(data)))
            top = self.display_entry(entry)
            #if "body" in entry:
            self.display_text(lines, line, top)
            self.refresh()
            k = self.stdscr.getkey()
            if k == "KEY_UP":
                line = bind(line-1, 0, len(lines)-1)
            elif k == "KEY_DOWN":
                line = bind(line+1, 0, len(lines)-1)
            elif k == "KEY_PPAGE":
                line = bind(line-(self.Y-top-3), 0, len(lines)-1)
            elif k == "KEY_NPAGE":
                line = bind(line+(self.Y-top-3), 0, len(lines)-1)
            elif k in ("KEY_LEFT", "h"):
                return -1
            elif k in ("KEY_RIGHT", "l"):
                return +1
            elif k == "o":
                webbrowser.open_new_tab(entry.get("url", "https://reddit.com/" + entry.get("permalink")))
            elif k == "q":
                return

    def display_entry(self, entry):
        self.main.clear()
        title = entry.get("title", entry.get("link_title"))
        title = "".join(filter(lambda c: c in string.printable, title))
        url = entry.get("url", "https://reddit.com/" + entry.get("permalink"))
        pos = 0
        self.main.attrset(curses.A_BOLD)
        for line in textwrap.wrap(title, self.X-2):
            self.main.insstr(pos, 0, line.center(self.X))
            pos += 1
        link = url
        if len(link) > self.X - 4:
            begin, end = link[:(self.X-8)//2], link[-(self.X-6)//2:]
            link = begin + "..." + end
        self.main.attrset(curses.color_pair(3))
        self.main.insstr(pos, 0, ("<" + link + ">").center(self.X))
        self.main.attrset(0)
        pos += 1
        if "body" in entry:
            kind = "Comment"
        elif "selftext" in entry and entry["selftext"]:
            kind = "Self-post"
        else:
            kind = "Link"
        byline = "{} by /u/{}".format(kind, entry["author"])
        self.main.insstr(pos, self.X - 1 - len(byline), byline)
        return pos + 1

    def display_text(self, lines, line, top):
        start, end = line, line + (self.Y-top-3)
        for i, line in enumerate(lines[start:end]):
            self.main.insstr(top + 1 + i, 1, line)

if __name__ == "__main__":
    data = []
    tail = []
    for line in fileinput.input():
        data.append(json.loads(line))
    locale.setlocale(locale.LC_ALL, "")
    curses.wrapper(Interface, data)
    print("\n".join(tail))
    
