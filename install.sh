#!/bin/sh
# Install or upgrade plexi: https://github.com/brunoenten/plexi
#
#   curl -fsSL https://raw.githubusercontent.com/brunoenten/plexi/main/install.sh | sh
#
# On Arch/Omarchy it adds the bruno-omarchy-addons pacman repository and installs plexi from it,
# so pacman -Syu keeps it up to date. Elsewhere it puts the single-file script in ~/.local/bin
# (or $PLEXI_BIN). PLEXI_VERSION=0.4.0 pins a version (on Arch, the release's package).
set -eu

main() {
    repo=brunoenten/plexi
    addons=bruno-omarchy-addons
    key=16114DD8DBCA434D6F5EB1236F6D038C8A17FE15
    say() { printf '\033[1m%s\033[0m\n' "$*"; }
    die() { printf '\033[31merror:\033[0m %s\n' "$*" >&2; exit 1; }
    command -v curl >/dev/null || die "curl is required"

    if command -v pacman >/dev/null && [ -z "${PLEXI_BIN:-}" ] && [ -z "${PLEXI_VERSION:-}" ]; then
        if ! grep -q "^\[$addons\]" /etc/pacman.conf; then
            say "adding the $addons pacman repository (asks for your password)"
            curl -fsSL "https://raw.githubusercontent.com/brunoenten/$addons/main/key.asc" | sudo pacman-key --add -
            sudo pacman-key --lsign-key "$key"
            printf '\n[%s]\nServer = https://github.com/brunoenten/%s/releases/download/repo\n' "$addons" "$addons" \
                | sudo tee -a /etc/pacman.conf >/dev/null
        fi
        say "installing plexi with pacman (this also brings the system up to date)"
        # When piped into sh, stdin is this script; pacman's questions need the keyboard.
        if (exec </dev/tty) 2>/dev/null; then
            sudo pacman -Syu --needed plexi </dev/tty
        else
            sudo pacman -Syu --needed --noconfirm plexi
        fi
        say "done — run plexi"
        return
    fi

    if [ -n "${PLEXI_VERSION:-}" ]; then
        tag="v${PLEXI_VERSION#v}"
    else
        tag=$(curl -fsSL "https://api.github.com/repos/$repo/releases/latest" | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -n1)
        [ -n "$tag" ] || die "couldn't find the latest release on GitHub"
    fi
    version=${tag#v}
    say "plexi $version"

    if command -v pacman >/dev/null && [ -z "${PLEXI_BIN:-}" ]; then
        url="https://github.com/$repo/releases/download/$tag/plexi-$version-1-any.pkg.tar.zst"
        say "installing the package with pacman (asks for your password)"
        # --noconfirm: when piped into sh, stdin is this script, not the keyboard
        sudo pacman -U --needed --noconfirm "$url"
    else
        bin=${PLEXI_BIN:-$HOME/.local/bin/plexi}
        command -v python3 >/dev/null || die "plexi needs Python 3.11 or newer"
        python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' || die "plexi needs Python 3.11 or newer"
        mkdir -p "$(dirname "$bin")"
        tmp="$bin.download"
        curl -fsSL -o "$tmp" "https://raw.githubusercontent.com/$repo/$tag/plexi"
        chmod +x "$tmp"
        mv "$tmp" "$bin"
        say "installed $bin"
        if command -v xdg-terminal-exec >/dev/null; then
            apps=${XDG_DATA_HOME:-$HOME/.local/share}
            mkdir -p "$apps/applications" "$apps/icons/hicolor/scalable/apps"
            curl -fsSL -o "$apps/applications/plexi.desktop" "https://raw.githubusercontent.com/$repo/$tag/plexi.desktop"
            curl -fsSL -o "$apps/icons/hicolor/scalable/apps/plexi.svg" "https://raw.githubusercontent.com/$repo/$tag/plexi.svg"
        fi
        command -v mpv >/dev/null || printf 'note: install mpv to play videos\n'
        case ":$PATH:" in *":$(dirname "$bin"):"*) ;; *) printf 'note: add %s to your PATH\n' "$(dirname "$bin")" ;; esac
    fi
    say "done — run plexi"
}

main "$@"
