#!/usr/bin/env python3
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
UPSTREAM = 'https://gitlab.com/kalilinux/build-scripts/kali-vm.git'


def run(args, *, cwd=None, timeout=300, env=None, capture=False):
    result = subprocess.run(args, cwd=cwd, env=env, timeout=timeout,
                            check=True, text=True, capture_output=capture)
    return result.stdout.strip() if capture else None


def configuration():
    config = json.loads((ROOT / 'blueprint.json').read_text())
    required = {'upstream_commit', 'hostname', 'username', 'keyboard', 'timezone',
                'locale', 'disk_gb', 'autologin', 'clipboard', 'extra_packages', 'profiles'}
    if set(config) != required:
        raise ValueError('Unexpected or missing configuration fields; keep secrets local')
    if not re.fullmatch('[0-9a-f]{40}', config['upstream_commit']):
        raise ValueError('Pin the upstream recipe to a commit')
    if not re.fullmatch('[a-z][a-z0-9_-]{0,31}', config['username']) or config['username'] in {'root', 'nobody'}:
        raise ValueError('Choose a non-root Linux username of 1 to 32 characters')
    if not re.fullmatch('[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', config['hostname']):
        raise ValueError('Choose a lowercase hostname of 1 to 63 characters')
    for field in ('keyboard', 'locale'):
        if not re.fullmatch('[A-Za-z0-9_.-]+', config[field]):
            raise ValueError('Invalid ' + field)
    if not re.fullmatch('[A-Za-z_+-]+/[A-Za-z_+-]+', config['timezone']):
        raise ValueError('Invalid timezone')
    if type(config['disk_gb']) is not int or not 80 <= config['disk_gb'] <= 300:
        raise ValueError('Invalid disk size')
    if any(type(config[name]) is not bool for name in ('autologin', 'clipboard')):
        raise ValueError('Boolean options must be true or false')
    if not isinstance(config['extra_packages'], list) or any(
            not isinstance(item, str) or not re.fullmatch('[a-z0-9][a-z0-9+.-]+', item)
            for item in config['extra_packages']):
        raise ValueError('Invalid package list')
    if set(config['profiles']) != {'Desktop', 'Work'}:
        raise ValueError('Expected Desktop and Work profiles')
    for profile in config['profiles'].values():
        if set(profile) != {'cpus', 'memory_mb'} or any(type(value) is not int for value in profile.values()):
            raise ValueError('Invalid host profile')
        if not 1 <= profile['cpus'] <= 32 or not 2048 <= profile['memory_mb'] <= 65536:
            raise ValueError('Host profile out of range')
    return config


def validate():
    configuration()
    for path in (ROOT / 'guest').glob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    for required in ('configure.py', 'session.py', 'network.py', 'conky.conf', 'wallpaper.png'):
        if not (ROOT / 'guest' / required).is_file():
            raise ValueError('Missing runtime file: ' + required)
    with (ROOT / 'guest/wallpaper.png').open('rb') as image:
        if image.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError('Bundled wallpaper must be PNG')
    print('Configuration and Python syntax are valid. No image was built.')


def vmx_settings(config):
    profile = config['profiles']['Desktop']
    return {
        '.encoding': 'UTF-8', 'displayName': 'Kali Blueprint', 'virtualHW.version': '22',
        'guestOS': 'debian12-64', 'numvcpus': str(profile['cpus']),
        'cpuid.coresPerSocket': str(profile['cpus']), 'memsize': str(profile['memory_mb']),
        'ethernet0.connectionType': 'nat', 'ethernet0.addressType': 'generated',
        'isolation.tools.hgfs.disable': 'TRUE', 'sharedFolder.maxNum': '0',
        'isolation.tools.dnd.disable': 'TRUE',
        'isolation.tools.copy.disable': str(not config['clipboard']).upper(),
        'isolation.tools.paste.disable': str(not config['clipboard']).upper(),
        'usb.generic.autoconnect': 'FALSE', 'usb.generic.allowHID': 'FALSE',
        'usb.vbluetooth.startConnected': 'FALSE', 'keyboard.vusb.enable': 'FALSE',
        'mouse.vusb.enable': 'FALSE', 'mks.noHostCursor': 'TRUE', 'mks.enable3d': 'FALSE',
        'serial0.present': 'FALSE', 'vhv.enable': 'FALSE',
        'annotation': 'Independent personal Kali configuration. Change the public initial password before use.',
    }


