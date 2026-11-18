param(
    [Parameter(Mandatory=$true)][string]$Vmx,
    [ValidateSet('Desktop','Work')][string]$Profile = 'Work'
)
$ErrorActionPreference = 'Stop'
$vmxPath = (Resolve-Path -LiteralPath $Vmx).Path
if ([IO.Path]::GetExtension($vmxPath) -ne '.vmx') { throw 'Select a VMware VMX file' }
$text = [IO.File]::ReadAllText($vmxPath)
$suspended = [regex]::Match($text,'(?m)^checkpoint\.vmState\s*=\s*"([^"]*)"').Groups[1].Value
if ((Test-Path -LiteralPath ($vmxPath + '.lck')) -or $suspended -or (Get-ChildItem -LiteralPath (Split-Path -LiteralPath $vmxPath) -Filter '*.vmss')) {
    throw 'Kali is running or suspended. Resume it in VMware, shut it down completely and close its tab first'
}
$config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'blueprint.json') -Raw | ConvertFrom-Json
$selected = $config.profiles.$Profile
if ($null -eq $selected -or [int]$selected.cpus -lt 1 -or [int]$selected.memory_mb -lt 2048) { throw 'Invalid resource profile' }
$values = @{numvcpus=[string]$selected.cpus;'cpuid.coresPerSocket'=[string]$selected.cpus;memsize=[string]$selected.memory_mb}
$updated = $text
foreach ($name in $values.Keys) {
    $pattern = '(?m)^' + [regex]::Escape($name) + '\s*=.*$'
    if ([regex]::Matches($updated,$pattern).Count -ne 1) { throw ('Missing or duplicate VMX setting: ' + $name) }
    $updated = [regex]::Replace($updated,$pattern,($name + ' = "' + $values[$name] + '"'))
}
if ($updated -ne $text) {
    $backup = $vmxPath + '.before-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
    Copy-Item -LiteralPath $vmxPath -Destination $backup -ErrorAction Stop
    [IO.File]::WriteAllText($vmxPath,$updated,[Text.UTF8Encoding]::new($false))
}
Write-Output ('Selected ' + $Profile + '. Disk size and existing guest files were preserved.')
