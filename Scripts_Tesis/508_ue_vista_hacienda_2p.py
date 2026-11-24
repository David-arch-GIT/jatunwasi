# 508_ue_vista_hacienda_2p.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (solo lectura) capturas del 2do piso de la Hacienda para ubicar las "puertas por las que no se
#   entra" (pedido de la usuaria). SceneCapture2D temporal: (a) cenital ortografica sin techos,
#   (b) vistas a la altura de los ojos desde puntos VISTAS=[(x,y,z,yaw),...]. Borra los temporales.
import unreal, json, traceback, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vista2p.json"
DIRP = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vista2p"
os.makedirs(DIRP, exist_ok=True)
try:
    VISTAS
except NameError:
    VISTAS = []
try:
    CENITAL
except NameError:
    CENITAL = True
res = {"err": None, "files": []}
cap = None
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
    ocultar = [a for a in acts if a.get_actor_label() in ("HACV7_EXP_Roofs", "HACV7_EXP_RoofTrim", "HACV7_EXP_CornicesTrim", "Cube16", "Cube17", "Cube18", "Cube13", "Cube14", "Cube15")]
    cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(-7300, -1600, 3000), unreal.Rotator(0, -90, 0))
    cap.set_actor_label("TMP_Vista2P")
    cc = cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_BASE_COLOR)  # albedo sin luz (el mapa es de noche)
    if CENITAL:
        rt = unreal.RenderingLibrary.create_render_target2d(world, 1600, 1100, unreal.TextureRenderTargetFormat.RTF_RGBA8)
        cc.set_editor_property("texture_target", rt)
        cc.set_editor_property("fov_angle", 60.0)
        cap.set_actor_location(unreal.Vector(-7300, -1600, 2700), False, False)
        for a in ocultar: cc.hide_actor_components(a, True)
        r = unreal.Rotator(); r.pitch = -90; r.yaw = 0; cap.set_actor_rotation(r, False)
        cc.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, rt, DIRP, "cenital.png"); res["files"].append("cenital.png")
    rt2 = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cc.set_editor_property("texture_target", rt2)
    cc.set_editor_property("projection_type", unreal.CameraProjectionMode.PERSPECTIVE)
    cc.set_editor_property("fov_angle", 90.0)
    cc.clear_hidden_components()
    for i, (x, y, z, yaw) in enumerate(VISTAS):
        cap.set_actor_location(unreal.Vector(x, y, z), False, False)
        r = unreal.Rotator(); r.pitch = 0; r.yaw = yaw; cap.set_actor_rotation(r, False)
        cc.capture_scene()
        fn = "v%d_%d_%d_y%d.png" % (i, x, y, yaw)
        unreal.RenderingLibrary.export_render_target(world, rt2, DIRP, fn); res["files"].append(fn)
except Exception:
    res["err"] = traceback.format_exc()[:1200]
finally:
    if cap: unreal.EditorLevelLibrary.destroy_actor(cap)
open(OUT, "w").write(json.dumps(res))

