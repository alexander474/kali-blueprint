# Kali Blueprint

A standard Kali Linux/Xfce VMware image with personal defaults, built by GitHub Actions using Kali's upstream debos recipes. This is an independent project, not an official Kali image.

## Build and download

1. Open **Actions → Kali Blueprint → Run workflow** on `main`.
2. Wait for the build. The workflow creates a **draft release** with numbered `7z` parts and `SHA256SUMS`.
3. Download every archive part into one directory. Verify the checksums and extract the first part with 7-Zip. Open the extracted `.vmx` in VMware Workstation supporting virtual hardware 22. Choose **I copied it** when asked.
4. Before starting the VM, select its resource profile with `Set-Profile.ps1 -Vmx '<path>.vmx' -Profile Work` or `Desktop`. The shared image has a dynamically growing 150 GB virtual disk; changing profiles changes CPU/RAM, not disk contents.
5. Start Kali. The public initial login is **kali / kali**. Change it locally with `passwd` before using a lab VPN. The default password is deliberately public, never your personal password.

The image includes `kali-linux-default`, Norwegian keyboard, Europe/Oslo, selected Xfce defaults, optional autologin, Conky, Flameshot and VMware guest tools. No customer-target allowlists, command wrappers or work-project plugins are added. Existing Windows security stays enabled.

## Your wallpaper

The public image keeps Kali's installed wallpaper. Personal images are not included in Git or Actions Secrets.

Keep your current wallpaper in Proton Drive or another local location. After local SSH enrollment, run:

```powershell
.\Personalize.ps1 -Target kali -Wallpaper 'C:\path\your-wallpaper.png'
```

`Target` is your trusted SSH alias. An optional `-PublicIdentityFile` selects the public key corresponding to your 1Password agent; private keys are never exported. The helper copies your original image without editing it, verifies SHA-256, and saves a local wallpaper selection. Log out and back into Xfce to apply it. Updating the public configuration does not replace your selected local wallpaper.

## Local access and credentials

SSH is installed but disabled in the shared image. Each new VM initializes its own SSH host keys. Enroll SSH locally through the VMware console, verify the host fingerprint, and authorize your selected public key before enabling access. Keep SSH restricted to your intended local host. Do not accept unknown host keys automatically.

Use 1Password for private client keys. Add personal VPN profiles locally after import. Neither belongs in GitHub Secrets or a publicly downloadable image. The workflow needs only GitHub's short-lived repository token to create the draft release; it does not need a personal access token.

## Configuration

Edit `blueprint.json` for common defaults and extra packages. Desktop starts with 8 vCPU/12 GiB RAM, Work with 4 vCPU/8 GiB. Adjust for the actual host. The upstream recipe commit is pinned; package versions still follow Kali rolling, so builds on different dates can differ.

Build files are limited to the recipe, runtime configuration, guest helpers and Windows helpers. Reports, personal settings, wallpapers, test logs, course material, VM disks and backups stay outside Git. A draft release is not a claim that native VMware, keyboard/mouse, clipboard or personal VPN behavior has been tested.

Kali Linux™ is a trademark of OffSec. Upstream recipes and included software retain their respective licenses; the build integration is provided under GPL-3.0-or-later. No personal wallpaper or third-party logo artwork is redistributed by this repository.
