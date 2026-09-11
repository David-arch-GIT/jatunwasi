# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Alinea la rampa de colision (COL_HACV7_StairRamp) BAJO las escaleras visibles de la hacienda,
#   para que se pueda subir al 2do piso. Mantiene las escaleras de madera como estan (solo mueve la colision invisible).
#   Guarda. Reporta bounds antes/despues.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/alinear_rampa.json"
res = {"antes": None, "despues": None, "objetivo": None, "err": []}
eas = unreal.EditorActorSubsystem()
stair = None; ramp = None
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    if l == "HACV7_EXP_Staircase": stair = a
    if l == "COL_HACV7_StairRamp": ramp = a
if stair and ramp:
    try:
        sorg, sext = stair.get_actor_bounds(False)   # centro visual de la escalera
        rorg, rext = ramp.get_actor_bounds(False)
        rloc = ramp.get_actor_location()
        res["antes"] = {"ramp_loc": [round(rloc.x), round(rloc.y), round(rloc.z)], "ramp_bounds_c": [round(rorg.x), round(rorg.y), round(rorg.z)]}
        res["objetivo"] = {"stair_bounds_c": [round(sorg.x), round(sorg.y), round(sorg.z)]}
        # delta para alinear centro de bounds del ramp con el de la escalera (solo X,Y; Z lo dejamos)
        dx = sorg.x - rorg.x
        dy = sorg.y - rorg.y
        newloc = unreal.Vector(rloc.x + dx, rloc.y + dy, rloc.z)
        ramp.set_actor_location(newloc, False, False)
        rorg2, _ = ramp.get_actor_bounds(False)
        res["despues"] = {"ramp_loc": [round(newloc.x), round(newloc.y), round(newloc.z)], "ramp_bounds_c": [round(rorg2.x), round(rorg2.y), round(rorg2.z)]}
    except Exception as e:
        res["err"].append(str(e)[:80])
else:
    res["err"].append("no encontre escalera o rampa: stair=%s ramp=%s" % (bool(stair), bool(ramp)))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ALINEAR RAMPA %s" % res["despues"])
