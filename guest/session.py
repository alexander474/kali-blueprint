#!/usr/bin/env python3
import configparser
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

RUNTIME = Path(__file__).resolve().parent
SHORTCUTS = 'xfce4-keyboard-shortcuts'
PRINT = '/commands/custom/Print'
PRINT_DEFAULTS = {'xfce4-screenshooter', 'xfce4-screenshooter -f', '/usr/share/kali-themes/xfce4-screenshooter'}


def command(args, *, capture=False):
    result = subprocess.run(args, check=True, timeout=20, text=True, capture_output=capture)
    return result.stdout if capture else None


def poll(read):
    for attempt in range(8):
        try:
            value = read()
        except subprocess.SubprocessError:
            value = None
        if value:
            return value
        if attempt < 7:
            time.sleep(1)
    return None


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
            return
        backup = path.with_name(path.name + '.before-' + current[:12])
        if not backup.exists():
            shutil.copyfile(path, backup)
    path.write_text(content, encoding='utf-8', newline='\n')
    state[key] = digest


def load_state(path):
    if not path.exists():
        return {}
    data = path.read_bytes()
    try:
        state = json.loads(data)
    except ValueError:
        state = None
    if isinstance(state, dict):
        return state
    backup = path.with_name(path.name + '.invalid-' + hashlib.sha256(data).hexdigest()[:12])
    if not backup.exists():
        shutil.copyfile(path, backup)
    print(f'Invalid {path.name} kept as {backup.name}; one-time settings are not repeated', file=sys.stderr)
    return {'bundled_wallpaper_applied': True, 'print_shortcut': True}


def flameshot_settings(path):
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    if path.exists():
        with path.open(encoding='utf-8') as stream:
            config.read_file(stream)
    if config.has_option('General', 'useX11LegacyScreenshot'):
        return
    if not config.has_section('General'):
        config.add_section('General')
    config.set('General', 'useX11LegacyScreenshot', 'true')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(path.name + '.before-' + hashlib.sha256(path.read_bytes()).hexdigest()[:12])
        if not backup.exists():
            shutil.copyfile(path, backup)
    with path.open('w', encoding='utf-8') as stream:
        config.write(stream, space_around_delimiters=False)


def shortcut_properties():
    props = command(['xfconf-query', '-c', SHORTCUTS, '-l'], capture=True).splitlines()
    override = '/commands/custom/override'
    if override in props and command(['xfconf-query', '-c', SHORTCUTS, '-p', override], capture=True).strip() == 'true':
        return props
    return None


def print_shortcut(state):
    props = poll(shortcut_properties)
    if not props:
        raise ValueError('Xfce shortcuts are not initialized')
    if PRINT in props:
        if command(['xfconf-query', '-c', SHORTCUTS, '-p', PRINT], capture=True).strip() not in PRINT_DEFAULTS:
            state['print_shortcut'] = True
            return
    elif state.get('print_shortcut'):
        return
    command(['xfconf-query', '-c', SHORTCUTS, '-p', PRINT, '-n', '-t', 'string', '-s', 'flameshot gui'])
    state['print_shortcut'] = True


def wallpaper(path):
    path = path.resolve(strict=True)

    def monitors():
        lines = command(['xrandr', '--listactivemonitors'], capture=True).splitlines()[1:]
        return [line.split()[-1] for line in lines if line.strip()]

    found = poll(monitors)
    if not found:
        raise ValueError('No active monitors; keep the existing background')
    for name in found:
        command(['xfconf-query', '-c', 'xfce4-desktop', '-p', f'/backdrop/screen0/monitor{name}/workspace0/last-image',
                 '-n', '-t', 'string', '-s', str(path)])
    command(['xfdesktop', '--reload'])


def apply_background(state):
    if not state.get('bundled_wallpaper_applied', False):
        wallpaper(RUNTIME / 'wallpaper.png')
        state['bundled_wallpaper_applied'] = True


def main():
    if os.geteuid() == 0 or not os.environ.get('DISPLAY') or not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise SystemExit('Run as the logged-in Xfce user, not root')
    home = Path.home()
    statepath = home / '.local/state/kali-blueprint/managed.json'
    state = load_state(statepath)
    conky = home / '.config/conky/kali-blueprint.conf'
    steps = (
        ('Conky configuration', lambda: managed(conky, (RUNTIME / 'conky.conf').read_text(), state)),
        ('Flameshot configuration', lambda: flameshot_settings(home / '.config/flameshot/flameshot.ini')),
        ('Print shortcut', lambda: print_shortcut(state)),
        ('Wallpaper', lambda: apply_background(state)),
    )
    for name, step in steps:
        try:
            step()
        except (OSError, ValueError, configparser.Error, subprocess.SubprocessError) as error:
            print(f'{name} unchanged: {error}', file=sys.stderr)
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
