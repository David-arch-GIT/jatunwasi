# 528_test_final_reinicio_pie.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE (Convai APAGADO via 400) del REINICIO tras el final (pedido de la usuaria):
#   449 "entrar" pone al visitante en el salon -> se espera a que los creditos sean visibles (~37 s) ->
#   1) boton A antes de 4 s de creditos NO reinicia; 2) a los 6 s se inyecta el boton A (misma via que OpenXR,
#   UJWEntradaVR.PruebaInyectar) -> el mapa se recarga: tiempo de juego vuelve a ~0 y el pawn al inicio.
$S = "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis"; $DIR = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
$API = "http://localhost:8090/api/editor"; $LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
function Run-Py($code, $out) { $o = "$DIR/$out"; if (Test-Path $o) { Remove-Item $o }; Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script=$code} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 300 | Out-Null; $k=0; while (-not (Test-Path $o) -and $k -lt 240) { Start-Sleep -Milliseconds 250; $k++ }; if (Test-Path $o) { Get-Content $o -Raw | ConvertFrom-Json } }
$estado = @'
import unreal, json
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
p = unreal.GameplayStatics.get_player_pawn(w, 0)
cred = [c for c in p.get_components_by_class(unreal.SceneComponent) if c.get_name().startswith("CreditosFinal")]
L = p.get_actor_location()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test528.json", "w").write(json.dumps({"t": round(unreal.GameplayStatics.get_time_seconds(w), 1), "pawn": [round(L.x), round(L.y), round(L.z)], "creditos": cred[0].is_visible() if cred else None, "mundo": w.get_path_name()}))
'@
Set-Content "$DIR/est528.py" $estado -Encoding utf8
$inyA = "import unreal`nw = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()`np = unreal.GameplayStatics.get_player_pawn(w, 0)`nok = unreal.JWEntradaVR.prueba_inyectar(p, 'BotonA', unreal.Vector(1, 0, 0))`nopen(r'$DIR/iny528.txt','w').write(str(ok))"
$logStart = (Get-Item $LOG).Length
Run-Py "PHASE='convai_off'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())" "test400_convai_off.json" | Out-Null
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep 1; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 60)
Start-Sleep 6
$res = [ordered]@{}
$res.inicio = Run-Py "exec(open(r'$DIR/est528.py', encoding='utf-8-sig').read())" "test528.json"
$res.entrar = Run-Py "PHASE='entrar'`nexec(open(r'$S/449_ue_test_final_pie.py', encoding='utf-8-sig').read())" "test449_entrar.json"
$k = 0; do { Start-Sleep 1; $k++; $e = Run-Py "exec(open(r'$DIR/est528.py', encoding='utf-8-sig').read())" "test528.json" } while (-not $e.creditos -and $k -lt 70)
$res.creditos_visibles = $e
Run-Py $inyA "iny528.txt" | Out-Null
Start-Sleep 2
$res.A_antes_de_4s = Run-Py "exec(open(r'$DIR/est528.py', encoding='utf-8-sig').read())" "test528.json"
Start-Sleep 5
Run-Py $inyA "iny528.txt" | Out-Null
Start-Sleep 8
$k = 0; do { $d = Run-Py "exec(open(r'$DIR/est528.py', encoding='utf-8-sig').read())" "test528.json"; Start-Sleep 1; $k++ } while (($null -eq $d) -and $k -lt 20)
$res.tras_A = $d
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Start-Sleep 5
$on = Run-Py "PHASE='convai_on'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())" "test400_convai_on.json"
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$res.reinicio_log = @($delta -split "`n" | Where-Object { $_ -match "JWGuia: reinicio" }).Count
$res.errores = @($delta -split "`n" | Where-Object { $_ -match "Blueprint Runtime|Accessed None|\[Compiler\]" }).Count
$res.convai_on = (($on.flags | ForEach-Object { $_ -join ':' }) -join ', ')
$res | ConvertTo-Json -Depth 4
