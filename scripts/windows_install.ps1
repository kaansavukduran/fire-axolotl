param([ValidateSet('Install', 'Uninstall')][string]$Mode = 'Install')
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path "$PSScriptRoot/..").Path
$evidence = Join-Path $root 'work/windows-installer-test'
New-Item $evidence -ItemType Directory -Force | Out-Null

function BrowserChoice {
    $key = 'HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice'
    return (Get-ItemProperty $key -ErrorAction SilentlyContinue).ProgId
}

if ($Mode -eq 'Install') {
    $files = @(Get-ChildItem "$root/dist/windows-release/*-Setup.exe")
    if ($files.Count -ne 1) { throw 'Expected one Windows Setup.exe' }
    $setup = $files[0].FullName
    if ((Get-Item $setup).VersionInfo.ProductName -ne 'Fire Axolotl') { throw 'Installer extraction wrapper has the wrong product branding' }
    $signature = Get-AuthenticodeSignature $setup
    if ($signature.Status -ne 'NotSigned') { throw "Unexpected developer-installer signing state: $($signature.Status)" }
    $destination = Join-Path $env:RUNNER_TEMP 'FireAxolotlInstalled'
    if (Test-Path $destination) { throw 'Clean installation target must not exist' }
    $firefox = 'C:\Program Files\Mozilla Firefox\firefox.exe'
    $firefoxHash = if (Test-Path $firefox) { (Get-FileHash $firefox -Algorithm SHA256).Hash } else { $null }
    $choice = BrowserChoice
    $sentinel = Join-Path $env:APPDATA "Mozilla/Firefox/fire-axolotl-install-check-$([guid]::NewGuid()).txt"
    New-Item (Split-Path $sentinel) -ItemType Directory -Force | Out-Null
    [IO.File]::WriteAllText($sentinel, 'Firefox profile data must survive Fire Axolotl install/uninstall.')
    $ini = Join-Path $evidence 'install.ini'
    [IO.File]::WriteAllText($ini, "[Install]`r`nInstallDirectoryPath=$destination`r`nDesktopShortcut=false`r`nStartMenuShortcuts=true`r`nTaskbarShortcut=false`r`nMaintenanceService=false`r`nPreventRebootRequired=true`r`n")
    $process = Start-Process $setup -ArgumentList @('/S', "/INI=$ini") -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Windows installation failed: $($process.ExitCode)" }
    $binary = Join-Path $destination 'fire-axolotl.exe'
    if (!(Test-Path $binary) -or !(Test-Path "$destination/uninstall/helper.exe")) { throw 'Installed browser or uninstaller missing' }
    $env:AION_INSTALLED_DIRECTORY = $destination
    python "$PSScriptRoot/verify_windows_installation.py"
    if ($LASTEXITCODE -ne 0) { throw 'Installed native payload differs from the verified ZIP' }
    if ((BrowserChoice) -ne $choice) { throw 'Installation changed the default browser without consent' }
    $links = @("$env:APPDATA/Microsoft/Windows/Start Menu/Programs/Fire Axolotl.lnk", "$env:ProgramData/Microsoft/Windows/Start Menu/Programs/Fire Axolotl.lnk")
    $link = $links | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (!$link) { throw 'Fire Axolotl Start Menu shortcut missing' }
    $shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut($link)
    if ($shortcut.TargetPath -ne $binary) { throw 'Start Menu shortcut targets another browser' }
    @{payload_verified=$true; installed_binary=$binary; install_directory=$destination; authenticode_status=[string]$signature.Status; default_browser=$choice; firefox_binary=$firefox; firefox_sha256=$firefoxHash; firefox_sentinel=$sentinel; start_menu_shortcut=$link} | ConvertTo-Json -Depth 5 | Set-Content "$evidence/installation.json" -Encoding utf8
    "AION_NATIVE_BINARY=$binary" | Out-File $env:GITHUB_ENV -Append -Encoding utf8
} else {
    $state = Get-Content "$evidence/installation.json" -Raw | ConvertFrom-Json
    $probe = Get-Content "$evidence/profile-probe.json" -Raw | ConvertFrom-Json
    $process = Start-Process "$($state.install_directory)/uninstall/helper.exe" -ArgumentList '/S' -Wait -PassThru
    if ($process.ExitCode -ne 0) { throw "Windows uninstallation failed: $($process.ExitCode)" }
    if (Test-Path $state.installed_binary) { throw 'Installed browser still exists after uninstall' }
    if (!(Test-Path $state.firefox_sentinel) -or !(Test-Path $probe.marker)) { throw 'Uninstallation removed user profile data' }
    if ([IO.File]::ReadAllText($state.firefox_sentinel) -ne 'Firefox profile data must survive Fire Axolotl install/uninstall.' -or (Get-FileHash $probe.marker -Algorithm SHA256).Hash.ToLowerInvariant() -ne $probe.marker_sha256) { throw 'User profile sentinel contents changed' }
    if ((BrowserChoice) -ne $state.default_browser) { throw 'Uninstallation changed the default browser' }
    if ($state.firefox_sha256 -and (Get-FileHash $state.firefox_binary -Algorithm SHA256).Hash -ne $state.firefox_sha256) { throw 'Existing Firefox executable was changed' }
    @{profiles_preserved=$true; default_browser_preserved=$true; firefox_binary_checked=[bool]$state.firefox_sha256; firefox_binary_preserved=$(if ($state.firefox_sha256) { $true } else { $null }); own_default_profile_root=$probe.default_profile_root} | ConvertTo-Json -Depth 5 | Set-Content "$evidence/uninstallation.json" -Encoding utf8
    Remove-Item $state.firefox_sentinel, $probe.marker
}
