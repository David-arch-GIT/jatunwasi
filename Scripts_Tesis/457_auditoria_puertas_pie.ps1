# 457_auditoria_puertas_pie.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: repetir SOLO el tramo de puertas de la auditoria 456 (alli se pasaron indices en vez de
#   nombres). Convai APAGADO (400). Por puerta: acercarse 1.6 m, leer giro de hojas; luego alejarse y
#   leer (deben cerrar). Salida auditoria_puertas.json + errores del log.
$S = "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis"
$D = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
$API = "http://localhost:8090/api/editor"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
$all = [ordered]@{}
function Invoke-Py($file, $pre, $outName, $key) {
    $o = "$D/$outName"; if (Test-Path $o) { Remove-Item $o }
    $code = $pre + "`nexec(open(r'$S/$file', encoding='utf-8-sig').read())"
    Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script=$code} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 300 | Out-Null
    $k = 0; while (-not (Test-Path $o) -and $k -lt 240) { Start-Sleep -Milliseconds 500; $k++ }
    $all[$key] = if (Test-Path $o) { Get-Content $o -Raw | ConvertFrom-Json } else { "sin salida" }
}
function Wait-Secs($s) { $t0 = Get-Date; while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 500 } }
$logStart = (Get-Item $LOG).Length
Invoke-Py "400_ue_test_locomocion_pie.py" "PHASE='convai_off'" "test400_convai_off.json" "convai_off"
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep 1; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 60)
Wait-Secs 10
foreach ($n in "PUERTA_Templo", "PUERTA_Hacienda", "PUERTA_Convento_A", "PUERTA_Convento_B") {
    Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='cerca_$n'" "test428_cerca_$n.json" "cerca_$n"
    Wait-Secs 3
    Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='leer'" "test428_leer.json" "leer_$n"
}
Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='lejos'" "test428_lejos.json" "lejos"
Wait-Secs 4
Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='leer'" "test428_leer.json" "leer_lejos"
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Wait-Secs 5
Invoke-Py "400_ue_test_locomocion_pie.py" "PHASE='convai_on'" "test400_convai_on.json" "convai_on"
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null
$rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$all["log_errores"] = @($delta -split "`n" | Where-Object { $_ -match "Error|Accessed None|Blueprint Runtime|Ensure|Assertion" -and $_ -notmatch "LogPython|execute_script" } | Select-Object -First 40)
$all | ConvertTo-Json -Depth 8 -Compress | Set-Content "$D/auditoria_puertas.json" -Encoding utf8
"OK"
