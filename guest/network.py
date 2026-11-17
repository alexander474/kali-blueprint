#!/usr/bin/env python3
import json
import subprocess


def query(*args):
    result = subprocess.run(['ip', '-j', *args], check=True, capture_output=True, text=True, timeout=5)
    return json.loads(result.stdout)


def main():
    try:
        links = {item['ifname']: item for item in query('-d', 'link', 'show')}
        addresses = query('-4', 'addr', 'show', 'scope', 'global')
        tunnels = {name for name, item in links.items()
                   if item.get('linkinfo', {}).get('info_kind') in {'tun', 'wireguard'}
                   or name.startswith(('tun', 'tap', 'wg'))}
        ipv4 = {item['ifname']: [value['local'] for value in item.get('addr_info', [])
                                if value.get('family') == 'inet'] for item in addresses}
        routes = sorted(query('-4', 'route', 'show', 'default'), key=lambda item: item.get('metric', 0))
        primary = next((item['dev'] for item in routes if item.get('dev') not in tunnels), None)
        nat = ', '.join(ipv4.get(primary, [])) or 'ingen adresse'
        vpn = ', '.join(address for name in sorted(tunnels) for address in ipv4.get(name, []))
        print('Kali NAT   ' + nat)
        print('VPN: ' + (vpn or 'frakoblet'))
    except (OSError, ValueError, subprocess.SubprocessError):
        print('Nettverk: utilgjengelig')


if __name__ == '__main__':
    main()
