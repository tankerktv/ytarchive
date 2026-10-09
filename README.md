<img src="assets/logo.svg" width="96" align="right" alt="ytarchive logo: a video resting in a tray">

# ytarchive

Keeps a personal archive of YouTube channels: watches a list of channels and
fetches everything new on its own. Close the window, reboot the machine — it
carries on.

Written after a plain `yt-dlp` script stalled two nights in a row and once ate
all the memory. Most of the decisions below come from that.

## What it does

* Walks a list of channels and downloads whatever is not in the archive yet.
* **Cannot hang forever.** A silent `yt-dlp` is killed together with its
  children. A stall is detected by silence, not by duration — a two-hour video
  is not a stall.
* **One video cannot hold up the rest.** A download that keeps talking but
  stays below a speed threshold for ten minutes is stopped and deferred to the
  next pass; what was downloaded is kept. When everything is slow, the program
  concludes it is the connection and stops deferring.
* **Calls for you by itself.** Expired cookies or an outdated yt-dlp come as a
  tray notification, not as a line in a window that is minimised.
* **Explains refusals in words.** “Cookies expired”, “yt-dlp is outdated”,
  “network failure” — instead of an exit code. A failure common to every
  channel is reported once, not repeated per channel.
* **A window**: what is downloading right now, how fast, progress bars per
  channel and per video, a live log, a tray icon.
* **Per-video choice**: every channel has a list with checkboxes, title search,
  thumbnails and a preview. Everything is checked by default — you uncheck what
  you do not want rather than picking what you do.
* **Five languages**, window and log alike: English, Russian, German, Spanish,
  French. The system language is used by default; changing it takes effect
  immediately.
* **Per-channel rules**: no shorter, no longer, no older — one line instead
  of a hundred checkboxes. A source can also be a playlist or a single video.
* **Working hours and a speed limit**, so the downloader does not share the
  line with the rest of the house during the day.
* **Cookies from the browser** instead of a file exported by hand.
* **Looks after itself**: removes old logs, shows useless download leftovers,
  checks its record against the files on disk and updates yt-dlp.
* **A library**: everything downloaded, across all channels — searchable,
  sortable by date and size, with the description and one-click playback.
* **Knows what is gone from YouTube.** A video in the archive that has
  disappeared from its channel’s list is marked; that is what an archive is for.
* **Prepares the archive for a media server**: `.nfo` files that make
  Jellyfin, Kodi and Plex show a channel as a series.
* **Estimates disk space up front.** `plan` shows what a channel will take
  before anything is downloaded.

## Installing

You need Python 3.10 or newer. Download the program, then run the installer
from its folder:

```bash
install.cmd        # Windows — or just double-click it
./install.sh       # Linux, macOS
```

It shows what it is going to do and asks before doing it: a Python
environment inside the program folder, `yt-dlp` and the window in it, a
shortcut, and autostart at login. It needs no administrator rights.
`python install.py --dry-run` shows the steps without changing anything.

Two things it cannot install through Python are `node` (without it YouTube
serves storyboards instead of the video) and `ffmpeg`; it tells you how to
get them.

On the first run the program asks for the interface language and the folder
to keep the archive in, then writes the settings itself.

**[INSTALL.md](INSTALL.md) walks through all of it step by step** —
including the YouTube cookies the program needs and what to do when
something goes wrong. По-русски: [INSTALL.ru.md](INSTALL.ru.md).

The window is optional: `--no-gui` installs only the command line and the
background downloader, without Qt.

## Usage

```bash
python ytarchive.py plan      # what would be downloaded and how big, changing nothing
python ytarchive.py check     # reach the channels, downloading nothing
python ytarchive.py run       # one pass and exit
python ytarchive.py daemon    # download continuously, on its own schedule
python ytarchive.py stop      # ask the running copy to stop
python ytarchive.py verify    # check the record against the files on disk
python ytarchive.py clean     # show what old files can be removed
python ytarchive.py update    # update yt-dlp
python ytarchive.py nfo       # description files for a media server
python ytarchive.py gui       # the window
```

