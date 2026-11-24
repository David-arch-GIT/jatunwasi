# 456_auditoria_pie_completa.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: orquestar UNA pasada PIE pre-APK con Convai APAGADO (400 convai_off/on):
#   recorrido Templo->Convento->Hacienda (barreras), 4 puertas, mirada a criatura, pozo, subida al salon
#   (446 GUIADO) y final (449). Junta todos los JSON en auditoria_pie.json y extrae errores del log.
$ErrorActionPreference = "Stop"
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
    $txt = if (Test-Path $o) { Get-Content $o -Raw } else { '{"err":"sin salida"}' }
    $all[$key] = ($txt | ConvertFrom-Json)
    return $all[$key]
}
function Wait-Secs($s) { $t0 = Get-Date; while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 500 } }
$logStart = (Get-Item $LOG).Length

Invoke-Py "400_ue_test_locomocion_pie.py" "PHASE='convai_off'" "test400_convai_off.json" "convai_off" | Out-Null
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep 1; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 60)
Wait-Secs 10

$e0 = Invoke-Py "455_ue_auditoria_pie.py" "PHASE='estado'" "test455_estado.json" "estado_inicial"
$trigs = $e0.trigs
foreach ($zona in "Templo", "Convento", "Hacienda") {
    $tn = $trigs.PSObject.Properties | Where-Object { $_.Name -like "*$zona*" -and $_.Name -notlike "*Fin*" } | Select-Object -First 1
    if ($tn) {
        $v = $tn.Value
        Invoke-Py "455_ue_auditoria_pie.py" "PHASE='tp'; TP=($($v[0]),$($v[1]),$($v[2]))" "test455_tp.json" "tp_$zona" | Out-Null
        Wait-Secs 4
        Invoke-Py "455_ue_auditoria_pie.py" "PHASE='estado'" "test455_estado.json" "estado_tras_$zona" | Out-Null
    } else { $all["tp_$zona"] = "SIN TRIGGER" }
}
foreach ($n in "PUERTA_Templo", "PUERTA_Hacienda", "PUERTA_Convento_A", "PUERTA_Convento_B") {
    Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='cerca_$n'" "test428_cerca_$n.json" "puerta_cerca_$n" | Out-Null
    Wait-Secs 3
    Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='leer'" "test428_leer.json" "puerta_leer_$n" | Out-Null
}
Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='lejos'" "test428_lejos.json" "puertas_lejos" | Out-Null
Wait-Secs 4
Invoke-Py "428_ue_test_puertas_pie.py" "PHASE='leer'" "test428_leer.json" "puertas_leer_lejos" | Out-Null
Invoke-Py "436_ue_test_mirada_criatura.py" "PHASE='mirar'" "test436_mirar.json" "mirada_mirar" | Out-Null
Wait-Secs 4
Invoke-Py "436_ue_test_mirada_criatura.py" "PHASE='leer'" "test436_leer.json" "mirada_leer" | Out-Null
Invoke-Py "455_ue_auditoria_pie.py" "PHASE='pozo'" "test455_pozo.json" "pozo" | Out-Null
Invoke-Py "446_ue_test_subida_salon_pie.py" "GUIADO=True" "test446.json" "subida_salon" | Out-Null
Invoke-Py "449_ue_test_final_pie.py" "PHASE='entrar'" "test449_entrar.json" "final_entrar" | Out-Null
Wait-Secs 4
Invoke-Py "449_ue_test_final_pie.py" "PHASE='leer'" "test449_leer.json" "final_4s" | Out-Null
Wait-Secs 78
Invoke-Py "449_ue_test_final_pie.py" "PHASE='leer'" "test449_leer.json" "final_82s" | Out-Null
Wait-Secs 5
Invoke-Py "449_ue_test_final_pie.py" "PHASE='leer'" "test449_leer.json" "final_87s" | Out-Null

Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Wait-Secs 5
Invoke-Py "400_ue_test_locomocion_pie.py" "PHASE='convai_on'" "test400_convai_on.json" "convai_on" | Out-Null

$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null
$rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$all["log_errores"] = @($delta -split "`n" | Where-Object { $_ -match "Error|Accessed None|Blueprint Runtime|Ensure|Assertion" -and $_ -notmatch "LogPython|execute_script" } | Select-Object -First 40)
$all | ConvertTo-Json -Depth 8 | Set-Content "$D/auditoria_pie.json" -Encoding utf8
"OK auditoria -> $D/auditoria_pie.json"
