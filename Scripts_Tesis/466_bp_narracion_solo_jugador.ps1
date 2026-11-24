# 466_bp_narracion_solo_jugador.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: BUG real: BP_NarrationPoint se disparaba con CUALQUIER actor (perfil OverlapAllDynamic): las
#   criaturas (Duende/Karisiri/Condenado) "gastaban" su leyenda antes de que llegue el visitante.
#   Arreglo: OnBeginOverlap -> Branch(OtherActor == GetPlayerPawn(0)) -> Play -> SetCollision(NoCollision).
#   Respaldo .uasset; compila y verifica errores en el LOG.
$API = "http://localhost:8090/api/blueprints"
$BP = "/Game/JWN/Blueprints/BP_NarrationPoint"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"
$LOG = "$ROOT/Saved/Logs/JatunWasiNawpakay.log"
Copy-Item "$ROOT/Content/JWN/Blueprints/BP_NarrationPoint.uasset" "$ROOT/Saved/ClaudeBackups/BP_NarrationPoint_pre_filtro.uasset" -Force
function Invoke-Bp($h) {
    $h["blueprint_path"] = $BP; if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = "EventGraph" }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
$res = [ordered]@{}
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$ev = $g.nodes | Where-Object { $_.title -match "Begin Overlap" }
$play = $g.nodes | Where-Object { $_.title -match "^Play" }
$thenLinks = ($ev.pins | Where-Object { $_.name -eq "then" }).links
if (@($thenLinks).Count -ne 1 -or $thenLinks[0].node_id -ne $play.id) { throw "grafo inesperado (ya filtrado?)" }
$x = $ev.pos_x; $y = $ev.pos_y
$pp  = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.GameplayStatics"; function_name="GetPlayerPawn"; pos_x=$x+200; pos_y=$y+260}).node_id
$eq  = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/Engine.KismetMathLibrary"; function_name="EqualEqual_ObjectObject"; pos_x=$x+460; pos_y=$y+200}).node_id
$br  = (Invoke-Bp @{operation="add_node"; node_class="K2Node_IfThenElse"; pos_x=$x+700; pos_y=$y}).node_id
$res.ids = @{pp=$pp; eq=$eq; br=$br}
Invoke-Bp @{operation="disconnect_pins"; node_id=$ev.id; pin_name="then"} | Out-Null
foreach ($c in @(@($ev.id,"then",$br,"execute"), @($ev.id,"OtherActor",$eq,"A"), @($pp,"ReturnValue",$eq,"B"), @($eq,"ReturnValue",$br,"Condition"), @($br,"then",$play.id,"execute"))) {
    Invoke-Bp @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null
}
$before = (Get-Item $LOG).Length
Invoke-Bp @{operation="compile"} | Out-Null
Start-Sleep 3
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($before, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$res.errores = @($delta -split "`n" | Where-Object { $_ -match "\[Compiler\]" })
$g2 = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$res.grafo = $g2.nodes | % { $n=$_; ($n.id.Substring(0,6) + " " + ($n.title -replace "`n.*","") + " | " + (($n.pins | Where-Object { $_.links.Count -gt 0 -and $_.direction -eq 'output' } | % { $_.name + '->' + (($_.links | % { $_.node_id.Substring(0,6) + '.' + $_.pin_name }) -join ',') }) -join ' ; ')) }
$res | ConvertTo-Json -Depth 5
