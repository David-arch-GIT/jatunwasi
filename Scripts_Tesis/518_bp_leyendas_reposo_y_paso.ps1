# 518_bp_leyendas_reposo_y_paso.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: leyendas naturales (pedido de la usuaria). La prueba 517 mostro que ademas del acercamiento
#   las criaturas DEAMBULABAN (DecidirAccion pone MaxWalkSpeed 40-110 y AI MoveTo a puntos del NavMesh:
#   giran sin rumbo, suben/bajan 50 cm, caminata en sitio desacoplada = "vuelan"). En el grafo:
#   (1) al activarse por la mirada: Mesh.PlayAnimation(WalkAnim, bucle) ANTES del MoveComponentTo;
#   (2) al terminar el acercamiento: Mesh.PlayAnimation(IdleAnim, bucle) -> se queda quieta mirandote;
#   (3) se QUITA el regreso de espaldas (DBBF84 queda sin ejecutar): tras 14 s solo se rearma la mirada
#       (Activado=false, MiradaT=0). Cada mirada la acerca un 25 % mas (y al acercarse se deshace: M_CriaturaDisuelve).
#   El deambular se apaga por instancia en 519 (VelMin=VelMax=0, use_controller_rotation_yaw=False, IdleAnim al inicio).
#   Respaldo BP_CriaturaViva_pre_reposo.uasset. Errores: LOG.
$API = "http://localhost:8090/api/blueprints"; $BP = "/Game/JWN/Blueprints/BP_CriaturaViva"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"; $LOG = "$ROOT/Saved/Logs/JatunWasiNawpakay.log"
Copy-Item "$ROOT/Content/JWN/Blueprints/BP_CriaturaViva.uasset" "$ROOT/Saved/ClaudeBackups/BP_CriaturaViva_pre_reposo.uasset" -Force
function Invoke-Bp($h) {
    $h["blueprint_path"] = $BP; if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = "EventGraph" }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$NN = @{}; $g.nodes | ForEach-Object { $NN[$_.id.Substring(0,6)] = $_ }
$stop = $NN["68CCAC"]; $setBase = $NN["AFAA22"]; $mov = $NN["77AD3B"]; $delay = $NN["589E88"]; $ret = $NN["DBBF84"]; $setAct = $NN["E01770"]; $mesh = $NN["473A95"]; $self = $NN["17AA1D"]
if (-not ($stop -and $setBase -and $mov -and $delay -and $ret -and $setAct -and $mesh -and $self)) { throw "grafo distinto al esperado" }
$l1 = ($stop.pins | Where-Object { $_.name -eq "then" }).links; $l2 = ($mov.pins | Where-Object { $_.name -eq "then" }).links; $l3 = ($delay.pins | Where-Object { $_.name -eq "then" }).links
if ($l1[0].node_id -ne $setBase.id -or $l2[0].node_id -ne $delay.id -or $l3[0].node_id -ne $ret.id) { throw "cadena ya modificada?" }
$CLS = "BP_CriaturaViva_C"; $x = $setBase.pos_x; $y = $setBase.pos_y
$pW = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.SkeletalMeshComponent"; function_name="PlayAnimation"; pos_x=$x-200; pos_y=$y+250}).node_id
$gW = (Invoke-Bp @{operation="add_member_get"; member_class=$CLS; member_name="WalkAnim"; pos_x=$x-450; pos_y=$y+350}).node_id
$pI = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.SkeletalMeshComponent"; function_name="PlayAnimation"; pos_x=$mov.pos_x+250; pos_y=$mov.pos_y+250}).node_id
$gI = (Invoke-Bp @{operation="add_member_get"; member_class=$CLS; member_name="IdleAnim"; pos_x=$mov.pos_x; pos_y=$mov.pos_y+350}).node_id
Invoke-Bp @{operation="set_pin_value"; node_id=$pW; pin_name="bLooping"; value="true"} | Out-Null
Invoke-Bp @{operation="set_pin_value"; node_id=$pI; pin_name="bLooping"; value="true"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$stop.id; pin_name="then"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$mov.id; pin_name="then"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$delay.id; pin_name="then"} | Out-Null
$C = @(
  @($self.id,"self",$gW,"self"), @($self.id,"self",$gI,"self"),
  @($mesh.id,"Mesh",$pW,"self"), @($gW,"WalkAnim",$pW,"NewAnimToPlay"),
  @($mesh.id,"Mesh",$pI,"self"), @($gI,"IdleAnim",$pI,"NewAnimToPlay"),
  @($stop.id,"then",$pW,"execute"), @($pW,"then",$setBase.id,"execute"),
  @($mov.id,"then",$pI,"execute"), @($pI,"then",$delay.id,"execute"),
  @($delay.id,"then",$setAct.id,"execute")
)
foreach ($c in $C) { Invoke-Bp @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null }
$l0 = (Get-Item $LOG).Length
Invoke-Bp @{operation="compile"} | Out-Null; Start-Sleep 3
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($l0, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $dl = $rd.ReadToEnd(); $rd.Close()
$errs = @($dl -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error|Warning)|LogBlueprint: Error" })
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$chk = foreach ($id in @($pW,$gW,$pI,$gI,$delay.id)) { $n = $g.nodes | Where-Object { $_.id -eq $id }; "{0}: {1}" -f ($n.title -replace "`n"," "), ((($n.pins | Where-Object { $_.links -or $_.name -eq "bLooping" }) | ForEach-Object { $_.name + "=" + $_.default_value + "->" + (($_.links | ForEach-Object { $_.node_id.Substring(0,6) + "." + $_.pin_name }) -join "|") }) -join "; ") }
[ordered]@{ errores = $errs.Count; detalle = ($errs | Select-Object -First 3); conexiones = $chk } | ConvertTo-Json -Depth 4
