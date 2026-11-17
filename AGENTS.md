# Kali Blueprint

## Purpose and scope

Build an ordinary Kali Linux/Xfce VMware image with the owner's desktop preferences, using pinned upstream debos recipes and GitHub Actions. Keep the project small and usable on different Windows hosts. This is an independent personal project, not an official Kali distribution or a customer environment.

Retain the standard Kali toolset. Do not import customer allowlists, command wrappers, corporate integrations or unrelated agent plugins. Do not change host antivirus, VBS, firewall, router or credential settings as a side effect of VM work.

## Read the minimum needed

Start with `git status --short --branch`, `README.md`, `blueprint.json` and the files affected by the request. Check the diff before editing. Preserve existing changes; never reset, clean or overwrite another person's work to obtain a clean checkout.

Use `rg`, focused reads and local tools first. Batch independent checks and return concise output. Prefer Git, the GitHub CLI or a suitable API/connector over browser automation. A browser is a fallback for a missing capability or the correct authenticated account, not the default for reading files, logs or checks.

Read only relevant log tails or error excerpts. Use one bounded watch with backoff for builds; avoid repeated full logs, screenshots and unchanged status reports. Do not start extra models or agents unless requested. Do not promise an exact token cost or saving without measurements.

## Project map and contracts

- `blueprint.json`: sole source of build settings, user/hostname and host resource profiles. Default identity is `alex@lab`; the initial password is deliberately public: `kali`.
- `build.py`: validates settings, fetches the pinned upstream revision, installs the guest overlay, builds and packages the VMware image. A changed upstream recipe must be reviewed; do not disable mismatch checks to force a build through.
- `guest/configure.py`: runs only inside the build filesystem. Resolve the configured account through the account database; never assume `/home/kali`.
- `guest/session.py`: runs as the real desktop user with Xfce/DBus. Discover monitor properties and network interfaces rather than hardcoding host-specific names or addresses.
- `guest/wallpaper.png`: public bundled artwork. Its `alex@lab` label is baked into the PNG; account changes do not rewrite it. Preserve the original bytes unless an image change is requested.
- `guest/network.py` and `guest/conky.conf`: local display information. A detected VPN interface is not proof of target connectivity.
- `Personalize.ps1` / `Set-Profile.ps1`: local Windows helpers. Keep existing files and take unique backups before managed changes. Resource profiles change CPU/RAM, never shrink a disk.
- `.github/workflows/build.yml`: PR/source checks and explicitly dispatched builds on `main`, using a standard GitHub-hosted runner. Build output is a draft release with split archives and checksums.

## Preserve users and data

Operate on a new imported VM for runtime validation. Do not replace or start an existing VM, delete snapshots or backups, or move user disks without authorization. Keep old releases and versions unless removal is specifically requested.

Desktop setup must be repeatable: do not overwrite manually edited configuration or reapply the bundled wallpaper on every login. Keep custom wallpaper selection explicit. Any startup retry must be bounded and leave a useful error rather than hang indefinitely.

The shared image must contain no personal SSH private keys, VPN profiles, tokens, real passwords, host-specific addresses or enrolled authorized keys. SSH starts disabled; imports initialize their own SSH host keys and machine identity. Never turn off host verification or forward the SSH agent as a shortcut.

Only read files within the requested project scope. Do not search credential stores, browser profiles or unrelated study documents. Keep private overrides, temporary checks, reports and build logs in ignored `.local/` or an authorized external work directory. Do not commit generated disks, archives, caches or a narrative history of experiments. The bundled public artwork is intentional; personal paths and cloud-service references are not portable configuration.

## Authentication and GitHub

The repository is `alexander474/kali-blueprint`. Verify the authenticated author before any remote write. Do not silently use a work account or change global Git/SSH authentication. For Git operations, select the owner's private GitHub public identity through the existing 1Password SSH agent; never export the private key. Commit using the owner's configured name and GitHub no-reply address.

SSH Git access does not provide REST API credentials. Use an already authorized personal CLI/connector when available; otherwise finish the code and checks before reporting the specific missing capability. Never scrape a token from another application or create credentials to avoid a handoff.

Use a feature branch and a focused PR. Inspect staged content and run a secret scan before pushing. Keep PR descriptions about final behavior and actual validation. GitHub does not permit authors to approve their own PR; do not fabricate a review or approval. Merge or publish only within the user's explicit authorization. Ordinary preparation and reversible fixes do not need repeated permission requests; existing authorization persists.

## Validation and delivery

1. Run `python3 build.py --validate` (`python` on Windows). This checks source/configuration only; it does not build or boot a VM.
2. If PowerShell changes, parse the scripts with `System.Management.Automation.Language.Parser::ParseFile` and check relevant behavior. If runtime or build behavior changes, add focused temporary checks for the affected contract, including repeat runs and preservation of user changes where relevant. Avoid tests that merely duplicate implementation.
3. Check `git diff --check`, review the staged file list and diff, and scan staged content/history for secrets with a trusted available scanner. A scanner crash or a missing scanner is not a clean scan.
4. After PR checks pass, run a full Actions image build when build inputs changed and the user has authorized it. Do not rebuild a large image for agent-documentation-only changes. Follow an authorized build to completion; inspect a failure before retrying.
5. Verify packaging, archive test, checksum entries and release assets. Keep the release a draft until publication is requested. CI success does not establish native VMware or VPN behavior. State what was built, what was tested and which local checks remain.

Keep durable rules here and normal usage in `README.md`. Update them when behavior changes. `CLAUDE.md` imports this file; do not maintain a second copy of these rules. For long tasks, keep a short checkpoint in ignored `.local/` with the current branch/commit, verified checks and remaining work; do not claim completion from a previous agent's summary without checking the evidence.
