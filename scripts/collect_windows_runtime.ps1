param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path "$PSScriptRoot/..").Path
$pin = Get-Content "$root/windows-runtime.json" -Raw | ConvertFrom-Json
$vswhere = "${env:ProgramFiles(x86)}/Microsoft Visual Studio/Installer/vswhere.exe"
$vs = (& $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath).Trim()
$candidates = @(Get-Item "$vs/VC/Redist/MSVC/*/x64/Microsoft.VC143.CRT" | Sort-Object FullName -Descending)
$selected = $null
foreach ($candidate in $candidates) {
    $matches = $true
    foreach ($property in $pin.files.PSObject.Properties) {
        $file = Join-Path $candidate.FullName $property.Name
        if (!(Test-Path $file) -or (Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value.sha256) { $matches = $false; break }
    }
    if ($matches) { $selected = $candidate.FullName; break }
}
if (!$selected) { throw 'The reviewed x64 Microsoft runtime version/hashes are unavailable; review pins before changing them' }
if (Test-Path $OutputDirectory) { throw 'Runtime staging directory must be new' }
New-Item "$OutputDirectory/files" -ItemType Directory -Force | Out-Null
$files = @{}
foreach ($property in $pin.files.PSObject.Properties) {
    $file = Get-Item (Join-Path $selected $property.Name)
    $signature = Get-AuthenticodeSignature $file.FullName
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') { throw "Microsoft signature verification failed: $($file.Name)" }
    if ($file.Length -ne $property.Value.bytes -or $file.VersionInfo.FileVersion -ne $property.Value.version) { throw 'Runtime size/version changed' }
    Copy-Item $file.FullName "$OutputDirectory/files/$($file.Name)"
    if ((Get-FileHash "$OutputDirectory/files/$($file.Name)" -Algorithm SHA256).Hash.ToLowerInvariant() -ne $property.Value.sha256) { throw 'Runtime copy hash mismatch' }
    $files[$file.Name] = @{sha256=$property.Value.sha256; bytes=$file.Length; version=$file.VersionInfo.FileVersion; signature='Valid'; signer=$signature.SignerCertificate.Subject}
}
$redist = "$vs/Licenses/1033/Redist.txt"
if ((Get-FileHash $redist -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pin.redist_notice_sha256) { throw 'Original redistribution notice changed' }
Copy-Item $redist "$OutputDirectory/REDIST.txt"
@{version=$pin.version; architecture='x64'; source='Licensed Visual Studio 2022 VC/Redist/MSVC x64 Microsoft.VC143.CRT'; image_version=$env:ImageVersion; files=$files; redistribution_url=$pin.redistribution_url} | ConvertTo-Json -Depth 8 | Set-Content "$OutputDirectory/collection.json" -Encoding utf8
