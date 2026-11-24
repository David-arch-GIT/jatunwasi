# 463_test_voces_pie.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: orquestar 462 en PIE con Convai APAGADO: voces al inicio (1, 4, 10, 20, 40 s) y prueba del
#   mix de conversacion (push a los 5 s, pop a los 8 s): la voz debe seguir "sonando" (PlayWhenSilent).
$S = "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis"
$D = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
$API = "http://localhost:8090/api/editor"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
$all = [ordered]@{}
function Invoke-Py($file, $pre, $outName, $key) {
    $o = "$D/$outName"; if (Test-Path $o) { Remove-Item $o }
    $code = $pre + "`nexec(open(r'$S/$file', encoding='utf-8-sig').read())"
    Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script=$code} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 300 | Out-Null
    $k = 0; while (-not (Test-Path $o) -and $k -lt 240) { Start-Sleep -Milliseconds 250; $k++ }
    $all[$key] = if (Test-Path $o) { Get-Content $o -Raw | ConvertFrom-Json } else { "sin salida" }
}
function Wait-Until($t0, $s) { while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 200 } }
$logStart = (Get-Item $LOG).Length
Invoke-Py "400_ue_test_locomocion_pie.py" "PHASE='convai_off'" "test400_convai_off.json" "convai_off"
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep -Milliseconds 300; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 200)
$t0 = Get-Date
Wait-Until $t0 1;  Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t01"
Wait-Until $t0 4;  Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t04"
Wait-Until $t0 5;  Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='push'" "test462_push.json" "push_t05"
Wait-Until $t0 7;  Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t07_con_mix"
Wait-Until $t0 8;  Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='pop'" "test462_pop.json" "pop_t08"
Wait-Until $t0 10; Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t10"
Wait-Until $t0 20; Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t20"
Wait-Until $t0 30; Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t30_fin_intro"
Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='tp'; TP=(76,-1304)" "test462_tp.json" "tp_fuente"
Wait-Until $t0 33; Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t33_en_fuente"
Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='tp'; TP=(-4310,-143)" "test462_tp.json" "tp_duende"
Wait-Until $t0 36; Invoke-Py "462_ue_test_voces_mezcla_pie.py" "PHASE='voces'" "test462_voces.json" "t36_en_duende"
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Start-Sleep 5
Invoke-Py "400_ue_test_locomocion_pie.py" "PHASE='convai_on'" "test400_convai_on.json" "convai_on"
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null
$rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$all["log_errores"] = @($delta -split "`n" | Where-Object { $_ -match "Error|Accessed None|Blueprint Runtime|Ensure|Assertion" -and $_ -notmatch "LogPython|execute_script" } | Select-Object -First 30)
$all | ConvertTo-Json -Depth 8 -Compress | Set-Content "$D/test_voces.json" -Encoding utf8
"OK"
