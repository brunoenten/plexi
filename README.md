# plexi

A lightweight, keyboard-driven Plex client for the terminal, built for [Omarchy](https://omarchy.org).

Browse your libraries as a tree — **library → show → season → episode** or **library → movie** — with **Continue Watching** and **Recently Added** at the top, and play with `mpv`. Plexi picks up your current Omarchy theme colors and follows along live when you switch themes.

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
- Continue Watching (in progress and up next) and Recently Added across all libraries
- Resumes where you left off and reports progress back to Plex (watched at 90%)
- Unwatched `●` / in-progress `◐` markers, detail pane with summary and media info
- Incremental search across everything you've loaded

## Install

On Omarchy / Arch, install the package from the [latest release](https://github.com/brunoenten/plexi/releases/latest):

```sh
sudo pacman -U https://github.com/brunoenten/plexi/releases/download/v0.3.0/plexi-0.3.0-1-any.pkg.tar.zst
```

Then launch **Plexi** from the app launcher (<kbd>Super</kbd> + <kbd>Space</kbd>), or run `plexi` in a terminal.

Prefer building it yourself? Each release also ships its `PKGBUILD`:

```sh
mkdir plexi && cd plexi
curl -LO https://github.com/brunoenten/plexi/releases/latest/download/PKGBUILD
makepkg -si
```

Anywhere else with Python 3.11+ and mpv, it's a single file:

```sh
curl -Lo ~/.local/bin/plexi https://raw.githubusercontent.com/brunoenten/plexi/main/plexi
chmod +x ~/.local/bin/plexi
```

An AUR package is coming once AUR registrations reopen.

## Usage

```
plexi           browse your libraries (signs in on first run)
plexi login     sign in again / pick another server
plexi logout    forget the saved server and token
plexi log       show the end of the log
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
| `c` | reconnect (ask plex.tv for every server address) |
| `esc` | cancel a slow request |
| `g` `G` · `ctrl-d` `ctrl-u` | top, bottom · half page |
| `q` | quit |

## Configuration

Credentials live in `~/.config/plexi/config.toml` (mode `600`). `PLEX_URL` and `PLEX_TOKEN` override them, which is handy for a server you reach directly:

```sh
PLEX_URL=http://192.168.1.10:32400 PLEX_TOKEN=xxxx plexi
```

Colors are read from `~/.local/state/omarchy/current/theme/colors.toml`. Outside Omarchy, plexi falls back to a neutral dark palette.

## Troubleshooting

Plexi remembers every address Plex advertises for your server (local, remote, relay). If the current one stops answering, it tries all of them in parallel, asks plex.tv for fresh ones if needed, and switches to the best one that responds. IPv6 and IPv4 are raced too, so a broken IPv6 route doesn't stall anything.

Every request, the addresses tried and their results are logged (tokens redacted) to `~/.local/state/plexi/plexi.log`:

```sh
plexi log
```

Set `PLEXI_DEBUG=1` for extra detail, such as which IP each connection used.

## Notes

Plexi direct-plays the original file; there's no server-side transcoding. That's ideal on a local network, but very high-bitrate files over a slow remote connection may buffer.

## License

MIT
