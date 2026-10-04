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

- Python 3.11+ and `mpv`; optional ImageMagick for media artwork
- Signs in through plex.tv in your browser, finds your server, prefers local connections
- Continue Watching (in progress and up next) and Recently Added across all libraries
- Resumes where you left off and reports progress back to Plex (watched at 90%)
- Detects an HDMI receiver and bitstreams Dolby (incl. TrueHD/Atmos) and DTS (incl. DTS-HD/DTS:X)
- Switches the display to HDR for HDR titles, passing the film's metadata through, and matches the refresh rate to the frame rate
- Unwatched `●` / in-progress `◐` markers, detail pane with summary and media info
- Movie/show posters and episode stills in the detail pane, loaded in the background and cached in memory
- Incremental search across everything you've loaded

## Install

On Omarchy / Arch, install the package from the [latest release](https://github.com/brunoenten/plexi/releases/latest):

```sh
sudo pacman -U https://github.com/brunoenten/plexi/releases/download/v0.4.0/plexi-0.4.0-1-any.pkg.tar.zst
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

## Media artwork

With ImageMagick (`magick`) installed, selecting a movie, show, season, or episode displays its Plex artwork above the details. Episodes use their still image, with parent artwork as a fallback. Images load on a background worker, and a bounded memory cache avoids downloading them again while browsing. Missing artwork or ImageMagick leaves the text interface usable.

Plexi detects sixel support (including Foot) at startup and uses the Kitty graphics protocol in Kitty and Ghostty. Other terminals, and terminal multiplexers, use a color block preview. The detail pane appears from 64 columns wide, and images appear from 13 rows tall. Select an individual movie, show, season, or episode to see its artwork; library headings and hubs have text details. A loading message appears while the preview downloads.

Set `artwork = "auto"` in `~/.config/plexi/config.toml` or use `PLEXI_ARTWORK=auto`. Supported modes are `auto`, `sixel`, `kitty`, `blocks`, and `off`. Use `off` for the text interface. Artwork is requested only from the configured Plex server, using the existing authentication headers; no credentials are stored in image files.

## Surround sound passthrough

When your default audio output is HDMI and the device on the other end (an AV receiver, soundbar or TV) advertises Dolby or DTS support, plexi sends those tracks to it untouched instead of decoding them: Dolby Digital, Dolby Digital+, TrueHD (including Atmos), DTS and DTS-HD (including DTS:X). The receiver's name appears in the top border, and the detail pane shows how each title's audio will be played.

How it works:

- The supported formats come from the HDMI device's ELD, which ALSA exposes in `/proc/asound/card*/eld#*`.
- If the PipeWire HDMI output doesn't declare those formats yet (the default on a fresh install), plexi declares them once with `pactl set-sink-formats`. This is the same as ticking them under "Advanced" in pavucontrol, and WirePlumber remembers it.
- Passthrough only applies when the HDMI output is the default output, so headphones and speakers keep working as usual. Detection runs again before each playback.
- PipeWire can only bitstream to an output that no other app is connected to. Browsers often keep a silent stream open, so if, say, Chromium holds the HDMI output, plexi plays decoded audio instead and tells you which app is in the way. The top border shows this too.
- While bitstreaming, mpv's volume keys have no effect; use the receiver's volume.

- When a surround track can't be bitstreamed and the HDMI output only takes stereo PCM (PipeWire's default HDMI profile), mpv re-encodes it to 5.1 Dolby Digital instead of downmixing it to stereo.

To turn it off, set `passthrough = "off"` in `~/.config/plexi/config.toml`, or launch with `PLEXI_PASSTHROUGH=off plexi`.

Some links advertise the receiver's formats but can't carry them, such as active DisplayPort-to-HDMI adapters, which often pass only 48 kHz bitstreams. List what actually works, for example `passthrough = "ac3,dts"`. The names are `ac3`, `eac3`, `truehd`, `dts` and `dts-hd`. Other surround tracks are then re-encoded to Dolby Digital, and DTS-HD plays as its DTS core.

## HDR and refresh rate

mpv always opens fullscreen. For HDR10, HLG and Dolby Vision titles, plexi asks mpv to hand the video to the compositor in its own colorspace, with the film's mastering metadata (peak brightness, MaxCLL, MaxFALL). Hyprland's `render:cm_auto_hdr` (on by default) then switches the display to HDR while mpv is fullscreen, and back to SDR when you leave fullscreen or stop playback. The detail pane shows each title's HDR format and frame rate.

On Hyprland, plexi also makes sure the display shows every frame for the same time, so motion doesn't judder.

If VRR is on (`misc:vrr`, for example `3` for fullscreen video and games only) and the display's VRR range covers the video's frame rate or a multiple of it, plexi leaves the mode alone and lets VRR follow the film. That means no blank screen, and even 24.000 fps films play at their exact rate. The range comes from the display's EDID. With a 48–120 Hz TV, run the desktop at 120 Hz: at 60 Hz, 23.976 fps doesn't fit, because doubling it gives 47.95 Hz, just under the minimum.

Otherwise it switches the display's refresh rate to match the video: 23.976 fps films play at 23.98 Hz, 25 fps at 50 Hz, 29.97 fps at 59.94 Hz, and so on. It picks the closest exact multiple your display offers at its current resolution, switches to 10-bit output for HDR titles, and puts everything back when mpv exits, even if you've quit plexi in the meantime. The screen (and an AV receiver in between) goes blank for a second or two while the mode changes.

Notes:

- Dolby Vision plays as HDR10 on displays without Dolby Vision support. mpv converts profile 5, which has no HDR10 base layer.
- Outside Hyprland the display mode is left alone. Other compositors with color management (KDE Plasma, for example) still receive the HDR request.

To turn either off, set `hdr = "off"` (HDR is tone-mapped to SDR) or `match_refresh = "off"` in `config.toml`, or launch with `PLEXI_HDR=off` / `PLEXI_REFRESH=off`. `match_refresh = "switch"` always switches modes, even when VRR could be used.

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
