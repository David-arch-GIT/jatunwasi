# 418_ue_test_puerta_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba de BP_PuertaProximidad SIN gastar Convai (usar antes 400 convai_off).
#   PHASE="place"  (editor): coloca un ejemplar TEMPORAL "TEST_Puerta" en la entrada del Templo.
#   PHASE="cerca"  (PIE): lleva al pawn a 1.5 m de la puerta (barrido=True para disparar overlap).
#   PHASE="leer"   (PIE): lee el giro relativo de HojaIzq/HojaDer y la variable Abrir.
#   PHASE="lejos"  (PIE): lleva al pawn a 8 m.
#   PHASE="clean"  (editor): borra TEST_Puerta (no queda nada en el nivel).
import unreal, json, traceback
try:
    PHASE
except NameError:
    PHASE = "leer"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test418_%s.json" % PHASE
DOOR = unreal.Vector(25, 10350, 0)
res = {"phase": PHASE, "err": None}
try:
    if PHASE in ("place", "clean"):
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if a.get_actor_label() == "TEST_Puerta":
                unreal.EditorLevelLibrary.destroy_actor(a)
        if PHASE == "place":
            cls = unreal.EditorAssetLibrary.load_blueprint_class("/Game/JWN/Blueprints/BP_PuertaProximidad")
            a = unreal.EditorLevelLibrary.spawn_actor_from_class(cls, DOOR)
            a.set_actor_label("TEST_Puerta")
            res["placed"] = True
    else:
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
        door = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_actor_label() == "TEST_Puerta"][0]
        if PHASE == "cerca":
            pawn.set_actor_location(unreal.Vector(DOOR.x, DOOR.y - 600, 20), False, True)
            pawn.set_actor_location(unreal.Vector(DOOR.x, DOOR.y - 150, 20), True, True)
        elif PHASE == "lejos":
            pawn.set_actor_location(unreal.Vector(DOOR.x, DOOR.y - 800, 20), True, True)
        res["pawn"] = str(pawn.get_actor_location())
        res["abrir"] = door.get_editor_property("Abrir")
        for nm in ("HojaIzq", "HojaDer"):
            c = [x for x in door.get_components_by_class(unreal.StaticMeshComponent) if x.get_name().startswith(nm)][0]
            r = c.get_editor_property("relative_rotation"); l = c.get_editor_property("relative_location")
            res[nm] = {"yaw": round(r.yaw, 1), "loc": [round(l.x), round(l.y), round(l.z)]}
        z = [x for x in door.get_components_by_class(unreal.SphereComponent)][0]
        res["overlapping_pawn"] = z.is_overlapping_actor(pawn)
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
