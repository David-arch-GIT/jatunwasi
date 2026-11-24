# 487_test_adela_guia_pie.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: orquestar 486 en PIE con Convai APAGADO (400): intro -> "Sigueme" -> visitante 3 m detras
#   hasta el Templo -> narracion + pregunta (sin pisarse) -> se aleja y vuelve -> tramo 2 -> se queda quieto
#   ("No te quedes atras" 1 vez) -> microfono abierto (Adela calla y se detiene) -> final en el salon.
#   Muestrea cada ~1 s: estado, voces simultaneas, anim. Salida test_adela_guia.json + errores de log.
$S = "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis"
$D = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
$API = "http://localhost:8090/api/editor"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
$muestras = New-Object System.Collections.ArrayList
function Invoke-Fase($pre, $etiqueta) {
    $ph = ([regex]::Match($pre, "PHASE='(\w+)'")).Groups[1].Value
    $o = "$D/test486_$ph.json"; if (Test-Path $o) { Remove-Item $o }
    $code = $pre + "`nexec(open(r'$S/486_ue_test_adela_guia_pie.py', encoding='utf-8-sig').read())"
    Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script=$code} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 120 | Out-Null
    $k = 0; while (-not (Test-Path $o) -and $k -lt 200) { Start-Sleep -Milliseconds 100; $k++ }
    $r = if (Test-Path $o) { Get-Content $o -Raw | ConvertFrom-Json } else { $null }
    if ($r) { $r | Add-Member -NotePropertyName etiqueta -NotePropertyValue $etiqueta -Force; [void]$muestras.Add($r) }
    return $r
}
function Wait-Secs($s) { $t0 = Get-Date; while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 200 } }
function Get-Estado($r) { if ($r -and $r.dbg) { ([regex]::Match($r.dbg, "estado=(\w+)")).Groups[1].Value } else { "?" } }
$logStart = (Get-Item $LOG).Length
$o = "$D/test400_convai_off.json"; if (Test-Path $o) { Remove-Item $o }
Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script="PHASE='convai_off'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
$k = 0; while (-not (Test-Path $o) -and $k -lt 120) { Start-Sleep -Milliseconds 250; $k++ }
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep -Milliseconds 300; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 200)

# 1) intro (27 s) -> debe arrancar el tramo 0
for ($i = 0; $i -lt 34; $i += 2) { Invoke-Fase "PHASE='estado'" "intro" | Out-Null; Wait-Secs 2 }
# 2) seguir 3 m detras hasta que llegue a la estacion del Templo (max 100 s)
for ($i = 0; $i -lt 100; $i++) { $r = Invoke-Fase "PHASE='seguir'; DIST=300" "seguir_t0"; if ((Get-Estado $r) -eq "EnEstacion") { break }; Wait-Secs 0.8 }
# 3) acercarse a la estacion: narracion del templo + pregunta (esperar 30 s)
Invoke-Fase "PHASE='tp'; TP=(-60,9400)" "llega_templo" | Out-Null
for ($i = 0; $i -lt 32; $i += 2) { Invoke-Fase "PHASE='estado'" "templo_pregunta" | Out-Null; Wait-Secs 2 }
# 4) se aleja (entra al templo) y vuelve -> tramo 1
Invoke-Fase "PHASE='tp'; TP=(0,12000)" "dentro_templo" | Out-Null; Wait-Secs 3
Invoke-Fase "PHASE='tp'; TP=(-60,9300)" "vuelve" | Out-Null
for ($i = 0; $i -lt 6; $i++) { Invoke-Fase "PHASE='estado'" "vuelve" | Out-Null; Wait-Secs 1 }
# 5) se queda quieto -> Adela se aleja, espera y avisa UNA vez
for ($i = 0; $i -lt 20; $i++) { Invoke-Fase "PHASE='estado'" "quieto" | Out-Null; Wait-Secs 1 }
# 6) microfono abierto: Adela calla y se detiene
Invoke-Fase "PHASE='seguir'; DIST=300" "acerca" | Out-Null; Wait-Secs 2
Invoke-Fase "PHASE='mic'; ABIERTO=True" "mic_abierto" | Out-Null
for ($i = 0; $i -lt 4; $i++) { Invoke-Fase "PHASE='estado'" "mic_abierto" | Out-Null; Wait-Secs 1 }
Invoke-Fase "PHASE='mic'; ABIERTO=False" "mic_cerrado" | Out-Null
for ($i = 0; $i -lt 4; $i++) { Invoke-Fase "PHASE='seguir'; DIST=300" "tras_mic" | Out-Null; Wait-Secs 1 }
# 7) estacion Hacienda y final
Invoke-Fase "PHASE='forzar'; I=2" "forzar_hacienda" | Out-Null
Invoke-Fase "PHASE='tp'; TP=(-7300,-700)" "llega_hacienda" | Out-Null
for ($i = 0; $i -lt 6; $i++) { Invoke-Fase "PHASE='estado'" "hacienda" | Out-Null; Wait-Secs 1 }
Invoke-Fase "PHASE='tp'; TP=(-8300,-1700,440)" "sube_piso2" | Out-Null
for ($i = 0; $i -lt 3; $i++) { Invoke-Fase "PHASE='estado'" "final" | Out-Null; Wait-Secs 1 }

Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Wait-Secs 5
$o = "$D/test400_convai_on.json"; if (Test-Path $o) { Remove-Item $o }
Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script="PHASE='convai_on'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
$k = 0; while (-not (Test-Path $o) -and $k -lt 120) { Start-Sleep -Milliseconds 250; $k++ }
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$errs = @($delta -split "`n" | Where-Object { $_ -match "Blueprint Runtime|Accessed None|\[Compiler\]|Error: " -and $_ -notmatch "LogPython|ensure|LogOutputDevice" })
@{ muestras = $muestras; errores = $errs.Count; ej = ($errs | Select-Object -First 5); convai_on = (Get-Content $o -Raw) } | ConvertTo-Json -Depth 6 -Compress | Set-Content "$D/test_adela_guia.json" -Encoding utf8
"OK muestras=" + $muestras.Count + " errores=" + $errs.Count
