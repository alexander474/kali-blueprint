# Kali Blueprint

A Kali Linux VM for VMware, with Xfce, standard Kali tools, Norwegian keyboard and a custom desktop.

## Start

1. Download all archive parts from [Releases](https://github.com/alexander474/kali-blueprint/releases). Sign in to see drafts.
2. Keep the parts in one folder and extract `kali-blueprint.7z.001` with 7-Zip.
3. Open the `.vmx` in VMware. Choose **I copied it** if asked.
4. Set CPU and RAM, then start the VM and log in using the release notes.

| PC | CPUs | RAM |
| --- | ---: | ---: |
| Laptop | 4 | 8 GB |
| Desktop | 8 | 12 GB |

New builds use `alex / kali` on `lab`. Run `passwd` to change the password before using a lab VPN. The wallpaper is set automatically; change it through Xfce Settings.

## Build

Choose **Actions → Kali Blueprint → Run workflow → main**. The download appears as a draft under Releases.

Defaults: [blueprint.json](blueprint.json). Development: [AGENTS.md](AGENTS.md).

Independent project, not an official Kali image. GPL-3.0-or-later for the build integration. Kali Linux and its dragon logo are OffSec trademarks.
