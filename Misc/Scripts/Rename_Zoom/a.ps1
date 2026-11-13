# Renames ZOOMxxxx folders to the TIME part of the .hprj file inside them.
# Example: ZOOM0001\261107-174534.hprj  ->  folder renamed to 174534
#
# Usage:
#   .\rename_zoom.ps1 -DryRun    # only shows what would happen
#   .\rename_zoom.ps1            # actually renames

param(
    [switch]$DryRun
)

# Work in the folder where the script is saved
$root = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
Write-Host "Looking in: $root"

$folders = @(Get-ChildItem -LiteralPath $root -Directory | Where-Object { $_.Name -match '^ZOOM\d+$' })

if ($folders.Count -eq 0) {
    Write-Host "No ZOOMxxxx folders found here."
}

foreach ($dir in $folders) {
    $files = @(Get-ChildItem -LiteralPath $dir.FullName -File | Where-Object { $_.Extension -ieq '.hprj' })

    if ($files.Count -eq 0) {
        Write-Host "SKIP  $($dir.Name): no .hprj file found"
        continue
    }

    if ($files.Count -gt 1) {
        Write-Host "SKIP  $($dir.Name): more than one .hprj file found"
        continue
    }

    # 261107-174534.hprj -> 261107-174534 -> 174534
    $base = $files[0].BaseName

    if ($base -notmatch '^\d+-(\d+)$') {
        Write-Host "SKIP  $($dir.Name): unexpected file name '$($files[0].Name)'"
        continue
    }

    $time = $Matches[1]

    if (Test-Path -LiteralPath (Join-Path $root $time)) {
        Write-Host "SKIP  $($dir.Name): '$time' already exists"
        continue
    }

    if ($DryRun) {
        Write-Host "WOULD RENAME  $($dir.Name) -> $time"
    }
    else {
        Rename-Item -LiteralPath $dir.FullName -NewName $time
        Write-Host "RENAMED  $($dir.Name) -> $time"
    }
}

Write-Host ""
Read-Host "Done. Press Enter to close"