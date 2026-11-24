# 505_test_cartelas_frente_pie.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (copia de 471 + medicion 504) verificar que el panel abierto quede FRENTE al visitante. Orquestar 470 en PIE con Convai APAGADO: por cada una de las 24 cartelas -> apuntar, leer
#   (debe abrir: Abierto, panel visible, voz sonando), desviar, leer (debe cerrar). Tabla + errores de log.
$S = "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis"
$D = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
$API = "http://localhost:8090/api/editor"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
function Invoke-Py($pre, $outName) {
    $o = "$D/$outName"; if (Test-Path $o) { Remove-Item $o }
    $code = $pre + "`nexec(open(r'$S/470_ue_test_cartelas_pie.py', encoding='utf-8-sig').read())"
    Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script=$code} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 300 | Out-Null
    $k = 0; while (-not (Test-Path $o) -and $k -lt 240) { Start-Sleep -Milliseconds 250; $k++ }
    if (Test-Path $o) { Get-Content $o -Raw | ConvertFrom-Json } else { $null }
}
function Wait-Secs($s) { $t0 = Get-Date; while (((Get-Date) - $t0).TotalSeconds -lt $s) { Start-Sleep -Milliseconds 200 } }
$logStart = (Get-Item $LOG).Length
$o = "$D/test400_convai_off.json"; if (Test-Path $o) { Remove-Item $o }
Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script="PHASE='convai_off'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
$k = 0; while (-not (Test-Path $o) -and $k -lt 120) { Start-Sleep -Milliseconds 250; $k++ }
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep 1; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 60)
Wait-Secs 30   # despues de la intro de Adela (27 s, prioridad mayor)
$lista = (Invoke-Py "PHASE='lista'" "test470_lista.json").cartelas
$tabla = @()
for ($i = 0; $i -lt $lista.Count; $i++) {
    $ap = Invoke-Py "PHASE='apuntar'; IDX=$i" "test470_apuntar.json"
    Wait-Secs 1.0
    $ab = Invoke-Py "PHASE='leer'; IDX=$i" "test470_leer.json"
    $fr = Invoke-Py "IDX=$i`nexec(open(r'$S/504_ue_medir_cartela_frente.py', encoding='utf-8-sig').read())#" "test504.json"
    Invoke-Py "PHASE='desviar'" "test470_desviar.json" | Out-Null
    Wait-Secs 1.0
    $ce = Invoke-Py "PHASE='leer'; IDX=$i" "test470_leer.json"
    $tabla += [pscustomobject]@{ cartela=$lista[$i]; dist=$ap.dist; err=$ap.err; abre=$ab.abierto; panel=$ab.panel_visible; voz=$ab.sonando; audio=$ab.audio; cierra=(-not $ce.abierto); panel_oculto=(-not $ce.panel_visible); dist_h=$fr.dist_h; lat=$fr.angulo_lateral; dz=$fr.dz; normal=$fr.normal_hacia_camara; rotYaw=$fr.panel_rot[1]; camYaw=$fr.cam_yaw; ferr=$fr.err }
}
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Wait-Secs 5
$o = "$D/test400_convai_on.json"; if (Test-Path $o) { Remove-Item $o }
Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script="PHASE='convai_on'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
$k = 0; while (-not (Test-Path $o) -and $k -lt 120) { Start-Sleep -Milliseconds 250; $k++ }
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$errs = @($delta -split "`n" | Where-Object { $_ -match "Blueprint Runtime|Accessed None|\[Compiler\]" })
@{ tabla = $tabla; errores = $errs.Count; ej = ($errs | Select-Object -First 3); convai_on = (Get-Content $o -Raw) } | ConvertTo-Json -Depth 5 | Set-Content "$D/test505_cartelas_frente.json" -Encoding utf8
$tabla | Format-Table -AutoSize | Out-String -Width 200
"errores runtime: " + $errs.Count
"convai_on: " + (Get-Content $o -Raw)

