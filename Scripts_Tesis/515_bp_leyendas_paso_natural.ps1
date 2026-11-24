# 515_bp_leyendas_paso_natural.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: pedido de la usuaria tras el visor: "las leyendas se mueven rapido, como si volaran; que sea
#   natural (las 3)". En BP_CriaturaViva, al ser miradas 2.2 s, la MALLA se deslizaba el 60 % de la
#   distancia al visitante (hasta ~15 m) en 2.2 s (~7 m/s) y a los 12 s volvia de espaldas en 2.5 s.
#   Ahora: 25 % de la distancia en 5.5 s (~1 m/s, ritmo de su caminata en sitio), espera 14 s y regreso
#   lento de 10 s (discreto). Solo valores de pines; respaldo BP_CriaturaViva_pre_natural.uasset.
$API = "http://localhost:8090/api/blueprints"; $BP = "/Game/JWN/Blueprints/BP_CriaturaViva"
$LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
function Id($pre) { ($g.nodes | Where-Object { $_.id.StartsWith($pre) }).id }
$cambios = @( @("4D7B7C","B","0.25"), @("69D17F","B","0.25"), @("77AD3B","OverTime","5.5"), @("589E88","Duration","14.0"), @("DBBF84","OverTime","10.0") )
foreach ($c in $cambios) {
    Invoke-RestMethod -Uri "$API/modify" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"; operation="set_pin_value"; node_id=(Id $c[0]); pin_name=$c[1]; value=$c[2]} | ConvertTo-Json) -ContentType "application/json" | Out-Null
}
$l0 = (Get-Item $LOG).Length
Invoke-RestMethod -Uri "$API/modify" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"; operation="compile"} | ConvertTo-Json) -ContentType "application/json" | Out-Null
Start-Sleep 3
$g = Invoke-RestMethod -Uri "$API/get_graph" -Method Post -Body (@{blueprint_path=$BP; graph_name="EventGraph"} | ConvertTo-Json) -ContentType "application/json"
foreach ($c in $cambios) { "{0}.{1} = {2} (esperado {3})" -f $c[0], $c[1], ((($g.nodes | Where-Object { $_.id.StartsWith($c[0]) }).pins | Where-Object { $_.name -eq $c[1] }).default_value), $c[2] }
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($l0, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $dl = $rd.ReadToEnd(); $rd.Close()
"errores compilador: " + @($dl -split "`n" | Where-Object { $_ -match "\[Compiler\].*(Error|error)|LogBlueprint: Error" }).Count
