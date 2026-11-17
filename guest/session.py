#!/usr/bin/env python3
"""Apply user defaults inside the real Xfce session and preserve user edits."""
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

RUNTIME = Path(__file__).resolve().parent


def command(args, *, capture=False):
    result = subprocess.run(args, check=True, timeout=20, text=True, capture_output=capture)
    return result.stdout if capture else None


def managed(path, content, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(content.encode()).hexdigest()
    key = str(path)
    if path.exists():
        current = hashlib.sha256(path.read_bytes()).hexdigest()
        if current == digest:
            state[key] = digest
            return
        if current != state.get(key):
            return  # An existing personal file is not ours to replace.
        backup = path.with_name(path.name + '.before-' + current[:12])
        if not backup.exists():
            shutil.copyfile(path, backup)
    path.write_text(content, encoding='utf-8', newline='\n')
    state[key] = digest


def wallpaper(path):
    path = path.expanduser().resolve(strict=True)
    if not path.is_file() or path.stat().st_size > 32 * 1024**2 or path.suffix.lower() not in {'.png', '.jpg', '.jpeg'}:
        raise ValueError('Choose a local PNG or JPEG wallpaper')
    with path.open('rb') as stream:
        header = stream.read(8)
    if not (header == b'\x89PNG\r\n\x1a\n' or header.startswith(b'\xff\xd8\xff')):
        raise ValueError('Wallpaper content must be PNG or JPEG')
    props = command(['xfconf-query', '-c', 'xfce4-desktop', '-l'], capture=True).splitlines()
    targets = [item for item in props if item.endswith('/last-image') and '/backdrop/' in item]
    if not targets:
        raise ValueError('No active Xfce wallpaper properties; keep the existing background')
    for prop in targets:
        command(['xfconf-query', '-c', 'xfce4-desktop', '-p', prop, '-s', str(path)])
    command(['xfdesktop', '--reload'])


def main():
    if os.geteuid() == 0 or not os.environ.get('DISPLAY') or not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise SystemExit('Run as the logged-in Xfce user, not root')
    home = Path.home()
    statepath = home / '.local/state/kali-blueprint/managed.json'
    state = json.loads(statepath.read_text()) if statepath.exists() else {}
    conky = home / '.config/conky/kali-blueprint.conf'
    managed(conky, (RUNTIME / 'conky.conf').read_text(), state)
    flameshot = home / '.config/flameshot/flameshot.ini'
    flameshot.parent.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    if flameshot.exists():
        config.read(flameshot)
    if not config.has_section('General'):
        config.add_section('General')
    if not config.has_option('General', 'useX11LegacyScreenshot'):
        config.set('General', 'useX11LegacyScreenshot', 'true')
        if flameshot.exists():
            backup = flameshot.with_name(flameshot.name + '.before-' + hashlib.sha256(flameshot.read_bytes()).hexdigest()[:12])
            if not backup.exists():
                shutil.copyfile(flameshot, backup)
        with flameshot.open('w') as stream:
            config.write(stream, space_around_delimiters=False)
    shortcut = '/commands/custom/Print'
    existing = subprocess.run(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', shortcut],
                              capture_output=True, text=True, timeout=10)
    if existing.returncode != 0 or existing.stdout.strip() in {'xfce4-screenshooter', 'xfce4-screenshooter -f'}:
        command(['xfconf-query', '-c', 'xfce4-keyboard-shortcuts', '-p', shortcut,
                 '-n', '-t', 'string', '-s', 'flameshot gui'])
    personal = home / '.config/kali-blueprint/personal.json'
    if personal.exists():
        settings = json.loads(personal.read_text())
        if set(settings) != {'wallpaper'}:
            raise ValueError('Personal settings currently support only a local wallpaper path')
        wallpaper(Path(settings['wallpaper']))
    statepath.parent.mkdir(parents=True, exist_ok=True)
    statepath.write_text(json.dumps(state, indent=2) + '\n')
    running = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'conky'],
                             stdout=subprocess.DEVNULL, timeout=5)
    if running.returncode == 1:
        subprocess.Popen(['conky', '-p', '2', '-c', str(conky)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    elif running.returncode != 0:
        raise RuntimeError('Could not determine whether Conky is already running')


if __name__ == '__main__':
    main()
