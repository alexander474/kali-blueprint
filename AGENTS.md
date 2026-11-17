# Working on Kali Blueprint

This builds a Kali/Xfce VMware image using upstream debos recipes. Keep the standard tools and the owner's desktop settings. Build defaults belong in `blueprint.json`; guest setup is in `guest/` and packaging is in `build.py`.

Read `git status`, `README.md` and the affected files before editing. Preserve unrelated changes, existing VMs, backups and releases. Keep code and documentation short and direct. Do not add explanatory comments or repeat information between files. Keep shebangs and required license notices.

Use local tools, Git and CLI/API calls. Do not use browser automation unless the user asks for it. Read focused excerpts, not entire logs. Do not start extra agents or models unless requested. Keep temporary work in ignored `.local/` or an authorized external directory.

Use `alexander474/kali-blueprint` and the owner's private GitHub key through the existing 1Password SSH agent. Verify the account before remote writes. Do not use a work identity, export keys, extract tokens or change global authentication. Use a feature branch and PR. If personal API access is unavailable, push the branch and provide its compare link. Merge and publish only when authorized; do not fake self-approval.

Keep credentials and VPN profiles out of Git and shared images. SSH stays disabled until enrolled locally. New VMs need their own SSH host keys and machine ID. Leave host security settings alone.

Resolve the configured guest account and discover actual Xfce monitor properties and network interfaces. Setup must preserve user edits on repeat runs. The wallpaper is applied once; its `alex@lab` text is part of the PNG. Keep the artwork unchanged unless asked to edit it. Resource profiles change CPU/RAM, never disk contents.

Before pushing, run `python3 build.py --validate` (`python` on Windows), `git diff --check`, relevant behavior checks and a secret scan. Parse changed PowerShell scripts. Check staged files. Report a failed or unavailable check honestly.

Follow an authorized Actions build to completion and check the archive, checksums and release files. Use standard Ubuntu runners and keep releases as drafts. Build success does not prove VMware, clipboard or VPN behavior. Test those on a separate imported VM. Do not rebuild just for documentation edits.

`CLAUDE.md` imports this guide. Keep one set of instructions. Report what changed, what passed and what remains.
