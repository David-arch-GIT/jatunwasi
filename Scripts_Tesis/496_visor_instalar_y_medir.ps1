# 496_visor_instalar_y_medir.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: instalar el APK en el visor conectado por USB y medir FLUIDEZ y ESTABILIDAD de verdad:
#   - modo kiosco (no se suspende / evita el cuelgue al quitarse el visor) + guardian_pause para medir sin
#     llevarlo puesto (se restaura al final);
#   - abre la app y cada INTERVALO s registra: FPS (VrApi), GPU%/CPU%, temperatura, memoria (PSS), si el
#     proceso sigue vivo; al final busca cierres (logcat crash, dropbox ANR/crash/tombstone).
#   Parametros: -Serial (si hay 2 visores) -Minutos (duracion) -Intervalo (s entre muestras) -SinInstalar
#   (solo medir) -Puesto (la usuaria recorre con el visor PUESTO: no toca guardian_pause).
param([string]$Serial = "", [int]$Minutos = 5, [int]$Intervalo = 20, [switch]$SinInstalar, [switch]$Puesto)
$adb = "C:\Users\Mi PC\AppData\Local\Android\Sdk\platform-tools\adb.exe"
$apk = "C:\UnrealProjects\JatunWasiNawpakay\Binaries\Android\JatunWasiNawpakay-Android-Shipping-arm64.apk"
$pkg = "com.jatunwasi.nawpaqay"
$out = "C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups\visor_medicion_$(Get-Date -Format 'HHmmss').json"
$devs = @((& $adb devices) | Select-String "\tdevice$" | % { ($_ -split "\t")[0] })
if ($devs.Count -eq 0) { "NO HAY VISOR conectado/autorizado (acepta 'Permitir depuracion USB' en el visor)"; exit 1 }
if (-not $Serial) { $Serial = $devs[0] }
function A { & $adb -s $Serial @args }
$r = [ordered]@{ serial = $Serial; modelo = (A shell getprop ro.product.model).Trim(); version_so = (A shell getprop ro.build.version.incremental).Trim() }
$r.bateria = ((A shell dumpsys battery) | Select-String "level|temperature" | % { $_.Line.Trim() }) -join "; "
if (-not $SinInstalar) {
    $t0 = Get-Date
    $r.instalacion = ((A install -r $apk) | Select-Object -Last 1)
    $r.instalacion_s = [int]((Get-Date) - $t0).TotalSeconds
}
# modo kiosco (persistente hasta reiniciar el visor) + medir sin llevarlo puesto
A shell am broadcast -a com.oculus.vrpowermanager.prox_close | Out-Null
A shell settings put system screen_off_timeout 7200000 | Out-Null
if (-not $Puesto) { A shell setprop debug.oculus.guardian_pause 1 | Out-Null }
A shell am force-stop $pkg | Out-Null
Start-Sleep 2
A logcat -c | Out-Null
$act = ((A shell cmd package resolve-activity --brief $pkg) | Select-Object -Last 1).Trim()
$r.actividad = $act
A shell am start -n $act | Out-Null
$inicio = Get-Date
$muestras = @()
while (((Get-Date) - $inicio).TotalMinutes -lt $Minutos) {
    Start-Sleep $Intervalo
    $pid_ = (A shell pidof $pkg).Trim()
    $vr = (A logcat -d -s VrApi:I) | Select-String "FPS=" | Select-Object -Last 3
    $fps = @($vr | % { [regex]::Match($_.Line, 'FPS=(\d+)/(\d+)').Groups[1].Value } | Where-Object { $_ })
    $gpu = @($vr | % { [regex]::Match($_.Line, 'GPU%=([\d\.]+)').Groups[1].Value } | Where-Object { $_ })
    $cpu = @($vr | % { [regex]::Match($_.Line, 'CPU%=([\d\.]+)').Groups[1].Value } | Where-Object { $_ })
    $tmp = @($vr | % { [regex]::Match($_.Line, 'Temp=([\d\.]+)C').Groups[1].Value } | Where-Object { $_ })
    $pss = ((A shell dumpsys meminfo $pkg) | Select-String "TOTAL PSS:|TOTAL:" | Select-Object -First 1)
    $m = [ordered]@{ t_s = [int]((Get-Date) - $inicio).TotalSeconds; vivo = [bool]$pid_; fps = ($fps -join ","); gpu = ($gpu -join ","); cpu = ($cpu -join ","); temp = ($tmp -join ","); mem = if ($pss) { ($pss.Line -replace '\s+', ' ').Trim().Substring(0, [Math]::Min(60, ($pss.Line -replace '\s+', ' ').Trim().Length)) } else { "" } }
    $muestras += [pscustomobject]$m
    "{0,4}s vivo={1} FPS={2} GPU%={3} CPU%={4} Temp={5} {6}" -f $m.t_s, $m.vivo, $m.fps, $m.gpu, $m.cpu, $m.temp, $m.mem
    if (-not $pid_) { break }
}
$r.muestras = $muestras
$r.crash = @((A logcat -d -b crash) | Select-Object -Last 15)
$r.fatal = @((A logcat -d) | Select-String "FATAL|ANR in $pkg|Fatal signal|LowMemoryKiller.*$pkg|lowmemorykiller" | Select-Object -Last 10 | % { $_.Line })
$r.ue_errores = @((A logcat -d -s UE:E) | Select-Object -Last 10)
$dbx = (A shell dumpsys dropbox) | Select-String "data_app_crash|data_app_anr|SYSTEM_TOMBSTONE|system_app_anr" | Select-Object -Last 8
$r.dropbox = @($dbx | % { $_.Line.Trim() })
if (-not $Puesto) { A shell setprop debug.oculus.guardian_pause 0 | Out-Null }
$r | ConvertTo-Json -Depth 5 | Set-Content $out -Encoding utf8
"--- vivo al final: " + [bool]((A shell pidof $pkg).Trim()) + " | crash: " + $r.crash.Count + " | fatal: " + $r.fatal.Count + " | dropbox: " + $r.dropbox.Count
"guardado: $out"
