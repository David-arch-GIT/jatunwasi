# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Mueve el PlayerStart FUERA de la plaza (que cuelga al arrancar por ser la zona mas pesada)
#   a un punto frente a la hacienda (zona que funciona). Traza al suelo para Z correcto (no dentro de pared).
#   Captura el viewport desde ese punto para verificar que este despejado. Guarda el nivel.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mover_spawn.json"
res = {"ok": False, "nuevo": None, "err": []}
eas = unreal.EditorActorSubsystem()
# candidato: frente a la hacienda (marker -7000,-2500), 800 hacia la plaza (este) = despejado
CX, CY = -6200.0, -2500.0
# trazar al suelo
start = unreal.Vector(CX, CY, 3000.0)
end = unreal.Vector(CX, CY, -3000.0)
hit = unreal.SystemLibrary.line_trace_single(
    eas, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [],
    unreal.DrawDebugTrace.NONE, True, unreal.LinearColor.RED, unreal.LinearColor.GREEN, 0.0)
groundZ = 95.0
if hit:
    try:
        groundZ = hit.to_tuple()[5].z  # impact_point.z
    except Exception as e:
        res["err"].append("trace: %s" % e)
newloc = unreal.Vector(CX, CY, groundZ + 110.0)
# mover PlayerStart
ps = None
for a in eas.get_all_level_actors():
    if a.get_class().get_name() == "PlayerStart" or "PlayerStart" in a.get_actor_label():
        ps = a
        break
if ps:
    ps.set_actor_location(newloc, False, False)
    # orientar mirando hacia la hacienda (oeste, yaw 180)
    ps.set_actor_rotation(unreal.Rotator(pitch=0.0, yaw=180.0, roll=0.0), False)
    res["ok"] = True
    res["nuevo"] = {"x": round(newloc.x), "y": round(newloc.y), "z": round(newloc.z), "groundZ": round(groundZ)}
else:
    res["err"].append("no encontre PlayerStart")
# posicionar camara del editor en el spawn para capturar
try:
    les = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    les.set_level_viewport_camera_info(unreal.Vector(CX, CY, groundZ + 160.0), unreal.Rotator(pitch=-5.0, yaw=180.0, roll=0.0))
except Exception as e:
    res["err"].append("cam: %s" % e)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MOVER SPAWN ok=%s %s" % (res["ok"], res["nuevo"]))
