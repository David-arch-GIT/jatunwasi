# 497_visor_registrar_recorrido.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: registrar la telemetria REAL del visor (VrApi, 1 linea por segundo) mientras la usuaria hace el
#   recorrido completo con el visor puesto. PHASE: "iniciar" (limpia logcat y graba en segundo plano),
#   "resumen" (detiene y analiza: FPS por minuto, % de segundos a tasa completa, peores momentos, GPU%,
#   temperatura, Stale, y cierres/ANR de la app).
param([string]$Phase = "resumen")
$adb = "C:\Users\Mi PC\AppData\Local\Android\Sdk\platform-tools\adb.exe"
$pkg = "com.jatunwasi.nawpaqay"
$D = "C:\UnrealProjects\JatunWasiNawpakay\Saved\ClaudeBackups"
$raw = "$D\recorrido_vrapi.txt"; $pidf = "$D\recorrido_logcat.pid"
if ($Phase -eq "iniciar") {
    & $adb logcat -c
    if (Test-Path $raw) { Remove-Item $raw }
    $p = Start-Process -FilePath $adb -ArgumentList "logcat", "-v", "time", "-s", "VrApi:I" -RedirectStandardOutput $raw -NoNewWindow -PassThru
    $p.Id | Set-Content $pidf
    "grabando (pid $($p.Id)) -> $raw"
    exit 0
}
if (Test-Path $pidf) { Stop-Process -Id ([int](Get-Content $pidf)) -Force -ErrorAction SilentlyContinue; Remove-Item $pidf }
$ls = Get-Content $raw | Where-Object { $_ -match "FPS=" }
$rows = foreach ($l in $ls) {
    [pscustomobject]@{
        t = [regex]::Match($l, '^\d+-\d+ (\d+:\d+:\d+)').Groups[1].Value
        fps = [int][regex]::Match($l, 'FPS=(\d+)/').Groups[1].Value
        hz = [int][regex]::Match($l, 'FPS=\d+/(\d+)').Groups[1].Value
        gpu = [double][regex]::Match($l, 'GPU%=([\d\.]+)').Groups[1].Value
        ms = [double][regex]::Match($l, 'CPU&GPU=([\d\.]+)').Groups[1].Value
        temp = [double][regex]::Match($l, 'Temp=([\d\.]+)').Groups[1].Value
        stale = [int][regex]::Match($l, 'Stale=(\d+)').Groups[1].Value
    }
}
$n = @($rows).Count
if ($n -eq 0) { "sin datos VrApi"; exit 1 }
$hz = ($rows | Group-Object hz | Sort-Object Count -Descending | Select-Object -First 1).Name
"segundos registrados: $n | frecuencia: $hz Hz"
"% segundos >= 95% de la tasa: " + [math]::Round(100 * @($rows | Where-Object { $_.fps -ge 0.95 * $_.hz }).Count / $n, 1)
"% segundos a media tasa o menos (<= 55%): " + [math]::Round(100 * @($rows | Where-Object { $_.fps -le 0.55 * $_.hz }).Count / $n, 1)
"FPS promedio: " + [math]::Round(($rows | Measure-Object fps -Average).Average, 1) + " | minimo: " + ($rows | Measure-Object fps -Minimum).Minimum
"GPU% promedio: " + [math]::Round(($rows | Measure-Object gpu -Average).Average * 100, 0) + " | temp ini/fin/max: " + $rows[0].temp + "/" + $rows[-1].temp + "/" + ($rows | Measure-Object temp -Maximum).Maximum
"--- por minuto (hora: fps prom / min / gpu%):"
$rows | Group-Object { $_.t.Substring(0, 5) } | % { "{0}  {1,5:N1} / {2,3} / {3,3:N0}%" -f $_.Name, ($_.Group | Measure-Object fps -Average).Average, ($_.Group | Measure-Object fps -Minimum).Minimum, (($_.Group | Measure-Object gpu -Average).Average * 100) }
"--- tramos lentos (>= 5 s seguidos por debajo del 80%):"
$run = @(); foreach ($r in $rows) { if ($r.fps -lt 0.8 * $r.hz) { $run += $r } else { if ($run.Count -ge 5) { "{0} -> {1}  ({2} s, fps prom {3:N0})" -f $run[0].t, $run[-1].t, $run.Count, ($run | Measure-Object fps -Average).Average }; $run = @() } }
if ($run.Count -ge 5) { "{0} -> {1}  ({2} s, fps prom {3:N0})" -f $run[0].t, $run[-1].t, $run.Count, ($run | Measure-Object fps -Average).Average }
"--- estabilidad:"
"app viva: " + [bool]((& $adb shell pidof $pkg).Trim())
"crash: " + @((& $adb logcat -d -b crash)).Count
"ANR/fatal: " + @((& $adb logcat -d) | Select-String "ANR in $pkg|Fatal signal|FATAL EXCEPTION").Count
