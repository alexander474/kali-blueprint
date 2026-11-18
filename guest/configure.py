#!/usr/bin/env python3
import json
import os
from pathlib import Path
import pwd
import subprocess


def main():
    if os.geteuid() != 0 or 'ID=kali' not in Path('/etc/os-release').read_text().replace('"', ''):
        raise SystemExit('Run only as root inside the Kali build filesystem')
    config = json.loads(Path('/etc/kali-blueprint/config.json').read_text())
    account = pwd.getpwnam(config['username'])
    home = Path(account.pw_dir)
    for relative in ('Kali', 'Kali/notes', 'Kali/work', 'Kali/evidence',
                     'Pictures', 'Pictures/Wallpapers', '.config',
                     '.config/autostart'):
        path = home / relative
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(0o700)
        os.chown(path, account.pw_uid, account.pw_gid)
    startup = home / '.config/autostart/kali-blueprint.desktop'
    startup.write_text('[Desktop Entry]\nType=Application\nName=Kali Blueprint\n'
                       'Exec=/usr/bin/python3 /usr/local/lib/kali-blueprint/session.py\n'
                       'OnlyShowIn=XFCE;\nTerminal=false\n')
    os.chown(startup, account.pw_uid, account.pw_gid)
    if config['autologin']:
        lightdm = Path('/etc/lightdm/lightdm.conf.d/90-kali-blueprint.conf')
        lightdm.parent.mkdir(parents=True, exist_ok=True)
        lightdm.write_text('[Seat:*]\nautologin-user=' + config['username'] + '\nautologin-user-timeout=0\n')
    subprocess.run(['systemctl', 'disable', 'ssh.service', 'ssh.socket'], check=True)
    init = Path('/usr/local/lib/kali-blueprint/initialize.sh')
    init.write_text('#!/bin/sh\nset -eu\nssh-keygen -A\n'
                    'install -d -m 700 /var/lib/kali-blueprint\n'
                    'touch /var/lib/kali-blueprint/initialized\n')
    init.chmod(0o755)
    unit = Path('/etc/systemd/system/kali-blueprint-initialize.service')
    unit.write_text('[Unit]\nDescription=Initialize this Kali Blueprint instance\n'
                    'Before=ssh.service display-manager.service\n'
                    'ConditionPathExists=!/var/lib/kali-blueprint/initialized\n'
                    '[Service]\nType=oneshot\nExecStart=/usr/local/lib/kali-blueprint/initialize.sh\n'
                    'RemainAfterExit=yes\n[Install]\nWantedBy=multi-user.target\n')
    subprocess.run(['systemctl', 'enable', 'kali-blueprint-initialize.service'], check=True)
    Path('/etc/machine-id').write_text('')
    print('Desktop defaults and bundled wallpaper installed; SSH disabled; no personal credentials enrolled.')


if __name__ == '__main__':
    main()
