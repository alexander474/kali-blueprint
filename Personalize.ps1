param(
    [Parameter(Mandatory=$true)][string]$Target,
    [Parameter(Mandatory=$true)][string]$Wallpaper,
    [string]$PublicIdentityFile
)
$ErrorActionPreference = 'Stop'
if ($Target -notmatch '^[A-Za-z0-9][A-Za-z0-9_.@-]*$') { throw 'Use a trusted SSH alias or user@IPv4 address' }
$image = Get-Item -LiteralPath (Resolve-Path -LiteralPath $Wallpaper).Path
if ($image.Extension.ToLowerInvariant() -notin @('.png','.jpg','.jpeg') -or $image.Length -gt 32MB) { throw 'Choose a local PNG or JPEG smaller than 32 MiB' }
$stream = [IO.File]::OpenRead($image.FullName)
try { $header = New-Object byte[] 8; $read = $stream.Read($header,0,8) } finally { $stream.Dispose() }
$signature = [BitConverter]::ToString($header)
if ($read -lt 3 -or ($signature -ne '89-50-4E-47-0D-0A-1A-0A' -and -not $signature.StartsWith('FF-D8-FF'))) { throw 'Wallpaper content must be PNG or JPEG' }
$sshOptions = @('-o','StrictHostKeyChecking=yes','-o','ForwardAgent=no')
if ($PublicIdentityFile) {
    $identity = (Resolve-Path -LiteralPath $PublicIdentityFile).Path
    if ([IO.Path]::GetExtension($identity) -ne '.pub') { throw 'Use the public identity file; keep the private key in your agent' }
    $sshOptions += @('-i',$identity,'-o','IdentitiesOnly=yes')
}
& ssh @sshOptions $Target 'mkdir -p ~/.local/share/kali-blueprint ~/.config/kali-blueprint && chmod 700 ~/.local/share/kali-blueprint ~/.config/kali-blueprint'
if ($LASTEXITCODE -ne 0) { throw 'SSH failed; verify the guest fingerprint and local agent enrollment first' }
$guestImage = '.local/share/kali-blueprint/personal-wallpaper' + $image.Extension.ToLowerInvariant()
& scp @sshOptions $image.FullName ($Target + ':' + $guestImage)
if ($LASTEXITCODE -ne 0) { throw 'Wallpaper transfer failed' }
$expected = (Get-FileHash -LiteralPath $image.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$remoteHash = & ssh @sshOptions $Target ('sha256sum ~/' + $guestImage)
if ($LASTEXITCODE -ne 0 -or ($remoteHash -split '\s+')[0] -ne $expected) { throw 'Wallpaper copy verification failed' }
$settings = '{"wallpaper":"~/' + $guestImage + '"}'
$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($settings))
& ssh @sshOptions $Target ('printf %s ' + $encoded + ' | base64 -d > ~/.config/kali-blueprint/personal.json')
if ($LASTEXITCODE -ne 0) { throw 'Could not save the local wallpaper selection' }
Write-Output 'Original image copied and verified without modification. The wallpaper is applied at the next Xfce login.'
