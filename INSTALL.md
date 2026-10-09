# Installing ytarchive

For someone setting the program up for the first time. From an empty machine
to the first downloaded video is six steps and about fifteen minutes, ten of
which are downloads that run by themselves.

*Русская версия: [INSTALL.ru.md](INSTALL.ru.md).*

## In short

1. Install Python 3.10 or newer.
2. Download the program.
3. Run the installer: `install.cmd` on Windows, `./install.sh` on Linux and macOS.
4. Install `node` and `ffmpeg` if the installer says they are missing.
5. Provide YouTube cookies.
6. Open the window, add a channel, press “Start”.

The same, in detail, below.

## Step 1. Python

Python **3.10 or newer** is required. To see what you already have:

```bash
python --version
```

On Linux and macOS the command may be called `python3`.

If Python is missing or older:

| System | How to install |
|---|---|
| Windows | `winget install Python.Python.3.12` — or the installer from [python.org](https://www.python.org/downloads/); **tick “Add python.exe to PATH”** in it |
| macOS | `brew install python` — or the installer from python.org |
| Debian, Ubuntu | `sudo apt-get install python3 python3-venv` |
| Fedora | `sudo dnf install python3` |

On Debian and Ubuntu `python3-venv` is a separate package: without it the
installer stops at the very first step and says so.

## Step 2. Download the program

The simplest way is an archive: on
[github.com/tankerktv/ytarchive](https://github.com/tankerktv/ytarchive)
press **Code → Download ZIP** and unpack it where the program is going to live.

Or with git, which makes updating easier later:

```bash
git clone https://github.com/tankerktv/ytarchive.git
```

**Pick the place now.** The program installs into its own folder and the
shortcuts point at it. If you move the folder, run the installer again.

Do not put the program into a folder that syncs to a cloud: the Python
environment inside it is thousands of small files.

## Step 3. The installer

**Windows:** double-click `install.cmd`.

If Windows shows “Windows protected your PC”, that is its reaction to a file
downloaded from the internet. “More info” → “Run anyway”. What the file does
is visible in the file itself: it finds Python and starts `install.py`.

**Linux and macOS:** in a terminal, from the program folder:

```bash
./install.sh
```

The installer:

1. asks whether to create a shortcut and whether to start downloading at login;
2. shows the list of what it is about to do;
3. asks “Go ahead?” — and touches nothing until you agree.

An empty answer accepts the option shown in capitals.

### What exactly it does

| What | Where |
|---|---|
| A Python environment | `.venv` inside the program folder |
| Packages: `yt-dlp`, the window (PySide6) | into that environment, not into the system |
| The “YouTube Archive” shortcut | Windows — desktop; Linux — applications menu; macOS — desktop |
| Autostart of the downloader | Windows — the Startup folder; Linux — `~/.config/autostart`; macOS — `~/Library/LaunchAgents` |

It does not ask for administrator rights and never runs `sudo`. Outside the
program folder it creates only the shortcut and the autostart entry.

### Look without changing anything

```bash
python install.py --dry-run
```

### Options

| Option | Effect |
|---|---|
| `--dry-run` | only show the steps |
| `--yes` | ask no questions |
| `--no-gui` | no window: command line and background downloader only (PySide6 is not installed) |
| `--no-shortcut` | do not create the shortcut |
| `--no-autostart` | do not start downloading at login |

On Windows options are passed like this: `install.cmd --no-autostart`.

## Step 4. node and ffmpeg

These two cannot be installed through Python. The installer checks for them
and:

* on Windows and macOS offers to install them itself (with `winget` or `brew`);
* on Linux prints the command for you to run: it needs `sudo`, and the
  installer does not ask for an administrator password.

| Program | Why | Windows | macOS | Debian, Ubuntu |
|---|---|---|---|---|
| `node` | without it YouTube serves a storyboard instead of the video | `winget install OpenJS.NodeJS.LTS` | `brew install node` | `sudo apt-get install nodejs` |
| `ffmpeg` | video and audio arrive separately and need joining | `winget install Gyan.FFmpeg` | `brew install ffmpeg` | `sudo apt-get install ffmpeg` |

Afterwards **open a new terminal** (on Windows, signing out and back in is
the reliable way): windows that were already open will not see the new
programs.

## Step 5. First run and cookies

Open the window — with the “YouTube Archive” shortcut or with:

```bash
.venv/bin/python ytarchive.py gui              # Linux, macOS
.venv\Scripts\pythonw.exe ytarchive.py gui     # Windows
```

The first time, the program asks for the **language** and the **archive
folder** — where the videos will go, one folder per channel. Choose a disk
with room to spare: a single channel is easily hundreds of gigabytes.

### Cookies

YouTube does not serve videos to someone who is not signed in. The program
needs a file with your session — `cookies.txt`:

1. Open a **private window** (incognito) in your browser and sign in to YouTube.
2. In the same tab open `https://www.youtube.com/robots.txt`.
3. Export the cookies for `youtube.com` with an extension that saves them in
   Netscape format — “Get cookies.txt LOCALLY”, for example.
4. **Close the private window** and do not use it again.
5. Save the file as `_tools/cookies.txt` inside the archive folder (create
   `_tools` if it is not there yet).

The private window is not about caution: YouTube keeps rotating the cookies
of an open tab, and cookies exported from an ordinary window soon stop
working.

> **This file is your Google sign-in, in plain text.** Whoever reads it is
> signed in as you. Keep it out of shared folders, cloud storage and backups
> that anyone else can read. The calmest option is a separate account just
> for the archive.

**Or without a file.** The window’s settings have a “YouTube cookies”
field: choose the browser in which you are signed in to YouTube, and the
program takes the cookies straight from it. This works reliably with
Firefox. Chrome and Edge on Windows encrypt their cookies and often cannot
be read — then the file is the way.

When the cookies expire the program says so in words — “cookies expired” —
and waits instead of hammering every channel. If the window is running it also shows a tray
notification. The cure is repeating these five steps.

### Check that everything is in place

```bash
.venv/bin/python ytarchive.py check            # Linux, macOS
.venv\Scripts\python.exe ytarchive.py check    # Windows
```

`check` names what is missing — `node`, `ffmpeg`, cookies — and downloads
nothing. It works after the first run: before that there are no settings.

## Step 6. The first channel

1. The **Channels** tab — find a channel by name. Before adding it you can
   see how many videos it has and how much space they will take.
2. Add the channel. If you do not want every video, open its list and
   uncheck the ones you do not need, or set the selection at once with
   “Rules…”: no shorter, no longer, no older.
   A playlist or a single video is added with “Add by address…”.
3. The **Overview** tab → **Start**.

You can close the window — it hides in the tray and the download carries on.
From then on the program checks the channels by itself: every half an hour
when there is nothing new.

To see what would be downloaded and how big it is, without downloading:

```bash
.venv/bin/python ytarchive.py plan
```

## Telegram notifications

The downloader runs without the window, and without the window there is
nobody to tell about trouble — expired cookies, an outdated yt-dlp. To have
it write to you:

1. In Telegram open `@BotFather`, send `/newbot` and answer two questions.
   You get a **bot token** — a line like `123456:ABC…`.
2. Save the token into a text file — one line, nothing else. Keep the file
   where cloud sync and backups do not look.
3. Send your bot any message: until you write first, a bot cannot write to you.
4. Find out your chat number — `@userinfobot` tells it, for example.
5. In the window’s settings, section “Telegram notifications”, give the token
   file and the chat number, save, and press “Test…”.

A test message arrives. From then on the program writes when it needs you,
and once more when the trouble is over. It reports the same trouble once,
not every hour.

> **The bot token is the right to write in its name.** The program’s settings
> hold only the path to the file; the token itself never gets there and is
> never written to the log. Do not paste the token into a command line or a
> chat: a token seen by someone else gets replaced (`/revoke` at `@BotFather`).

The same from the command line: `ytarchive.py notify`.

## Updating

Put the new version over the old one (or `git pull`) and run the installer
again. It does not touch your settings or the archive.

It is worth running the installer even without a new version — every month
or two, or when the program says “yt-dlp is outdated”: it upgrades `yt-dlp`,
which ages fast because YouTube changes all the time.

```bash
python install.py --yes
```

The “Update yt-dlp” button in the window’s settings and the command
`ytarchive.py update` do the same.

The program uses its own `yt-dlp` — the one the installer put into its
environment — even when another copy is installed system-wide. That other
copy stays yours: the program neither touches nor updates it.

## Uninstalling

1. Stop the downloader: with the button in the window or `ytarchive.py stop`.
2. Delete the shortcut and the autostart entry (the table in step 3 says where).
3. Delete the program folder.

The archive lives elsewhere, and removing the program does not touch it.

## When something goes wrong

| What you see | What it means |
|---|---|
| `install.cmd`: “Python 3.10 or newer was not found” | Python is not installed or not on PATH — step 1; then open the file again |
| The installer stops while creating the environment (Linux) | `python3-venv` is missing — `sudo apt-get install python3-venv` |
| It stops while installing packages | usually no network, or a proxy in the way; run it again — what is done is kept |
| “failed: create the window shortcut” | on Windows with a strict security policy scripts may not create shortcuts; make one by hand to `.venv\Scripts\pythonw.exe` with the arguments `ytarchive.py gui` |
| `check` says “no node” right after installing it | the terminal was opened before the installation — open a new one |
| Storyboard images are downloaded instead of videos | `node` is missing |
| “cookies expired” | step 5, export the cookies again |
| “yt-dlp is outdated” | the “Update yt-dlp” button in the settings, or the installer again |
| The log says “slower than … — deferring” for every video | the connection is slower than the threshold; in the window’s settings set “Defer downloads slower than” to “do not check” |
| The window does not open; the terminal says the window needs PySide6 | it was installed with `--no-gui`; run the installer without that option |

## Without the installer

The installer does nothing you could not do by hand:

```bash
python -m venv .venv
.venv/bin/python -m pip install ".[gui]" "yt-dlp[default]"
.venv/bin/python ytarchive.py gui
```

On Windows use `.venv\Scripts\python.exe` instead of `.venv/bin/python`.

## What has been verified

The installer has been run on Windows 11 and on Debian. **It has not been
run on macOS**: the steps for it follow the documentation and there is every
reason to expect them to work — but expectation is not verification. If
something goes wrong, `--dry-run` shows at which step, and “Without the
installer” gets you around it.
