# 436_ue_test_mirada_criatura.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: prueba PIE de la reaccion a la mirada de BP_CriaturaViva (usar antes 400 convai_off).
#   PHASE="mirar": pawn a 13 m del Karisiri (sobre NavMesh si es posible) girado hacia la criatura.
#   PHASE="leer": MiradaT, Activado y posicion de las 3 criaturas + distancia al pawn.
#   PHASE="noMirar": gira el pawn 180 grados (la mirada debe reiniciarse).
import unreal, json, math, traceback
try:
    PHASE
except NameError:
    PHASE = "leer"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test436_%s.json" % PHASE
res = {"phase": PHASE, "err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
    pc = unreal.GameplayStatics.get_player_controller(world, 0)
    crias = {a.get_actor_label(): a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_actor_label().startswith("Cria_")}
    k = crias["Cria_Karisiri"]; KL = k.get_actor_location()
    if PHASE == "mirar":
        nav = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(4000, 1700, 20), None, None, unreal.Vector(200, 200, 300))
        p = nav[0] if isinstance(nav, tuple) else nav
        if p is None: p = unreal.Vector(4000, 1700, 20)
        pawn.set_actor_location(p, False, True)
        cam = unreal.Vector(p.x, p.y, p.z + 150)   # v2: la camara aun no se actualizo tras mover el pawn
        d = unreal.Vector(KL.x - cam.x, KL.y - cam.y, KL.z + 60 - cam.z)
        yaw = math.degrees(math.atan2(d.y, d.x)); pitch = math.degrees(math.atan2(d.z, math.hypot(d.x, d.y)))
        pawn.set_actor_rotation(unreal.Rotator(0, 0, yaw), True)
        pc.set_control_rotation(unreal.Rotator(0, pitch, yaw))
        res["cam"] = [round(cam.x), round(cam.y), round(cam.z)]; res["yaw"] = round(yaw, 1)
    elif PHASE == "noMirar":
        r = pawn.get_actor_rotation(); pawn.set_actor_rotation(unreal.Rotator(0, 0, r.yaw + 180), True)
        pc.set_control_rotation(unreal.Rotator(0, 0, r.yaw + 180))
    cm = unreal.GameplayStatics.get_player_camera_manager(world, 0)
    CL = cm.get_camera_location(); CR = cm.get_camera_rotation()
    res["cam_rot"] = [round(CR.pitch, 1), round(CR.yaw, 1)]
    for lb, a in crias.items():
        L = a.get_actor_location()
        mesh = a.get_component_by_class(unreal.SkeletalMeshComponent); ML = mesh.get_world_location()
        res[lb] = {"MiradaT": round(a.get_editor_property("MiradaT"), 2), "Activado": a.get_editor_property("Activado"),
                   "loc": [round(L.x), round(L.y), round(L.z)], "malla": [round(ML.x), round(ML.y), round(ML.z)], "dist_malla": round(math.dist([ML.x, ML.y], [CL.x, CL.y])), "dist_cam": round(math.dist([L.x, L.y, L.z + 60], [CL.x, CL.y, CL.z]))}
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
