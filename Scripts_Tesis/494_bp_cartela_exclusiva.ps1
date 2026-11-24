# 494_bp_cartela_exclusiva.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: SOLO UNA CARTELA ABIERTA A LA VEZ. Cartelas vecinas (zampona/tarka en la misma vitrina, a 67 cm)
#   se abrian juntas (cono de apuntado de 18 grados). Se agrega en BP_XRPawn la variable CartelaAbierta
#   (Actor) y en BP_Cartela (Tick):
#     Branch(abrir) -> Branch(NOT IsValid(pawn.CartelaAbierta)) -> Set pawn.CartelaAbierta = self -> Abrir
#     Branch(cerrar) -> Set pawn.CartelaAbierta = None -> Cerrar
#   Respaldos .uasset. Compila y verifica errores en el LOG (no en la respuesta de la API).
$API = "http://localhost:8090/api/blueprints"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"
$LOG = "$ROOT/Saved/Logs/JatunWasiNawpakay.log"
$PAWN = "/Game/XRFramework/Blueprints/BP_XRPawn"; $CART = "/Game/Cartelas/BP_Cartela"
Copy-Item "$ROOT/Content/XRFramework/Blueprints/BP_XRPawn.uasset" "$ROOT/Saved/ClaudeBackups/BP_XRPawn_pre_cartela_exclusiva.uasset" -Force
Copy-Item "$ROOT/Content/Cartelas/BP_Cartela.uasset" "$ROOT/Saved/ClaudeBackups/BP_Cartela_pre_exclusiva.uasset" -Force
function Invoke-Bp($bp, $h) {
    $h["blueprint_path"] = $bp; if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = "EventGraph" }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
function Get-LogErrors($desde) { $fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($desde, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $d = $rd.ReadToEnd(); $rd.Close(); @($d -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error)|LogBlueprint: Error" }) }
$res = [ordered]@{}
# 1) variable en el pawn
$insp = Invoke-RestMethod -Uri "$API/inspect" -Method Post -Body (@{blueprint_path=$PAWN} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 120 | ConvertTo-Json -Depth 6
if ($insp -notmatch "CartelaAbierta") { Invoke-Bp $PAWN @{operation="add_variable"; variable_name="CartelaAbierta"; variable_type="object:/Script/Engine.Actor"} | Out-Null }
$l0 = (Get-Item $LOG).Length; Invoke-Bp $PAWN @{operation="compile"} | Out-Null; Start-Sleep 3
$res.pawn_errores = (Get-LogErrors $l0).Count
if ($res.pawn_errores -gt 0) { $res | ConvertTo-Json; throw "BP_XRPawn con errores" }
# 2) grafo de la cartela
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$CART; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$byPre = @{}; $g.nodes | % { $byPre[$_.id.Substring(0,6)] = $_ }
$cast = $byPre["5CF744"]; $brAbrir = $byPre["197623"]; $brCerrar = $byPre["3D6DFF"]; $abrir = $byPre["43D995"]; $cerrar = $byPre["1121AE"]
if (-not ($cast -and $brAbrir -and $brCerrar -and $abrir -and $cerrar)) { throw "grafo de BP_Cartela distinto al esperado" }
$castPin = ($cast.pins | Where-Object { $_.direction -eq "output" -and $_.type -eq "object" }).name
$thenA = ($brAbrir.pins | Where-Object { $_.name -eq "then" }).links; $thenC = ($brCerrar.pins | Where-Object { $_.name -eq "then" }).links
if (@($thenA).Count -ne 1 -or $thenA[0].node_id -ne $abrir.id -or @($thenC).Count -ne 1 -or $thenC[0].node_id -ne $cerrar.id) { throw "cadena abrir/cerrar inesperada (ya modificada?)" }
$x = $brAbrir.pos_x; $y = $brAbrir.pos_y
$CLS = "BP_XRPawn_C"
$get  = (Invoke-Bp $CART @{operation="add_member_get"; member_class=$CLS; member_name="CartelaAbierta"; pos_x=$x+150; pos_y=$y-250}).node_id
$isv  = (Invoke-Bp $CART @{operation="add_call_function"; function_class="/Script/Engine.KismetSystemLibrary"; function_name="IsValid"; pos_x=$x+350; pos_y=$y-250}).node_id
$not  = (Invoke-Bp $CART @{operation="add_call_function"; function_class="/Script/Engine.KismetMathLibrary"; function_name="Not_PreBool"; pos_x=$x+550; pos_y=$y-250}).node_id
$br   = (Invoke-Bp $CART @{operation="add_node"; node_class="K2Node_IfThenElse"; pos_x=$x+300; pos_y=$y-100}).node_id
$setA = (Invoke-Bp $CART @{operation="add_member_set"; member_class=$CLS; member_name="CartelaAbierta"; pos_x=$x+550; pos_y=$y-100}).node_id
$self = (Invoke-Bp $CART @{operation="add_node"; node_class="K2Node_Self"; pos_x=$x+400; pos_y=$y+20}).node_id
$setC = (Invoke-Bp $CART @{operation="add_member_set"; member_class=$CLS; member_name="CartelaAbierta"; pos_x=$brCerrar.pos_x+250; pos_y=$brCerrar.pos_y+150}).node_id
$res.ids = @{get=$get; isv=$isv; not=$not; br=$br; setA=$setA; self=$self; setC=$setC; castPin=$castPin}
Invoke-Bp $CART @{operation="disconnect_pins"; node_id=$brAbrir.id; pin_name="then"} | Out-Null
Invoke-Bp $CART @{operation="disconnect_pins"; node_id=$brCerrar.id; pin_name="then"} | Out-Null
$C = @(
  @($cast.id,$castPin,$get,"self"), @($get,"CartelaAbierta",$isv,"Object"), @($isv,"ReturnValue",$not,"A"), @($not,"ReturnValue",$br,"Condition"),
  @($brAbrir.id,"then",$br,"execute"), @($br,"then",$setA,"execute"), @($cast.id,$castPin,$setA,"self"), @($self,"self",$setA,"CartelaAbierta"), @($setA,"then",$abrir.id,"execute"),
  @($brCerrar.id,"then",$setC,"execute"), @($cast.id,$castPin,$setC,"self"), @($setC,"then",$cerrar.id,"execute")
)
foreach ($c in $C) { Invoke-Bp $CART @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null }
$l1 = (Get-Item $LOG).Length; Invoke-Bp $CART @{operation="compile"} | Out-Null; Start-Sleep 3
$errs = Get-LogErrors $l1
$res.cartela_errores = $errs.Count; if ($errs.Count) { $res.detalle = $errs | Select-Object -First 4 }
# verificacion de conexiones
$g2 = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$CART; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$res.verif = $g2.nodes | Where-Object { $_.id -in @($get,$isv,$not,$br,$setA,$self,$setC,$brAbrir.id,$brCerrar.id) } | % { $n=$_; ($n.id.Substring(0,6) + " " + ($n.title -replace "`n.*","") + " | " + (($n.pins | Where-Object { $_.links.Count -gt 0 -and $_.direction -eq 'output' } | % { $_.name + '->' + (($_.links | % { $_.node_id.Substring(0,6) + '.' + $_.pin_name }) -join ',') }) -join ' ; ')) }
$res | ConvertTo-Json -Depth 5
