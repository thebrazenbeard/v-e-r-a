# Read-only Vera Desktop V2 host inventory. This is NOT enrollment or proof
# that the process owning :18781 is the authenticated Vera gateway.
[CmdletBinding()]
param(
    [switch] $Inspect,
    [string] $ExpectedClientExe,
    [string] $ExpectedClientSha256
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$VeraRoot = 'D:\VERA'

if (-not $Inspect) {
    [pscustomobject]@{
        mode = 'dry-run'
        readOnly = $true
        inspectedHost = $false
        message = 'Use -Inspect in the authorized Windows session; no enrollment or installation occurs.'
    } | ConvertTo-Json -Compress
    return
}

if ($env:OS -ne 'Windows_NT') {
    throw 'Windows host required for -Inspect'
}

function Get-ListenerInventory([int] $Port) {
    try {
        $listeners = @(Get-NetTCPConnection -State Listen -ErrorAction Stop |
            Where-Object { $_.LocalPort -eq $Port })
        $onlyLoopback = $listeners.Count -gt 0
        foreach ($listener in $listeners) {
            if ($listener.LocalAddress -notin @('127.0.0.1', '::1')) {
                $onlyLoopback = $false
            }
        }
        $listenerState = 'absent'
        if ($listeners.Count -gt 0) { $listenerState = 'observed' }
        return [pscustomobject]@{
            state = $listenerState
            count = $listeners.Count
            onlyLoopback = $onlyLoopback
        }
    } catch {
        return [pscustomobject]@{ state = 'unavailable'; count = 0; onlyLoopback = $false }
    }
}

$rootPresent = Test-Path -LiteralPath $VeraRoot -PathType Container
$clientHashMatches = $false
$clientRunning = $false
$exactClientSupplied = -not [string]::IsNullOrWhiteSpace($ExpectedClientExe) -and
    $ExpectedClientSha256 -match '^[a-fA-F0-9]{64}$'

if ($exactClientSupplied) {
    try {
        $canonicalClient = [System.IO.Path]::GetFullPath($ExpectedClientExe)
        if (Test-Path -LiteralPath $canonicalClient -PathType Leaf) {
            $digest = (Get-FileHash -LiteralPath $canonicalClient -Algorithm SHA256).Hash
            $clientHashMatches = $digest -ieq $ExpectedClientSha256
            if ($clientHashMatches) {
                $matchingProcesses = @(Get-CimInstance Win32_Process -ErrorAction Stop |
                    Where-Object {
                        $_.ExecutablePath -and
                        $_.ExecutablePath.Equals($canonicalClient,
                            [System.StringComparison]::OrdinalIgnoreCase)
                    })
                $clientRunning = $matchingProcesses.Count -gt 0
            }
        }
    } catch {
        # A failed lookup never becomes proof of installed or running V2.
        $clientHashMatches = $false
        $clientRunning = $false
    }
}

$desktopLocations = @(
    [Environment]::GetFolderPath('Desktop'),
    [Environment]::GetFolderPath('CommonDesktopDirectory')
) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique
$shortcutNames = @()
foreach ($desktop in $desktopLocations) {
    if (-not (Test-Path -LiteralPath $desktop -PathType Container)) { continue }
    try {
        $shortcutNames += @(Get-ChildItem -LiteralPath $desktop -Filter '*.lnk' -File -ErrorAction Stop |
            Where-Object { $_.BaseName -match 'Vera' } |
            ForEach-Object { $_.Name })
    } catch {
        # A locked Desktop directory does not imply a clean shortcut state.
        $shortcutNames += '[shortcut inventory unavailable]'
    }
}

$v1 = Get-ListenerInventory 18777
$v2 = Get-ListenerInventory 18781

[pscustomobject]@{
    mode = 'host-inventory'
    readOnly = $true
    inspectedHost = $true
    authorizedRootPresent = $rootPresent
    expectedClientHashSupplied = $exactClientSupplied
    expectedClientHashMatches = $clientHashMatches
    expectedClientProcessObserved = $clientRunning
    legacyV1Port = $v1
    candidateV2Port = $v2
    veraDesktopShortcutNames = @($shortcutNames | Sort-Object -Unique)
    v2Authenticated = $false
    enrollmentQualified = $false
    releaseQualified = $false
    limitation = 'Ports, PIDs, executable hashes and shortcuts are observations, not server identity, owner consent, ACL, history or GUI qualification.'
} | ConvertTo-Json -Depth 5 -Compress
