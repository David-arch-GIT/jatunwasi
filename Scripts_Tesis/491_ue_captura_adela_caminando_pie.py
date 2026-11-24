# 491_ue_captura_adela_caminando_pie.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (PIE) captura VISUAL de Adela caminando desde la camara del visitante: coloca al pawn a DIST cm
#   de Adela (DIST>0 detras de ella, DIST<0 delante) sobre el NavMesh, orienta el control hacia ella y
#   ejecuta HighResShot (Saved/Screenshots). NOM = etiqueta.
import unreal, json, math, traceback
try:
    NOM
except NameError:
    NOM = "x"
try:
    DIST
except NameError:
    DIST = 350
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap491_%s.json" % NOM
res = {"err": None}
try:
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(w, 0)
    pc = unreal.GameplayStatics.get_player_controller(w, 0)
    a = [x for x in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Actor) if x.get_actor_label() == "Adela_Convai"][0]
    L = a.get_actor_location(); f = math.radians(a.get_actor_rotation().yaw + 90.0)
    r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(L.x - DIST * math.cos(f), L.y - DIST * math.sin(f), L.z + 50), None, None, unreal.Vector(150, 150, 600))
    q = r[0] if isinstance(r, tuple) else r
    if q: pawn.set_actor_location(unreal.Vector(q.x, q.y, q.z + 90), False, True)
    cam = unreal.GameplayStatics.get_player_camera_manager(w, 0).get_camera_location()
    rot = unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(L.x, L.y, L.z + 100))
    pc.set_control_rotation(rot)
    pawn.set_actor_rotation(unreal.Rotator(0, rot.yaw, 0), False)
    unreal.SystemLibrary.execute_console_command(w, "HighResShot 1")
    res["ok"] = True; res["adela_yaw"] = a.get_actor_rotation().yaw
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
