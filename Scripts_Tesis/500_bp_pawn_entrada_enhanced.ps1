# 500_bp_pawn_entrada_enhanced.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: ARREGLO del "no deja moverse" en el visor. En BP_XRPawn se reemplazan las 4 lecturas de teclas
#   sueltas (que en el visor valen 0 con Enhanced Input + OpenXR) por la libreria C++ UJWEntradaVR, que lee
#   acciones de Enhanced Input (IA_JW_*):
#     GetInputAnalogKeyState(Right_Thumbstick_X) -> UJWEntradaVR::MoverX
#     GetInputAnalogKeyState(Right_Thumbstick_Y) -> UJWEntradaVR::MoverY
#     WasInputKeyJustPressed(Right_A_Click)       -> UJWEntradaVR::BotonAPulsado
#     WasInputKeyJustPressed(Right_Trigger_Click) -> UJWEntradaVR::GatilloPulsado
#   Cada salida se reconecta a EXACTAMENTE los mismos destinos; luego se borra el nodo viejo. Respaldo del
#   .uasset. Compila y verifica errores en el LOG.
$API = "http://localhost:8090/api/blueprints"
$BP = "/Game/XRFramework/Blueprints/BP_XRPawn"
$ROOT = "C:/UnrealProjects/JatunWasiNawpakay"
$LOG = "$ROOT/Saved/Logs/JatunWasiNawpakay.log"
Copy-Item "$ROOT/Content/XRFramework/Blueprints/BP_XRPawn.uasset" "$ROOT/Saved/ClaudeBackups/BP_XRPawn_pre_entrada_enhanced.uasset" -Force
function Invoke-Bp($h) {
    $h["blueprint_path"] = $BP; if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = "EventGraph" }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
function Get-G { Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 180 }
$res = [ordered]@{}
$plan = @(
  @{ key = "OculusTouch_Right_Thumbstick_X"; title = "Analog Key"; fn = "MoverX" },
  @{ key = "OculusTouch_Right_Thumbstick_Y"; title = "Analog Key"; fn = "MoverY" },
  @{ key = "OculusTouch_Right_A_Click"; title = "Just Pressed"; fn = "BotonAPulsado" },
  @{ key = "OculusTouch_Right_Trigger_Click"; title = "Just Pressed"; fn = "GatilloPulsado" }
)
$g = Get-G
foreach ($p in $plan) {
    $old = $g.nodes | Where-Object { $_.title -match $p.title -and (($_.pins | Where-Object { $_.name -eq "Key" }).default_value -eq $p.key) } | Select-Object -First 1
    if (-not $old) { $res[$p.fn] = "nodo viejo no encontrado (ya reemplazado?)"; continue }
    $destinos = @((($old.pins | Where-Object { $_.name -eq "ReturnValue" }).links))
    $nuevo = (Invoke-Bp @{operation="add_call_function"; function_class="/Script/JWGuia.JWEntradaVR"; function_name=$p.fn; pos_x=$old.pos_x; pos_y=($old.pos_y - 120)}).node_id
    foreach ($d in $destinos) { Invoke-Bp @{operation="connect_pins"; source_node_id=$nuevo; source_pin="ReturnValue"; target_node_id=$d.node_id; target_pin=$d.pin_name} | Out-Null }
    Invoke-Bp @{operation="delete_node"; node_id=$old.id} | Out-Null
    $res[$p.fn] = @{ viejo = $old.id.Substring(0,6); nuevo = $nuevo.Substring(0,6); destinos = @($destinos | % { $_.node_id.Substring(0,6) + "." + $_.pin_name }) }
}
$l0 = (Get-Item $LOG).Length
Invoke-Bp @{operation="compile"} | Out-Null; Start-Sleep 3
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($l0, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $dl = $rd.ReadToEnd(); $rd.Close()
$res.errores_compilacion = @($dl -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error)|LogBlueprint: Error" }).Count
# verificacion: los nodos nuevos y sus destinos
$g2 = Get-G
$res.verif = @($g2.nodes | Where-Object { $_.title -match "Mover X|Mover Y|Boton A|Gatillo" } | % { ($_.id.Substring(0,6) + " " + ($_.title -replace "`n.*","") + " -> " + ((($_.pins | Where-Object { $_.name -eq "ReturnValue" }).links | % { $_.node_id.Substring(0,6) + "." + $_.pin_name }) -join ",")) })
$res.quedan_teclas_sueltas = @($g2.nodes | Where-Object { $_.title -match "Input Key|Analog Key" }).Count
$res | ConvertTo-Json -Depth 5
