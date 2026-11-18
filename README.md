# Kali Blueprint

A Kali Linux VM for VMware, with Xfce, standard Kali tools, Norwegian keyboard and a custom desktop.

## Start

1. Download all archive parts and `SHA256SUMS` from [Releases](https://github.com/alexander474/kali-blueprint/releases). Sign in to see drafts. The parts should match `SHA256SUMS` (`Get-FileHash`).
2. Keep the parts in one folder and extract `kali-blueprint.7z.001` with 7-Zip.
3. Open the `.vmx` in VMware Workstation Pro 25H2 or newer (virtual hardware 22). Choose **I copied it** if asked.
4. The VM starts with the Desktop profile. On the laptop, select Work before the first start.

| PC | Profile | CPUs | RAM |
| --- | --- | ---: | ---: |
| Laptop (work) | Work | 4 | 8 GB |
| Desktop | Desktop | 8 | 12 GB |

To change profile, shut Kali down completely (not suspended), close its VMware tab and run `.\Set-Profile.ps1 -Vmx <name>.vmx -Profile Work` (or `Desktop`) in the VM folder. It changes only CPU and RAM and keeps a backup of the `.vmx`.

New builds log in `alex` on `lab` automatically. The public password `kali` is needed for `sudo`; run `passwd` to change it before using a lab VPN. The wallpaper is set at the first login; change it through Xfce Settings.

## Build

Code changes merged into `main` start a build automatically. For a manual build, choose **Actions → Kali Blueprint → Run workflow → main**. The download appears as a draft under Releases.

Defaults: [blueprint.json](blueprint.json). Development: [AGENTS.md](AGENTS.md).

Independent project, not an official Kali image. GPL-3.0-or-later for the build integration. Kali Linux and its dragon logo are OffSec trademarks.
