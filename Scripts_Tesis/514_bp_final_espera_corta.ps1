# 514_bp_final_espera_corta.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: la usuaria entro al salon y "se quedo asi". Tras la despedida de Adela (21 s) el grafo de
#   BP_GestorRecorrido esperaba 75 s en silencio antes del fundido y los creditos. Delay A5FB48 -> 30 s
#   (cuenta desde que empieza la despedida: ~9 s de vals y faroles tras la ultima frase, luego fundido).
#   Respaldo: Saved/ClaudeBackups/BP_GestorRecorrido_pre_final_corto.uasset. Verifica errores en el LOG.
$API = "http://localhost:8090/api/blueprints"; $BP = "/Game/JWN/Blueprints/BP_GestorRecorrido"
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$d = $g.nodes | Where-Object { $_.id.StartsWith("A5FB48") }
Invoke-RestMethod -Uri "$API/modify" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"; operation="set_pin_value"; node_id=$d.id; pin_name="Duration"; value="30.0"} | ConvertTo-Json) -ContentType "application/json"
Invoke-RestMethod -Uri "$API/modify" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"; operation="compile"} | ConvertTo-Json) -ContentType "application/json"
