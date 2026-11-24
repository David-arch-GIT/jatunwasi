# 461_bp_pawn_mezcla_escucha.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: en BP_XRPawn, mientras el usuario mantiene el grip derecho (microfono Convai abierto) silenciar
#   las voces grabadas (SMX_Escucha: SCL_Voz 0, ambiente 0.4) para que Convai no "escuche" la narracion.
#   Presionar: Set bMute=false -> Branch(MixEscuchaActiva) [no: Push -> Set true] -> Haptic (cadena previa).
#   Soltar:    Set bMute=true  -> Branch(MixEscuchaActiva) [si: Pop -> Set false] -> Get (cadena previa).
#   Re-ejecutable (borra nodos sueltos de un intento previo). Respaldo del .uasset antes de tocar.
$API = "http://localhost:8090/api/blueprints"
$BP = "/Game/XRFramework/Blueprints/BP_XRPawn"
$GR = "EventGraph"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"
$MIX = "/Game/JWN/Audio/SMX_Escucha.SMX_Escucha"
Copy-Item "$ROOT/Content/XRFramework/Blueprints/BP_XRPawn.uasset" "$ROOT/Saved/ClaudeBackups/BP_XRPawn_pre_escucha.uasset" -Force
function Invoke-Bp($h) {
    $h["blueprint_path"] = $BP
    if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = $GR }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
function Get-Graph { Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name=$GR} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 180 }
$out = [ordered]@{}
$g = Get-Graph
foreach ($n in $g.nodes) {
    $linked = @($n.pins | Where-Object { $_.links.Count -gt 0 }).Count
    if ($linked -eq 0 -and ($n.title -match "MixEscuchaActiva|Sound Mix Modifier" -or ($n.class -eq "K2Node_IfThenElse"))) { Invoke-Bp @{operation="delete_node"; node_id=$n.id} | Out-Null; $out["borrado_" + $n.id.Substring(0,6)] = $n.title }
}
$g = Get-Graph
$setOn  = ($g.nodes | Where-Object { $_.title -match "bMute" -and ($_.pins | Where-Object { $_.name -eq "bMute" }).default_value -eq "false" }).id
$setOff = ($g.nodes | Where-Object { $_.title -match "bMute" -and ($_.pins | Where-Object { $_.name -eq "bMute" }).default_value -eq "true" }).id
$nOn  = (($g.nodes | Where-Object { $_.id -eq $setOn }).pins | Where-Object { $_.name -eq "then" }).links
$nOff = (($g.nodes | Where-Object { $_.id -eq $setOff }).pins | Where-Object { $_.name -eq "then" }).links
if (@($nOn).Count -ne 1 -or @($nOff).Count -ne 1) { throw "cadena inesperada: on=$(@($nOn).Count) off=$(@($nOff).Count) (ya cableado?)" }
$hapt = $nOn[0].node_id; $sigOff = $nOff[0].node_id
$out.prev = @{setOn=$setOn; hapt=$hapt; setOff=$setOff; sigOff=$sigOff}
$vars = (Invoke-RestMethod -Uri "$API/inspect" -Method Post -Body (@{blueprint_path=$BP} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 120 | ConvertTo-Json -Depth 6)
if ($vars -notmatch "MixEscuchaActiva") { Invoke-Bp @{operation="add_variable"; variable_name="MixEscuchaActiva"; variable_type="bool"} | Out-Null }
Invoke-Bp @{operation="compile"} | Out-Null
$CLS = "BP_XRPawn_C"
$pOn = $g.nodes | Where-Object { $_.id -eq $setOn }; $x = $pOn.pos_x; $y = $pOn.pos_y
$brP = (Invoke-Bp @{operation="add_node"; node_class="K2Node_IfThenElse"; pos_x=$x+250; pos_y=$y+250}).node_id
$getMixP  = (Invoke-Bp @{operation="add_member_get"; member_class=$CLS; member_name="MixEscuchaActiva"; pos_x=$x+50; pos_y=$y+380}).node_id
$push= (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.GameplayStatics"; function_name="PushSoundMixModifier"; pos_x=$x+500; pos_y=$y+300}).node_id
$sP  = (Invoke-Bp @{operation="add_member_set"; member_class=$CLS; member_name="MixEscuchaActiva"; pos_x=$x+780; pos_y=$y+300}).node_id
$pOff = $g.nodes | Where-Object { $_.id -eq $setOff }; $x2 = $pOff.pos_x; $y2 = $pOff.pos_y
$brR = (Invoke-Bp @{operation="add_node"; node_class="K2Node_IfThenElse"; pos_x=$x2+250; pos_y=$y2+250}).node_id
$getMixR  = (Invoke-Bp @{operation="add_member_get"; member_class=$CLS; member_name="MixEscuchaActiva"; pos_x=$x2+50; pos_y=$y2+380}).node_id
$pop = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.GameplayStatics"; function_name="PopSoundMixModifier"; pos_x=$x2+500; pos_y=$y2+300}).node_id
$sR  = (Invoke-Bp @{operation="add_member_set"; member_class=$CLS; member_name="MixEscuchaActiva"; pos_x=$x2+780; pos_y=$y2+300}).node_id
$out.ids = @{brP=$brP; getP=$getMixP; push=$push; sP=$sP; brR=$brR; getR=$getMixR; pop=$pop; sR=$sR}
Invoke-Bp @{operation="disconnect_pins"; node_id=$setOn; pin_name="then"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$setOff; pin_name="then"} | Out-Null
$C = @(
  @($setOn,"then",$brP,"execute"), @($getMixP,"MixEscuchaActiva",$brP,"Condition"), @($brP,"then",$hapt,"execute"), @($brP,"else",$push,"execute"),
  @($push,"then",$sP,"execute"), @($sP,"then",$hapt,"execute"),
  @($setOff,"then",$brR,"execute"), @($getMixR,"MixEscuchaActiva",$brR,"Condition"), @($brR,"else",$sigOff,"execute"), @($brR,"then",$pop,"execute"),
  @($pop,"then",$sR,"execute"), @($sR,"then",$sigOff,"execute")
)
foreach ($c in $C) { Invoke-Bp @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null }
Invoke-Bp @{operation="set_pin_value"; node_id=$sP; pin_name="MixEscuchaActiva"; value="true"} | Out-Null
Invoke-Bp @{operation="set_pin_value"; node_id=$sR; pin_name="MixEscuchaActiva"; value="false"} | Out-Null
Invoke-Bp @{operation="set_pin_object"; node_id=$push; pin_name="InSoundMixModifier"; object_path=$MIX} | Out-Null
Invoke-Bp @{operation="set_pin_object"; node_id=$pop; pin_name="InSoundMixModifier"; object_path=$MIX} | Out-Null
$out.compile = Invoke-Bp @{operation="compile"}
$out | ConvertTo-Json -Depth 6 | Set-Content "$ROOT/Saved/ClaudeBackups/bp_pawn_escucha.json" -Encoding utf8
"OK"