def build():
    if sys.platform != 'linux':
        raise ValueError('Build on a GitHub-hosted Ubuntu runner with Docker and KVM')
    config = configuration()
    work = ROOT / '.build'
    if work.exists() or (ROOT / 'dist').exists():
        raise ValueError('Use a fresh checkout; existing build outputs are preserved')
    if not Path('/dev/kvm').exists() or shutil.disk_usage(ROOT).free < 50 * 1024**3:
        raise ValueError('Build needs KVM and at least 50 GiB free disk space')
    work.mkdir()
    upstream = work / 'upstream'
    run(['git', 'init', str(upstream)], timeout=30)
    run(['git', 'remote', 'add', 'origin', UPSTREAM], cwd=upstream, timeout=30)
    run(['git', 'fetch', '--depth=1', 'origin', config['upstream_commit']], cwd=upstream)
    run(['git', 'checkout', '--detach', 'FETCH_HEAD'], cwd=upstream, timeout=30)
    if run(['git', 'rev-parse', 'HEAD'], cwd=upstream, capture=True) != config['upstream_commit']:
        raise ValueError('Upstream revision mismatch')
    overlay = upstream / 'blueprint-overlay'
    runtime = overlay / 'usr/local/lib/kali-blueprint'
    runtime.mkdir(parents=True)
    for path in (ROOT / 'guest').iterdir():
        if path.is_file() and path.suffix in ('.py', '.conf', '.png'):
            shutil.copyfile(path, runtime / path.name)
    settings = overlay / 'etc/kali-blueprint'
    settings.mkdir(parents=True)
    (settings / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    recipe = upstream / 'image.yaml'
    text = recipe.read_text()
    marker = '  - description: "Final cleanup (from within)"\n'
    if text.count(marker) != 1:
        raise ValueError('Upstream image recipe changed; review the integration')
    insertion = ('  - action: overlay\n    source: blueprint-overlay\n\n'
                 '  - action: run\n    chroot: true\n'
                 '    command: python3 /usr/local/lib/kali-blueprint/configure.py\n\n')
    recipe.write_text(text.replace(marker, insertion + marker), newline='\n')
    revision = run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture=True)
    version = 'blueprint-' + revision[:12]
    output = work / 'output'
    env = dict(os.environ, CONTAINER='docker', IMAGE='kali-blueprint-builder')
    run(['bash', 'build-in-container.sh', '--variant', 'vmware', '--desktop', 'xfce',
         '--toolset', 'default', '--keyboard', config['keyboard'], '--timezone', config['timezone'],
         '--locale', config['locale'], '--hostname', config['hostname'], '--size', str(config['disk_gb']),
         '--userpass', config['username'] + ':kali',
         '--packages', ','.join(config['extra_packages']), '--mirror', 'https://kali.download/kali',
         '--version', version, '--output', str(output)], cwd=upstream, env=env, timeout=12600)
    folders = list(output.glob('*.vmwarevm'))
    if len(folders) != 1:
        raise ValueError('Expected exactly one built VM')
    folder = folders[0]
    vmx_files = list(folder.glob('*.vmx'))
    if len(vmx_files) != 1 or not list(folder.glob('*.vmdk')):
        raise ValueError('Incomplete VMware output')
    values = {}
    for line in vmx_files[0].read_text().splitlines():
        match = re.fullmatch(r'\s*([^=\s]+)\s*=\s*"(.*)"\s*', line)
        if line.strip() and (not match or match[1] in values):
            raise ValueError('Invalid or duplicate VMX entry')
        if match:
            values[match[1]] = match[2]
    for key in list(values):
        if key.startswith(('usb:', 'sharedFolder')):
            del values[key]
    values.update(vmx_settings(config))
    vmx_files[0].write_text(''.join(f'{key} = "{value}"\n' for key, value in values.items()), encoding='utf-8')
    shutil.copyfile(ROOT / 'Set-Profile.ps1', folder / 'Set-Profile.ps1')
    shutil.copyfile(ROOT / 'Personalize.ps1', folder / 'Personalize.ps1')
    shutil.copyfile(ROOT / 'blueprint.json', folder / 'blueprint.json')
    shutil.copyfile(ROOT / 'README.md', folder / 'README.md')
    dist = ROOT / 'dist'
    dist.mkdir()
    archiver = shutil.which('7zz') or shutil.which('7z')
    if not archiver:
        raise ValueError('Install the 7zip package before packaging')
    run([archiver, 'a', '-t7z', '-mx=3', '-mmt=2', '-v1800m',
         str(dist / 'kali-blueprint.7z'), folder.name], cwd=output, timeout=1800)
    parts = sorted(dist.glob('kali-blueprint.7z.*'))
    if not parts or any(path.stat().st_size >= 2_000_000_000 for path in parts):
        raise ValueError('Missing or oversized release parts')
    run([archiver, 't', str(parts[0])], timeout=1800)
    sums = []
    for part in parts:
        with part.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        sums.append(f'{digest}  {part.name}\n')
    (dist / 'SHA256SUMS').write_text(''.join(sums))
    print('Build packaged. Native VMware and personal VPN checks remain local.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build a Kali VMware image.')
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args()
    try:
        validate()
        if not args.validate:
            build()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        sys.exit(str(error))
