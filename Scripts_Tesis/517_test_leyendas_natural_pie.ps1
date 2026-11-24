# 517_test_leyendas_natural_pie.ps1
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: prueba PIE (Convai APAGADO via 400) del acercamiento natural de las leyendas (515/516):
#   436 "mirar" pone al pawn a ~13-17 m mirando al Karisiri; se muestrea cada ~1 s la malla: distancia
#   recorrida, velocidad (cm/s), altura, y error de orientacion (frente de la criatura vs direccion al
#   visitante). Luego "noMirar" y se mide el regreso lento. Tabla + errores de log.
$S = "C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis"; $DIR = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
$API = "http://localhost:8090/api/editor"; $LOG = "C:/UnrealProjects/JatunWasiNawpakay/Saved/Logs/JatunWasiNawpakay.log"
function Run-Py($code, $out) { $o = "$DIR/$out"; if (Test-Path $o) { Remove-Item $o }; Invoke-RestMethod -Uri "$API/execute_script" -Method Post -Body (@{script=$code} | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 300 | Out-Null; $k=0; while (-not (Test-Path $o) -and $k -lt 240) { Start-Sleep -Milliseconds 100; $k++ }; if (Test-Path $o) { Get-Content $o -Raw | ConvertFrom-Json } }
$probe = @'
import unreal, json, math
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
k = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_actor_label() == "Cria_Karisiri"][0]
m = k.get_component_by_class(unreal.SkeletalMeshComponent); L = m.get_world_location(); R = m.get_world_rotation()
C = unreal.GameplayStatics.get_player_camera_manager(world, 0).get_camera_location()
frente = R.yaw + 90.0; hacia = math.degrees(math.atan2(C.y - L.y, C.x - L.x))
err = (hacia - frente + 180) % 360 - 180
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/probe517.json", "w").write(json.dumps({"t": unreal.GameplayStatics.get_time_seconds(world), "x": L.x, "y": L.y, "z": L.z, "err": round(err, 1), "dist": round(math.dist([L.x, L.y], [C.x, C.y])), "act": k.get_editor_property("Activado")}))
'@
Set-Content "$DIR/probe517.py" $probe -Encoding utf8
$logStart = (Get-Item $LOG).Length
Run-Py "PHASE='convai_off'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())" "test400_convai_off.json" | Out-Null
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"start"}' -ContentType "application/json" -TimeoutSec 60 | Out-Null
$k = 0; do { Start-Sleep 1; $k++; $st = Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"status"}' -ContentType "application/json" } while (-not $st.pie_active -and $k -lt 60)
Start-Sleep 5
Run-Py "PHASE='mirar'`nexec(open(r'$S/436_ue_test_mirada_criatura.py', encoding='utf-8-sig').read())" "test436_mirar.json" | Out-Null
Start-Sleep 1
Run-Py "PHASE='mirar'`nexec(open(r'$S/436_ue_test_mirada_criatura.py', encoding='utf-8-sig').read())" "test436_mirar.json" | Out-Null   # 2da vez: camara ya en su sitio
$filas = @(); $t0 = Get-Date
for ($i = 0; $i -lt 12; $i++) { $p = Run-Py "exec(open(r'$DIR/probe517.py', encoding='utf-8-sig').read())" "probe517.json"; $filas += $p; Start-Sleep -Milliseconds 900 }
Run-Py "PHASE='noMirar'`nexec(open(r'$S/436_ue_test_mirada_criatura.py', encoding='utf-8-sig').read())" "test436_noMirar.json" | Out-Null
for ($i = 0; $i -lt 26; $i++) { $p = Run-Py "exec(open(r'$DIR/probe517.py', encoding='utf-8-sig').read())" "probe517.json"; $filas += $p; Start-Sleep -Milliseconds 900 }
Invoke-RestMethod -Uri "$API/pie_control" -Method Post -Body '{"operation":"stop"}' -ContentType "application/json" -TimeoutSec 30 | Out-Null
Start-Sleep 5
$on = Run-Py "PHASE='convai_on'`nexec(open(r'$S/400_ue_test_locomocion_pie.py', encoding='utf-8-sig').read())" "test400_convai_on.json"
$prev = $null; $tab = foreach ($f in $filas) { $v = if ($prev) { [math]::Round([math]::Sqrt([math]::Pow($f.x-$prev.x,2)+[math]::Pow($f.y-$prev.y,2)) / [math]::Max(0.05, $f.t-$prev.t)) } else { 0 }; $prev = $f; [pscustomobject]@{ t=[math]::Round($f.t,1); act=$f.act; dist_m=[math]::Round($f.dist/100,2); vel_cm_s=$v; z=[math]::Round($f.z); err_orient=$f.err } }
$fs = [IO.File]::Open($LOG, 'Open', 'Read', 'ReadWrite'); $fs.Seek($logStart, 'Begin') | Out-Null; $rd = New-Object IO.StreamReader($fs); $delta = $rd.ReadToEnd(); $rd.Close()
$errs = @($delta -split "`n" | Where-Object { $_ -match "Blueprint Runtime|Accessed None|\[Compiler\]" })
$tab | Format-Table -AutoSize | Out-String -Width 160
"errores runtime: " + $errs.Count; $errs | Select-Object -First 3
"convai_on: " + (($on.flags | ForEach-Object { $_ -join ':' }) -join ', ')
