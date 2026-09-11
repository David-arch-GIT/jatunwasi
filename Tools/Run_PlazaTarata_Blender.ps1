$ErrorActionPreference = "Stop"

$Project = "C:\UnrealProjects\JatunWasiNawpakay"
$Script  = Join-Path $Project "Tools\JWN_Blender_PlazaTarata_Master.py"
$OutDir  = Join-Path $Project "External\BlenderGenerated\PlazaTarata"
$LogDir  = Join-Path $Project "Saved\Blender"
$LogFile = Join-Path $LogDir "PlazaTarata_Build.log"
$SuccessMarker = "JWN_PLAZA_BLENDER_BUILD=SUCCESS_V6_ARCHITECTURAL_QA"

$Expected = @(
    "JWN_PlazaTarata_Master.blend",
    "SM_PLZT_Hardscape.fbx",
    "SM_PLZT_GardenArchitecture.fbx",
    "SM_PLZT_CentralFountain.fbx",
    "SM_PLZT_Bench.fbx",
    "SM_PLZT_ColonialLamp.fbx",
    "SM_PLZT_GardenFence.fbx",
    "PlazaTarata_layout.json"
)

Write-Host "=== JATUN WASI - PLAZA TARATA BLENDER V6 ===" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $Script)) {
    Write-Host "ERROR: No existe el generador: $Script" -ForegroundColor Red
    exit 10
}

$Candidates = @()
$cmd = Get-Command blender.exe -ErrorAction SilentlyContinue
if ($cmd) { $Candidates += $cmd.Source }

$BlenderRoot = "C:\Program Files\Blender Foundation"
if (Test-Path -LiteralPath $BlenderRoot) {
    $Candidates += Get-ChildItem -Path $BlenderRoot -Filter blender.exe -File -Recurse -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty FullName
}

$Blender = $Candidates |
    Where-Object { $_ -and (Test-Path -LiteralPath $_) } |
    Sort-Object -Unique |
    Select-Object -Last 1

if (-not $Blender) {
    Write-Host "ERROR: No pude localizar blender.exe." -ForegroundColor Red
    exit 11
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

# Preserve previous output but remove it from the active output folder so an old
# .blend/FBX can never masquerade as a fresh successful build.
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupDir = Join-Path $LogDir ("PlazaTarata_PreV6_" + $stamp)
$OldFiles = @()

foreach ($name in $Expected) {
    $f = Join-Path $OutDir $name
    if (Test-Path -LiteralPath $f) { $OldFiles += $f }
}

if ($OldFiles.Count -gt 0) {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
    foreach ($f in $OldFiles) {
        Copy-Item -LiteralPath $f -Destination $BackupDir -Force
        Remove-Item -LiteralPath $f -Force
    }
    Write-Host "BACKUP_PREVIOUS_OUTPUT=$BackupDir" -ForegroundColor DarkCyan
}

$BuildStart = Get-Date

Write-Host "BLENDER=$Blender" -ForegroundColor Green
Write-Host "SCRIPT=$Script" -ForegroundColor Green
Write-Host "OUTPUT=$OutDir" -ForegroundColor Green
Write-Host ""
Write-Host "Ejecutando Blender V6. No cierres esta ventana..." -ForegroundColor Cyan

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $Blender
$psi.Arguments = '--background --factory-startup --python "' + $Script + '"'
$psi.UseShellExecute = $false
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.CreateNoWindow = $true

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $psi
[void]$p.Start()
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()
$p.WaitForExit()

@(
    "=== STDOUT ==="
    $stdout
    ""
    "=== STDERR ==="
    $stderr
    ""
    "EXIT_CODE=$($p.ExitCode)"
) | Set-Content -LiteralPath $LogFile -Encoding UTF8

$Missing = @()
$Stale = @()

foreach ($name in $Expected) {
    $f = Join-Path $OutDir $name
    if (-not (Test-Path -LiteralPath $f)) {
        $Missing += $name
    } else {
        $item = Get-Item -LiteralPath $f
        if ($item.LastWriteTime -lt $BuildStart.AddSeconds(-2)) {
            $Stale += $name
        }
    }
}

$HasMarker = $stdout.Contains($SuccessMarker)
$HasTraceback = $stderr.Contains("Traceback") -or $stdout.Contains("Traceback")
$HasQAFailure = $stderr.Contains("APPROVED_MASTER_QA_FAILED") -or $stdout.Contains("APPROVED_MASTER_QA_FAILED")

Write-Host ""

if ($HasMarker -and -not $HasTraceback -and -not $HasQAFailure -and $Missing.Count -eq 0 -and $Stale.Count -eq 0) {
    Write-Host "PLAZA_BLENDER_BUILD=SUCCESS_V6" -ForegroundColor Green
    Write-Host "QA arquitectónico y soporte físico superados." -ForegroundColor Green
    Get-ChildItem -LiteralPath $OutDir |
        Select-Object Name,Length,LastWriteTime |
        Format-Table -AutoSize
    Start-Process explorer.exe $OutDir
    exit 0
}

Write-Host "PLAZA_BLENDER_BUILD=FAILED_REAL" -ForegroundColor Red
if (-not $HasMarker) { Write-Host "Falta marcador de éxito V6." -ForegroundColor Yellow }
if ($HasTraceback) { Write-Host "El log contiene Traceback." -ForegroundColor Red }
if ($HasQAFailure) { Write-Host "El QA interno rechazó la geometría." -ForegroundColor Red }

if ($Missing.Count -gt 0) {
    Write-Host "Archivos no generados:" -ForegroundColor Red
    $Missing | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}
if ($Stale.Count -gt 0) {
    Write-Host "Archivos no regenerados:" -ForegroundColor Red
    $Stale | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
}

Write-Host "LOG=$LogFile" -ForegroundColor Yellow
if (Test-Path -LiteralPath $BackupDir) {
    Write-Host "BACKUP_PREVIOUS_OUTPUT=$BackupDir" -ForegroundColor Yellow
}
Write-Host "NO vuelvas a ejecutar. Envíame el log." -ForegroundColor Yellow
exit 12
