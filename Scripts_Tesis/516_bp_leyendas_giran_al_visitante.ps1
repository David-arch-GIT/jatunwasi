# 516_bp_leyendas_giran_al_visitante.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: complemento de 515. Al acercarse, la malla de la leyenda conservaba su giro: se deslizaba de
#   costado o de espaldas ("como si volara"). Ahora el MoveComponentTo de acercamiento (77AD3B) gira la
#   malla SUAVEMENTE (mismos 5.5 s) para quedar de frente al visitante:
#     yaw_rel = -90 (giro base de la malla, igual en las 3) + NormalizeAxis(yaw_mirar - yaw_actor)
#   (NormalizeAxis: nunca gira mas de 180 grados). Verificado antes (huesos L/R con get_socket_location): el frente de la
#   criatura = adelante del actor. Respaldo BP_CriaturaViva_pre_giro.uasset. Errores: LOG.
$API = "http://localhost:8090/api/blueprints"; $BP = "/Game/JWN/Blueprints/BP_CriaturaViva"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"; $LOG = "$ROOT/Saved/Logs/JatunWasiNawpakay.log"
Copy-Item "$ROOT/Content/JWN/Blueprints/BP_CriaturaViva.uasset" "$ROOT/Saved/ClaudeBackups/BP_CriaturaViva_pre_giro.uasset" -Force
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
$mov = $NN["77AD3B"]; $aloc = $NN["A82E2B"]; $cam = $NN["07FB19"]; $arot = $NN["1EDE19"]
if (-not ($mov -and $aloc -and $cam -and $arot)) { throw "grafo distinto al esperado" }
$rotLinks = ($mov.pins | Where-Object { $_.name -eq "TargetRelativeRotation" }).links
if (@($rotLinks).Count -ne 1 -or -not $rotLinks[0].node_id.StartsWith("F90822")) { throw "TargetRelativeRotation ya modificado?" }
$x = $mov.pos_x - 900; $y = $mov.pos_y + 300; $KML = "/Script/Engine.KismetMathLibrary"
$la  = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="FindLookAtRotation"; pos_x=$x; pos_y=$y}).node_id
$bla = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="BreakRotator"; pos_x=$x+250; pos_y=$y}).node_id
$bar = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="BreakRotator"; pos_x=$x+250; pos_y=$y+200}).node_id
$sub = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="Subtract_DoubleDouble"; pos_x=$x+450; pos_y=$y+100}).node_id
$nrm = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="NormalizeAxis"; pos_x=$x+600; pos_y=$y+100}).node_id
$add = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="Add_DoubleDouble"; pos_x=$x+750; pos_y=$y+100}).node_id
$mk  = (Invoke-Bp @{operation="add_call_function"; function_class=$KML; function_name="MakeRotator"; pos_x=$x+900; pos_y=$y+100}).node_id
Invoke-Bp @{operation="set_pin_value"; node_id=$add; pin_name="A"; value="-90.0"} | Out-Null
Invoke-Bp @{operation="disconnect_pins"; node_id=$mov.id; pin_name="TargetRelativeRotation"} | Out-Null
$C = @(
  @($aloc.id,"ReturnValue",$la,"Start"), @($cam.id,"ReturnValue",$la,"Target"), @($la,"ReturnValue",$bla,"InRot"),
  @($arot.id,"ReturnValue",$bar,"InRot"), @($bla,"Yaw",$sub,"A"), @($bar,"Yaw",$sub,"B"), @($sub,"ReturnValue",$nrm,"Angle"),
  @($nrm,"ReturnValue",$add,"B"), @($add,"ReturnValue",$mk,"Yaw"), @($mk,"ReturnValue",$mov.id,"TargetRelativeRotation")
)
foreach ($c in $C) { Invoke-Bp @{operation="connect_pins"; source_node_id=$c[0]; source_pin=$c[1]; target_node_id=$c[2]; target_pin=$c[3]} | Out-Null }
$l0 = (Get-Item $LOG).Length
Invoke-Bp @{operation="compile"} | Out-Null; Start-Sleep 3
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($l0, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $dl = $rd.ReadToEnd(); $rd.Close()
$errs = @($dl -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error)|LogBlueprint: Error" })
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
$chk = foreach ($id in @($la,$bla,$bar,$sub,$nrm,$add,$mk)) { $n = $g.nodes | Where-Object { $_.id -eq $id }; "{0}: {1}" -f ($n.title -replace "`n"," "), ((($n.pins | Where-Object { $_.links }) | ForEach-Object { $_.name + "->" + (($_.links | ForEach-Object { $_.node_id.Substring(0,6) + "." + $_.pin_name }) -join "|") }) -join "; ") }
[ordered]@{ errores = $errs.Count; detalle = ($errs | Select-Object -First 3); conexiones = $chk; addA = ((($g.nodes | Where-Object { $_.id -eq $add }).pins | Where-Object { $_.name -eq "A" }).default_value) } | ConvertTo-Json -Depth 4

