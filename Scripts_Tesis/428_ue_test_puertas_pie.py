# 428_ue_test_puertas_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE de las 4 puertas reales (usar antes 400 convai_off). Por cada puerta:
#   PHASE="cerca_<n>": lleva al pawn 1.6 m DELANTE de la puerta (con barrido -> dispara la zona).
#   PHASE="leer": giro actual de cada hoja de las 4 puertas + variable Abrir.
#   PHASE="lejos": lleva al pawn a la plaza (todas deben cerrarse).
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "leer"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test428_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    doors = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_actor_label().startswith("PUERTA_")}
    if PHASE.startswith("cerca_"):
        d = doors[PHASE[6:]]
        L = d.get_actor_location(); yaw = math.radians(d.get_actor_rotation().yaw)
        fx, fy = -math.sin(yaw), math.cos(yaw)          # local +Y = lado del visitante
        far = unreal.Vector(L.x + fx * 700, L.y + fy * 700, L.z + 20)
        near = unreal.Vector(L.x + fx * 160, L.y + fy * 160, L.z + 20)
        pawn.set_actor_location(far, False, True); pawn.set_actor_location(near, True, True)
        res["pawn"] = [round(pawn.get_actor_location().x), round(pawn.get_actor_location().y)]
    elif PHASE == "lejos":
        pawn.set_actor_location(unreal.Vector(600, -950, 30), False, True)
    for lb, d in doors.items():
        st = {"abrir": d.get_editor_property("Abrir")}
        for c in d.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_name().startswith("Hoja") and c.static_mesh:
                st[c.get_name()] = round(c.get_editor_property("relative_rotation").yaw, 1)
        res[lb] = st
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
