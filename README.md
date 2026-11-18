# Kali Blueprint

[![Kali Rolling](https://img.shields.io/badge/Kali-Rolling-557C94?logo=kalilinux&logoColor=white)](https://www.kali.org/)
[![Build](https://github.com/alexander474/kali-blueprint/actions/workflows/build.yml/badge.svg?branch=main&event=push)](https://github.com/alexander474/kali-blueprint/actions/workflows/build.yml)
[![Release](https://img.shields.io/github/v/release/alexander474/kali-blueprint?label=release)](https://github.com/alexander474/kali-blueprint/releases/latest)

A Kali Linux VM for VMware, with Xfce, standard Kali tools, Norwegian keyboard and a custom desktop.

## Start

1. Download all archive parts from the [latest release](https://github.com/alexander474/kali-blueprint/releases/latest).
2. Keep the parts in one folder and extract `kali-blueprint.7z.001` with 7-Zip or another 7z tool.
3. Open the `.vmx` in VMware Workstation Pro 25H2 or newer (virtual hardware 22) on a 64-bit x86 (amd64) PC. Choose **I copied it** if asked.
4. Start Kali.

The release also has `SHA256SUMS`; each part's SHA-256 hash should match it before extraction.

Kali logs in `alex` on `lab` automatically. The public password `kali` is needed for `sudo`; run `passwd` to change it before personal use or a lab VPN. The tools and VMware guest tools are installed, and the desktop is set up at the first login; change the wallpaper through Xfce Settings.

The VM has 8 CPUs and 12 GB RAM. On a smaller PC, shut Kali down and lower them in VMware's VM settings.

## Build

Code changes merged into `main` start a build automatically. For a manual build, choose **Actions → Kali Blueprint → Run workflow → main**. The download appears as a draft under Releases.

Defaults: [blueprint.json](blueprint.json). Development: [AGENTS.md](AGENTS.md).

Independent project, not an official Kali image. GPL-3.0-or-later for the build integration. Kali Linux and its dragon logo are OffSec trademarks.
