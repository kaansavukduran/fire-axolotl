$ErrorActionPreference = 'Stop'
$pin = Get-Content "$PSScriptRoot/../windows-build.json" -Raw | ConvertFrom-Json
$installer = Join-Path $env:RUNNER_TEMP 'MozillaBuildSetup.exe'
Invoke-WebRequest $pin.mozillabuild.url -OutFile $installer
if ((Get-FileHash $installer -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pin.mozillabuild.sha256) {
    throw 'MozillaBuild checksum mismatch'
}
$process = Start-Process $installer -ArgumentList '/S' -Wait -PassThru
if ($process.ExitCode -ne 0) { throw "MozillaBuild installation failed: $($process.ExitCode)" }
if (!(Test-Path 'C:\mozilla-build\VERSION')) { throw 'MozillaBuild installation is missing' }
if ((Get-Content 'C:\mozilla-build\VERSION' -Raw).Trim() -ne $pin.mozillabuild.version) { throw 'Unexpected MozillaBuild version' }
'MOZILLABUILD=C:\mozilla-build\' | Out-File $env:GITHUB_ENV -Append -Encoding utf8
'C:\mozilla-build\msys2\usr\bin' | Out-File $env:GITHUB_PATH -Append -Encoding utf8
'C:\mozilla-build\bin' | Out-File $env:GITHUB_PATH -Append -Encoding utf8
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem' -Name LongPathsEnabled -Value 1 -PropertyType DWord -Force | Out-Null
Get-PSDrive C, D | Select-Object Name, Used, Free
