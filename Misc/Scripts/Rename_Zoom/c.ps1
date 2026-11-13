# Renames the WAV files inside each NUMBER-TIME folder:
#   0054-174534\ZOOM0054_Tr4.WAV  ->  0054-174534\174534_Tr4.WAV
#
# Usage:
#   .\rename_wav.ps1 -DryRun    # only shows what would happen
#   .\rename_wav.ps1            # actually renames

param(
    [switch]$DryRun
)

$root = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
Write-Host "Looking in: $root"
Write-Host ""

# Only folders already named NUMBER-TIME (e.g. 0054-174534); capture the time part
$folders = @(Get-ChildItem -LiteralPath $root -Directory | Where-Object { $_.Name -match '^\d+-(\d+)$' })

if ($folders.Count -eq 0) {
    Write-Host "No NUMBER-TIME folders found here."
}

foreach ($dir in $folders) {
    $null = $dir.Name -match '^\d+-(\d+)$'
    $time = $Matches[1]

    $wavs = @(Get-ChildItem -LiteralPath $dir.FullName -File | Where-Object { $_.Extension -ieq '.wav' })

    if ($wavs.Count -eq 0) {
        Write-Host "SKIP  $($dir.Name): no WAV file found"
        continue
    }

    foreach ($f in $wavs) {
        # ZOOM0054_Tr4  ->  suffix "_Tr4"  (empty if there is none)
        if ($f.BaseName -notmatch '^ZOOM\d+(.*)$') {
            if ($f.BaseName -like "$time*") {
                Write-Host "OK    $($dir.Name)\$($f.Name): already renamed"
            }
            else {
                Write-Host "SKIP  $($dir.Name)\$($f.Name): unexpected file name"
            }
            continue
        }

        $suffix  = $Matches[1]
        $newName = "$time$suffix$($f.Extension)"

        if (Test-Path -LiteralPath (Join-Path $dir.FullName $newName)) {
            Write-Host "SKIP  $($dir.Name)\$($f.Name): '$newName' already exists"
            continue
        }

        if ($DryRun) {
            Write-Host "WOULD RENAME  $($dir.Name)\$($f.Name) -> $newName"
        }
        else {
            Rename-Item -LiteralPath $f.FullName -NewName $newName
            Write-Host "RENAMED  $($dir.Name)\$($f.Name) -> $newName"
        }
    }
}

Write-Host ""
Read-Host "Done. Press Enter to close"