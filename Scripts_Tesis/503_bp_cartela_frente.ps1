# 503_bp_cartela_frente.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: pedido de la usuaria tras la prueba en visor: "las cartelas se generan giradas o a un lado".
#   Causa: Abrir movia el ACTOR frente a la camara (yaw camara+180), pero el componente Panel tiene offset y
#   giro relativos distintos en cada cartela (ej. (-68,0,-45) yaw 90) -> quedaba corrido y de canto/espaldas.
#   Arreglo: tras SetActorLocationAndRotation, el Panel se coloca en coordenadas de MUNDO:
#     posicion = camara + adelante_horizontal * 120 cm   (solo yaw: no se inclina si se mira al piso)
#     rotacion = (pitch 0, yaw camara+90, roll 90)        (convencion de los paneles: yaw Y mira a rot(Y)*(+Y))
#   Respaldo del .uasset. Compila y revisa errores en el LOG.
$API = "http://localhost:8090/api/blueprints"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"
$LOG = "$ROOT/Saved/Logs/JatunWasiNawpakay.log"
$CART = "/Game/Cartelas/BP_Cartela"
Copy-Item "$ROOT/Content/Cartelas/BP_Cartela.uasset" "$ROOT/Saved/ClaudeBackups/BP_Cartela_pre_frente.uasset" -Force
function Invoke-Bp($h) {
    $h["blueprint_path"] = $CART; if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = "EventGraph" }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
function Get-LogErrors($desde) { $fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($desde, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $d = $rd.ReadToEnd(); $rd.Close(); @($d -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error)|LogBlueprint: Error" }) }
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$CART; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$N = @{}; $g.nodes | % { $N[$_.id.Substring(0,6)] = $_ }
$setAct = $N["2BD644"]; $play = $N["068B6D"]; $brk = $N["C5BD54"]; $fwd = $N["5CF260"]; $suma = $N["9C9F88"]; $panel = $N["85C60D"]
if (-not ($setAct -and $play -and $brk -and $fwd -and $suma -and $panel)) { throw "grafo distinto al esperado" }
$thenL = ($setAct.pins | ? { $_.name -eq "then" }).links
if (@($thenL).Count -ne 1 -or $thenL[0].node_id -ne $play.id) { throw "cadena Abrir ya modificada?" }
$x = $setAct.pos_x; $y = $setAct.pos_y
$KML = "/Script/Engine.KismetMathLibrary"
$mrH  = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="MakeRotator"; pos_x=$x-600; pos_y=$y+350}).node_id
$addY = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="Add_DoubleDouble"; pos_x=$x-300; pos_y=$y+500}).node_id
$mrP  = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="MakeRotator"; pos_x=$x-100; pos_y=$y+500}).node_id
$setP = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.SceneComponent"; function_name="K2_SetWorldLocationAndRotation"; pos_x=$x+250; pos_y=$y+250}).node_id
Invoke-Bp @{operation="set_pin_value"; node_id=$addY; pin_name="B"; value="90.0"} | Out-Null
Invoke-Bp @{operation="set_pin_value"; node_id=$mrP; pin_name="Roll"; value="90.0"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$fwd.id; pin_name="InRot"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$setAct.id; pin_name="then"} | Out-Null
$C = @(
  @($brk.id,"Yaw",$mrH,"Yaw"), @($mrH,"ReturnValue",$fwd.id,"InRot"),
  @($brk.id,"Yaw",$addY,"A"), @($addY,"ReturnValue",$mrP,"Yaw"),
  @($panel.id,"Panel",$setP,"self"), @($suma.id,"ReturnValue",$setP,"NewLocation"), @($mrP,"ReturnValue",$setP,"NewRotation"),
  @($setAct.id,"then",$setP,"execute"), @($setP,"then",$play.id,"execute")
)
foreach ($c in $C) { Invoke-Bp @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null }
$l1 = (Get-Item $LOG).Length; Invoke-Bp @{operation="compile"} | Out-Null; Start-Sleep 3
$errs = Get-LogErrors $l1
[ordered]@{ nodos = @{mrH=$mrH; addY=$addY; mrP=$mrP; setP=$setP}; errores = $errs.Count; detalle = ($errs | Select-Object -First 4) } | ConvertTo-Json -Depth 4
