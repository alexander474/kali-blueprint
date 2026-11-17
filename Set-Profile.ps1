param(
    [Parameter(Mandatory=$true)][string]$Vmx,
    [ValidateSet('Desktop','Work')][string]$Profile = 'Work'
)
$ErrorActionPreference = 'Stop'
$vmxPath = (Resolve-Path -LiteralPath $Vmx).Path
if ([IO.Path]::GetExtension($vmxPath) -ne '.vmx') { throw 'Select a VMware VMX file' }
if (Test-Path -LiteralPath ($vmxPath + '.lck')) { throw 'Shut down Kali and close its VMware tab first' }
$config = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'blueprint.json') -Raw | ConvertFrom-Json
$selected = $config.profiles.$Profile
if ($null -eq $selected -or [int]$selected.cpus -lt 1 -or [int]$selected.memory_mb -lt 2048) { throw 'Invalid resource profile' }
$values = @{numvcpus=[string]$selected.cpus;'cpuid.coresPerSocket'=[string]$selected.cpus;memsize=[string]$selected.memory_mb}
$text = [IO.File]::ReadAllText($vmxPath)
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
