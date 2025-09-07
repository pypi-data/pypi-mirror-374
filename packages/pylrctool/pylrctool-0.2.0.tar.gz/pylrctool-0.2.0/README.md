# pyLRCtool

Library to create and modify lrc files.

# Functionality

- parse lrc files and modify them
- create new lrc files
- export to srt file
- import from srt file
- add delay

# Installation

```
git clone https://github.com/varyg1001/pylrctool
cd pylrctool
pip install .
```

# Library usage

```py
from pathlib import Path

import pendulum
from pylrctool import LRCEvent, LRCFile

lrc_file = LRCFile()

file = Path('test.lrc')
file2 = Path('test.srt')

# Both statements below are equivalent
lrc_file.from_file(file)
lrc_file.from_string(file.read_text())
lrc_file.from_srt(file2)

# add new events
event = LRCEvent(
    time=pendulum.duration(minutes=0, seconds=29, milliseconds=130),
    data="And I ain't gon' kill my vibe",
)
lrc_file.add(event)

# other event types
title = LRCEvent(data="Don't Be Afraid", type=LRCEvent.Type.Title)
author = LRCEvent(data="Azahriah / BLANKS", type=LRCEvent.Type.Author)
length = LRCEvent(data="02:52", type=LRCEvent.Type.Length)
lrc_file.add(title)
lrc_file.add(author)
lrc_file.add(author)

# shift with 1 minute
lrc_file.shift(minutes=1)

# merge lines to create repeat ie. [00:35.06][00:36.06]Don't be afraid
lrc_file.merge_lines()

# saved to out.lrc
output = Path('out.lrc')
lrc_file.dump(output)

# saved to out.scr
output = Path('out.src')
lrc_file.dump_to_srt(output)

# dumps lyrics only
lrc_file.dumps(data_only=True)
```