`verify` and `clean` only show things unless given `--apply`. `clean --apply`
removes old logs and download leftovers that are no longer useful; a fresh
leftover of a video not yet downloaded is left alone — that is a download to
be resumed. `verify --apply` removes only duplicate lines from the record and
keeps the previous file next to it; a video without a file, or a file without
a record, is reported and left for you to decide.

A command that changes data has its own name rather than a flag on an ordinary
one: `plan` never downloads, whatever you pass it.

### Continuous work

`daemon` runs passes by itself and picks the pause from how a pass ended:
something was downloaded — come back in a minute; nothing new — half an hour;
a human is needed — an hour. No task scheduler is involved.

Two copies will not start: the lock will not let them. A stop request reaches
`yt-dlp` itself rather than the end of the current channel — a channel can hold
six hundred videos.

Working hours (`[schedule] hours = "23-7"`) are kept by `daemon` too:
outside them it waits, and a download in progress is interrupted — it resumes
from the same place. A one-off `run` ignores the hours: a person started it
and knows what time it is.

### The channel list

`_tools/channels.txt`, one source per line:

```
Name|address|rules
```

The name is the folder. The address is a channel’s `videos` tab, a playlist
or a single video. Using the `videos` tab is also how Shorts and live streams
are left out: they have tabs of their own.

Rules are optional: `min=60;max=7200;after=2024-01-01` — no shorter and no
longer than that many seconds, no older than the date. A rule takes videos
out of the queue and deletes nothing; a video with an unknown duration or
date is not affected. The date in a listing is approximate — YouTube says
“3 years ago”.

## Settings

Everything lives in `ytarchive.toml`, with typo checking: an unknown key is
named rather than silently ignored.

| Section | About |
|---|---|
| `[paths]` | archive, channel list, cookies, logs, unchecked videos |
| `[download]` | quality, AV1, subtitles, cookies from a browser, speed limit |
| `[limits]` | silence limit, pauses between videos, slow-download threshold, how long logs are kept |
| `[schedule]` | pauses between passes, working hours |
| `[interface]` | window language |

The silence limit must be noticeably larger than the pause between videos, or
the watchdog will kill a healthy download. This is checked when the settings
are read, not discovered at night.

## Design

```
core/     decisions: not a single import of Qt, yt-dlp or anything else
runner/   execution: processes, locks, the download session
app/      command line
gui/      the window on PySide6 — a thin shell over core
```

**All the meaningful logic lives in `core`.** There is not one framework import
there, so it is tested with bare `pytest` in a fraction of a second — which is
why the tests are run on every save. If a shell grows an `if` with a meaningful
condition, that `if` belongs in the core.

The window does not download. A separate process does; the window only watches
and can start it or ask it to stop. Otherwise two copies would fight over the
lock and the archive file, and closing the window would cut the download short.

## Platforms

Verified on Windows and on Debian (tests, window, command line). macOS is
untested — the code is portable and there is every reason to expect it to work,
but expectation is not verification.

The installer has been run on Windows and Debian; its macOS steps are untested.

Known limits: the `.nfo` files follow Kodi’s conventions and have not been
tried against a live media server. “Not in the channel’s list” means exactly
that, not “deleted”: a video sitting on another tab of the channel (Shorts,
live streams) is marked the same way. The trouble notification comes from the tray icon, so a
downloader started without the window can only write to the log. yt-dlp is
updated by the program only when the program installed it; a copy installed
some other way is asked to update itself, and its answer is shown as is.

## Development

```bash
.venv/bin/python -m pytest -q            # everything
.venv/bin/python -m pytest -q -m "not slow"   # core only, no real processes
```

Comments and docstrings are in Russian: the project is maintained by a Russian
speaker, and a comment explaining *why* is worth more in the author's own
language than a translated one. Identifiers and this file are in English.

## Licence

MIT.
