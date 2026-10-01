# plexi

A lightweight, keyboard-driven Plex client for the terminal, built for [Omarchy](https://omarchy.org).

Browse your libraries as a tree — **library → show → season → episode** or **library → movie** — and play with `mpv`. Plexi picks up your current Omarchy theme colors and follows along live when you switch themes.

```
╭─ plexi living-room ──────────────────────────────────────────────────────────────────────────╮
│ ▸   Movies                                         148 │                                     │
│ ▾   TV Shows                                        37 │  Severance                          │
│   ▾ ● Severance                        2022 · 1 season │  S01E02 · Half Loop                 │
│     ▾ ● Season 1                                   1/3 │  2022-02-18  ·  TV-MA  ·  50m       │
│            1  Good News About Hell                 57m │                                     │
│▎        ◐  2  Half Loop                       30m left │  ━━━━━━━━━━━━━━━━━━  20:00 / 50:00  │
│         ●  3  In Perpetuity                        50m │                                     │
│                                                        │  Mark navigates the halls.          │
│                                                        │                                     │
│                                                        │  1080p · h264 · aac · 6ch           │
╰─ 6/7 ──────────────────────────────────────────────────────────── ▶ Severance — S01E02 — … ─╯
 j/k move   l open   h back   enter play   p from start   w watched   / find   r reload   q quit
```

- Zero dependencies beyond Python 3.11+ and `mpv`
- Signs in through plex.tv in your browser, finds your server, prefers local connections
- Resumes where you left off and reports progress back to Plex (watched at 90%)
- Unwatched `●` / in-progress `◐` markers, detail pane with summary and media info
- Incremental search across everything you've loaded

## Install

On Omarchy / Arch, from the AUR:

```sh
omarchy pkg aur add plexi
```

Then launch **Plexi** from the app launcher (<kbd>Super</kbd> + <kbd>Space</kbd>), or run `plexi` in a terminal.

Manually, anywhere with Python 3.11+ and mpv:

```sh
curl -Lo ~/.local/bin/plexi https://raw.githubusercontent.com/OWNER/plexi/main/plexi
chmod +x ~/.local/bin/plexi
```

## Usage

```
plexi           browse your libraries (signs in on first run)
plexi login     sign in again / pick another server
plexi logout    forget the saved server and token
```

| Key | Action |
| --- | --- |
| `j` `k` / `↓` `↑` | move |
| `l` / `→` | open / expand |
| `h` / `←` | back / collapse |
| `enter` | play (resumes) or toggle |
| `p` | play from the start |
| `w` | toggle watched |
| `/` then `n` `N` | find, next, previous |
| `r` | reload |
| `g` `G` · `ctrl-d` `ctrl-u` | top, bottom · half page |
| `q` | quit |

## Configuration

Credentials live in `~/.config/plexi/config.toml` (mode `600`). `PLEX_URL` and `PLEX_TOKEN` override them, which is handy for a server you reach directly:

```sh
PLEX_URL=http://192.168.1.10:32400 PLEX_TOKEN=xxxx plexi
```

Colors are read from `~/.local/state/omarchy/current/theme/colors.toml`. Outside Omarchy, plexi falls back to a neutral dark palette.

## Notes

Plexi direct-plays the original file; there's no server-side transcoding. That's ideal on a local network, but very high-bitrate files over a slow remote connection may buffer.

## License

MIT
