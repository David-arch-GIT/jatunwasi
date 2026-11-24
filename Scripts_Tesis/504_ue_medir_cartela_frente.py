# 504_ue_medir_cartela_frente.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (PIE) mide si el panel de la cartela IDX abierta quedo FRENTE al visitante:
#   distancia horizontal camara->panel, angulo lateral respecto a la mirada, diferencia de altura,
#   y hacia donde mira la cara del panel (debe apuntar a la camara: dot ~ +1).
#   Convencion de los paneles (Plane roll 90): la cara mira a rot(yaw) * (0,1,0).
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test504.json"
res = {"err": None}
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
    carts = sorted([a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor) if a.get_class().get_name() == "BP_Cartela_C"], key=lambda a: a.get_actor_label())
    a = carts[IDX]
    cm = unreal.GameplayStatics.get_player_camera_manager(world, 0)
    C = cm.get_camera_location(); cy = cm.get_camera_rotation().yaw
    panel = [c for c in a.get_components_by_class(unreal.StaticMeshComponent) if c.get_name().startswith("Panel")][0]
    P = panel.get_world_location(); R = panel.get_world_rotation()
    f = unreal.MathLibrary.get_forward_vector(R); r = unreal.MathLibrary.get_right_vector(R); u = unreal.MathLibrary.get_up_vector(R)
    # normal del plano = eje Z local del componente
    n = u
    to_cam = unreal.Vector(C.x - P.x, C.y - P.y, C.z - P.z); L = math.sqrt(to_cam.x ** 2 + to_cam.y ** 2 + to_cam.z ** 2)
    dot = (n.x * to_cam.x + n.y * to_cam.y + n.z * to_cam.z) / L
    ang = math.degrees(math.atan2(P.y - C.y, P.x - C.x)) - cy
    ang = (ang + 180) % 360 - 180
    res.update({"cartela": a.get_actor_label(), "abierto": a.get_editor_property("Abierto"), "visible": panel.is_visible(),
                "dist_h": round(math.hypot(P.x - C.x, P.y - C.y)), "angulo_lateral": round(ang, 1), "dz": round(P.z - C.z),
                "normal_hacia_camara": round(dot, 3), "panel_rot": [round(R.pitch, 1), round(R.yaw, 1), round(R.roll, 1)], "cam_yaw": round(cy, 1)})
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
