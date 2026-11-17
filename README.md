# Kali Blueprint

A standard Kali Linux/Xfce VMware image with personal defaults, built by GitHub Actions using Kali's upstream debos recipes. This is an independent project, not an official Kali image.

## Build and download

1. Open **Actions → Kali Blueprint → Run workflow** on `main`.
2. Wait for the build. The workflow creates a **draft release** with numbered `7z` parts and `SHA256SUMS`.
3. Download every archive part into one directory. Verify the checksums and extract the first part with 7-Zip. Open the extracted `.vmx` in VMware Workstation supporting virtual hardware 22. Choose **I copied it** when asked.
4. Before starting the VM, select its resource profile with `Set-Profile.ps1 -Vmx '<path>.vmx' -Profile Work` or `Desktop`. The shared image has a dynamically growing 150 GB virtual disk; changing profiles changes CPU/RAM, not disk contents.
5. Start Kali. The default login is **alex / kali**, and the hostname is **lab**. Change the public initial password locally with `passwd` before using a lab VPN. The login name comes from `blueprint.json`; the initial password is always the public value `kali`.

The image includes `kali-linux-default`, Norwegian keyboard, Europe/Oslo, selected Xfce defaults, optional autologin, Conky, Flameshot and VMware guest tools. No customer-target allowlists, command wrappers or work-project plugins are added. Existing Windows security stays enabled.

## Wallpaper and identity

The bundled background in `guest/wallpaper.png` is installed automatically at the first Xfce login. It is the original PNG, copied without re-encoding. Its visible label is **alex@lab**, matching the default user and hostname. No cloud account, external image URL or post-import transfer is needed. Later logins preserve changes made through Xfce Settings.

The label is part of the image: changing `username` or `hostname` in `blueprint.json` changes the actual account or machine name but does not redraw the picture. Replace the PNG if you want different artwork or text. Do not put confidential information in the bundled image; it is public source and part of downloadable builds.

To select another local PNG or JPEG after importing the VM, use Xfce Settings. The optional Windows helper is also available after local SSH enrollment:

```powershell
.\Personalize.ps1 -Target kali -Wallpaper 'C:\path\your-wallpaper.png'
```

`Target` is your trusted SSH alias, for example `alex@<guest-IP>` after verifying its fingerprint. An optional `-PublicIdentityFile` selects the public key corresponding to your 1Password agent; private keys are never exported. The helper copies the image unchanged, verifies SHA-256, and saves an explicit wallpaper selection. Log out and back into Xfce to apply it. An explicit helper selection is reapplied at login; remove `~/.config/kali-blueprint/personal.json` if you want Xfce Settings to control the background again.

## Local access and credentials

SSH is installed but disabled in the shared image. Each new VM initializes its own SSH host keys. Enroll SSH locally through the VMware console, verify the host fingerprint, and authorize your selected public key before enabling access. Keep SSH restricted to your intended local host. Do not accept unknown host keys automatically.

Use 1Password for private client keys. Add personal VPN profiles locally after import. Neither belongs in GitHub Secrets or a publicly downloadable image. The workflow needs only GitHub's short-lived repository token to create the draft release; it does not need a personal access token.

## Configuration

Edit `blueprint.json` for common defaults and extra packages. Desktop starts with 8 vCPU/12 GiB RAM, Work with 4 vCPU/8 GiB. Adjust for the actual host. The upstream recipe commit is pinned; package versions still follow Kali rolling, so builds on different dates can differ.

The repository contains the build integration, desktop assets, helpers and agent instructions. Reports, personal overrides, test logs, course material, VM disks and backups stay outside Git. A draft release is not a claim that native VMware, keyboard/mouse, clipboard or personal VPN behavior has been tested.

## Working on the project

`AGENTS.md` is the shared project guide. `CLAUDE.md` imports it for Claude Code compatibility. Prefer local tools, Git and authenticated GitHub CLI/API operations; use a browser only when the required account or capability is unavailable through those tools.

Kali Linux™ and its dragon logo are trademarks of OffSec. The bundled background is provided by the project owner and includes that logo; its inclusion does not grant rights to the trademark or imply endorsement. Upstream recipes and included software retain their respective licenses; the build integration is provided under GPL-3.0-or-later.
