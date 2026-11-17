# Kali Blueprint

My Kali Linux VM for VMware, with Xfce, the standard Kali tools, Norwegian keyboard and a ready-made desktop.

## Get started

1. Download **all archive parts** from [Releases](https://github.com/alexander474/kali-blueprint/releases). Sign in to see draft releases.
2. Put the parts in the same folder and extract **`kali-blueprint.7z.001`** with 7-Zip.
3. Open the extracted **`.vmx`** in VMware Workstation. Choose **I copied it** if asked.
4. Adjust CPU and RAM below, then start the VM. Use the login in the release notes.
5. Open a terminal and run **`passwd`** to change the initial password before connecting a lab VPN.

New builds default to **alex / kali**, with hostname **lab**. The wallpaper is applied automatically. Change it through Xfce Settings whenever you like.

## Pick your resources

| PC | CPUs | RAM |
| --- | ---: | ---: |
| Laptop | 4 | 8 GB |
| Desktop | 8 | 12 GB |

Set these in VMware while the VM is shut down. The virtual disk grows as needed, up to 150 GB.

## Build a new image

Open **Actions → Kali Blueprint → Run workflow → main**. The finished image appears as a draft under Releases.

For different defaults, edit [blueprint.json](blueprint.json) before building. Development instructions are in [AGENTS.md](AGENTS.md).

Independent project; not an official Kali image. Build integration: GPL-3.0-or-later. Kali Linux and its dragon logo are trademarks of OffSec.
