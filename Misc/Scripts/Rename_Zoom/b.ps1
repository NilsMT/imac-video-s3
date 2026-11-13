# Prepends the NUMBER from the WAV file name to each folder name.
#   Folder 174534 containing ZOOM0054_Tr4.WAV  ->  0054-174534
#
# Usage:
#   .\prepend_number.ps1 -DryRun    # only shows what would happen
#   .\prepend_number.ps1            # actually renames

param(
    [switch]$DryRun
)

$root = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
Write-Host "Looking in: $root"
Write-Host ""

foreach ($dir in @(Get-ChildItem -LiteralPath $root -Directory)) {

    # Collect the numbers from ZOOMxxxx*.WAV files in the folder
    $numbers = @()
    foreach ($f in @(Get-ChildItem -LiteralPath $dir.FullName -File | Where-Object { $_.Extension -ieq '.wav' })) {
        if ($f.BaseName -match '^ZOOM(\d+)(_.*)?$') {
            $numbers += $Matches[1]
        }
    }
    $numbers = @($numbers | Select-Object -Unique)

    if ($numbers.Count -eq 0) {
        Write-Host "SKIP  $($dir.Name): no ZOOMxxxx*.WAV file found"
        continue
    }
    if ($numbers.Count -gt 1) {
        Write-Host "SKIP  $($dir.Name): WAV files have different numbers ($($numbers -join ', '))"
        continue
    }

    $number = $numbers[0]

    # Already prefixed? Leave it alone.
    if ($dir.Name -like "$number-*") {
        Write-Host "OK    $($dir.Name): already has the number"
        continue
    }

    $newName = "$number-$($dir.Name)"

    if (Test-Path -LiteralPath (Join-Path $root $newName)) {
        Write-Host "SKIP  $($dir.Name): '$newName' already exists"
        continue
    }

    if ($DryRun) {
        Write-Host "WOULD RENAME  $($dir.Name) -> $newName"
    }
    else {
        Rename-Item -LiteralPath $dir.FullName -NewName $newName
        Write-Host "RENAMED  $($dir.Name) -> $newName"
    }
}

Write-Host ""
Read-Host "Done. Press Enter to close"