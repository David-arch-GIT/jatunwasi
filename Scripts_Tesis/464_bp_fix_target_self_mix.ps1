# 464_bp_fix_target_self_mix.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: CORREGIR error de compilacion introducido por 460/461: los nodos Get/Set MixVozActiva y
#   MixEscuchaActiva se crearon como miembro externo sin Target ("uses an invalid target"). Se conecta un
#   nodo Self al pin self de cada uno. Luego compila y VERIFICA en el LOG (no en la respuesta de la API)
#   que no haya errores [Compiler] nuevos para el BP.
$API = "http://localhost:8090/api/blueprints"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
$res = [ordered]@{}
function Invoke-Bp($bp, $h) {
    $h["blueprint_path"] = $bp; if (-not $h.ContainsKey("graph_name")) { $h["graph_name"] = "EventGraph" }
    for ($t = 0; $t -lt 3; $t++) {
        try { $r = Invoke-RestMethod -Uri "$API/modify" -Method Post -Body ($h | ConvertTo-Json -Depth 5) -ContentType "application/json" -TimeoutSec 180; if ($r.success -or $r.node_id) { return $r } } catch { $r = $_.Exception.Message }
        Start-Sleep 2
    }
    throw "fallo: $($h.operation) -> $($r | ConvertTo-Json -Compress)"
}
foreach ($pair in @(@("/Game/JWN/Blueprints/BP_GuiaInteractiva", "MixVozActiva"), @("/Game/XRFramework/Blueprints/BP_XRPawn", "MixEscuchaActiva"))) {
    $bp = $pair[0]; $var = $pair[1]
    $g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$bp; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 180
    $nodes = $g.nodes | Where-Object { $_.title -match "^(Get|Set) $var" }
    $n = 0
    foreach ($nd in $nodes) {
        $selfPin = $nd.pins | Where-Object { $_.name -eq "self" -and $_.direction -eq "input" }
        if (-not $selfPin) { $res["$var sin pin self " + $nd.id.Substring(0,6)] = ($nd.pins | % name) -join ","; continue }
        if ($selfPin.links.Count -gt 0) { continue }
        $sid = (Invoke-Bp $bp @{operation="add_node"; node_class="K2Node_Self"; pos_x=($nd.pos_x - 160); pos_y=($nd.pos_y + 90)}).node_id
        Invoke-Bp $bp @{operation="connect_pins"; source_node_id=$sid; source_pin="self"; target_node_id=$nd.id; target_pin="self"} | Out-Null
        $n++
    }
    $res["$bp self_conectados"] = $n
    $before = (Get-Item $LOG).Length
    Invoke-Bp $bp @{operation="compile"} | Out-Null
    Start-Sleep 3
    $fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($before, 'Begin') | Out-Null
    $rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
    $errs = @($delta -split "`n" | Where-Object { $_ -match "\[Compiler\]" -and $_ -match "Error" })
    $res["$bp errores_compilacion"] = $errs.Count
    if ($errs.Count) { $res["$bp detalle"] = $errs | Select-Object -First 4 }
}
$res | ConvertTo-Json -Depth 5
