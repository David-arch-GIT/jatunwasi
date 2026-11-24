# 460_bp_adela_mezcla_conversacion.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: cablear en BP_GuiaInteractiva (Adela Convai) el silenciado de voces grabadas mientras Adela
#   habla: OnStartedTalking -> (PlayAnimation existente) -> Branch(!MixVozActiva) -> PushSoundMixModifier
#   (SMX_Conversacion) -> MixVozActiva=true ; OnFinishedTalking -> (PlayAnimation) -> Branch(MixVozActiva)
#   -> PopSoundMixModifier -> MixVozActiva=false. La guarda evita que el mix quede pegado si Convai
#   dispara "started" dos veces. Respaldo del .uasset antes de tocar.
$API = "http://localhost:8090/api/blueprints"
$BP = "/Game/JWN/Blueprints/BP_GuiaInteractiva"
$GR = "EventGraph"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"
Copy-Item "$ROOT/Content/JWN/Blueprints/BP_GuiaInteractiva.uasset" "$ROOT/Saved/ClaudeBackups/BP_GuiaInteractiva_pre_mezcla.uasset" -Force
function Invoke-Bp($h) {
    $h["blueprint_path"] = $BP
    if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = $GR }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 120; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
$out = [ordered]@{}
# re-ejecutable: borra Branch / nodos MixVozActiva / Push-Pop sueltos (sin enlaces) de un intento previo
$g0 = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name=$GR} | ConvertTo-Json) -ContentType "application/json"
foreach ($n in $g0.nodes) {
    $linked = @($n.pins | Where-Object { $_.links.Count -gt 0 }).Count
    if ($linked -eq 0 -and ($n.class -eq "K2Node_IfThenElse" -or $n.title -match "MixVozActiva|Sound Mix Modifier")) { Invoke-Bp @{operation="delete_node"; node_id=$n.id} | Out-Null; $out["borrado_" + $n.id.Substring(0,6)] = $n.title }
}
$vars = (Invoke-RestMethod -Uri "$API/inspect" -Method Post -Body (@{blueprint_path=$BP} | ConvertTo-Json) -ContentType "application/json" | ConvertTo-Json -Depth 6)
if ($vars -notmatch "MixVozActiva") { Invoke-Bp @{operation="add_variable"; variable_name="MixVozActiva"; variable_type="bool"} | Out-Null }
Invoke-Bp @{operation="compile"} | Out-Null
$CLS = "BP_GuiaInteractiva_C"
$brA = (Invoke-Bp @{operation="add_node"; node_class="K2Node_IfThenElse"; pos_x=1100; pos_y=1400}).node_id
$gA  = (Invoke-Bp @{operation="add_member_get"; member_class=$CLS; member_name="MixVozActiva"; pos_x=900; pos_y=1520}).node_id
$push = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.GameplayStatics"; function_name="PushSoundMixModifier"; pos_x=1350; pos_y=1400}).node_id
$sA  = (Invoke-Bp @{operation="add_member_set"; member_class=$CLS; member_name="MixVozActiva"; pos_x=1650; pos_y=1400}).node_id
$brB = (Invoke-Bp @{operation="add_node"; node_class="K2Node_IfThenElse"; pos_x=1100; pos_y=1800}).node_id
$gB  = (Invoke-Bp @{operation="add_member_get"; member_class=$CLS; member_name="MixVozActiva"; pos_x=900; pos_y=1920}).node_id
$pop = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.GameplayStatics"; function_name="PopSoundMixModifier"; pos_x=1350; pos_y=1800}).node_id
$sB  = (Invoke-Bp @{operation="add_member_set"; member_class=$CLS; member_name="MixVozActiva"; pos_x=1650; pos_y=1800}).node_id
$out.ids = @{brA=$brA; gA=$gA; push=$push; sA=$sA; brB=$brB; gB=$gB; pop=$pop; sB=$sB}
# Inicio del habla (anim 5E76CC) y fin (anim 931BD3)
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name=$GR} | ConvertTo-Json) -ContentType "application/json"
$animIni = ($g.nodes | Where-Object { $_.id -like "5E76CC*" }).id
$animFin = ($g.nodes | Where-Object { $_.id -like "931BD3*" }).id
$C = @(
  @($animIni,"then",$brA,"execute"), @($gA,"MixVozActiva",$brA,"Condition"), @($brA,"else",$push,"execute"), @($push,"then",$sA,"execute"),
  @($animFin,"then",$brB,"execute"), @($gB,"MixVozActiva",$brB,"Condition"), @($brB,"then",$pop,"execute"), @($pop,"then",$sB,"execute")
)
foreach ($c in $C) { Invoke-Bp @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null }
Invoke-Bp @{operation="set_pin_value"; node_id=$sA; pin_name="MixVozActiva"; value="true"} | Out-Null
Invoke-Bp @{operation="set_pin_value"; node_id=$sB; pin_name="MixVozActiva"; value="false"} | Out-Null
Invoke-Bp @{operation="set_pin_object"; node_id=$push; pin_name="InSoundMixModifier"; object_path="/Game/JWN/Audio/SMX_Conversacion.SMX_Conversacion"} | Out-Null
Invoke-Bp @{operation="set_pin_object"; node_id=$pop; pin_name="InSoundMixModifier"; object_path="/Game/JWN/Audio/SMX_Conversacion.SMX_Conversacion"} | Out-Null
$cmp = Invoke-Bp @{operation="compile"}
$out.compile = $cmp
$out | ConvertTo-Json -Depth 6 | Set-Content "$ROOT/Saved/ClaudeBackups/bp_adela_mezcla.json" -Encoding utf8
"OK"
