# 520_bp_leyendas_sin_vuelo.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: causa raiz del "vuelan" (prueba 517 tras 518/519): las Cria_* tienen gravedad 0 y modo de
#   movimiento de VUELO; el bucle DecidirAccion (BeginPlay -> Delay -> GetRandomReachablePoint -> AI MoveTo)
#   las movia con MaxFlySpeed 600 (MaxWalkSpeed no aplica en vuelo) por puntos del NavMesh: subian/bajaban
#   y giraban sin rumbo. Se DESCONECTA el arranque del bucle (Set CentroZona.then -> Delay): quedan en
#   reposo y solo avanzan caminando cuando el visitante las mira (515/516/518). Nada se borra.
#   Respaldo BP_CriaturaViva_pre_sin_vuelo.uasset. Errores: LOG.
$API = "http://localhost:8090/api/blueprints"; $BP = "/Game/JWN/Blueprints/BP_CriaturaViva"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
Copy-Item "C:/UnrealProjects/JatunWasiNawpakay/Content/JWN/Blueprints/BP_CriaturaViva.uasset" "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/BP_CriaturaViva_pre_sin_vuelo.uasset" -Force
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$set = $g.nodes | Where-Object { $_.id.StartsWith("AEB3A5") }
$lk = ($set.pins | Where-Object { $_.name -eq "then" }).links
if (@($lk).Count -ne 1 -or -not $lk[0].node_id.StartsWith("65A264")) { throw "cadena distinta (ya desconectada?)" }
Invoke-RestMethod -Uri "$API/modify" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"; operation="disconnect_pins"; node_id=$set.id; pin_name="then"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
$l0 = (Get-Item $LOG).Length
Invoke-RestMethod -Uri "$API/modify" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"; operation="compile"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
Start-Sleep 3
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($l0, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $dl = $rd.ReadToEnd(); $rd.Close()
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
"then de Set CentroZona: " + @((($g.nodes | Where-Object { $_.id.StartsWith("AEB3A5") }).pins | Where-Object { $_.name -eq "then" }).links).Count + " enlaces"
"errores compilador: " + @($dl -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error)|LogBlueprint: Error" }).Count
