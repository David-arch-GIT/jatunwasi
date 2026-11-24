# 450_ue_verificar_creditos_render.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: verificar VISUALMENTE (sin depender del viewport del editor, ocupado por el usuario) que el
#   plano de creditos del pawn se ve de frente y legible. Crea una SceneCapture2D temporal en el cielo
#   (z=30000) mirando +X y un plano con M_CreditosFinal a 120 cm con la rotacion relativa candidata;
#   renderiza cada candidata a un RenderTarget y la exporta a PNG. Borra los actores temporales.
import unreal, json, traceback, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_render.json"
DIRP = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_render"
os.makedirs(DIRP, exist_ok=True)
try:
    CANDS
except NameError:
    CANDS = [(90, 0, 90), (-90, 0, 90), (90, 0, -90), (-90, 0, -90), (0, 90, 0), (0, -90, 0)]
res = {"err": None, "files": []}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    rt = unreal.RenderingLibrary.create_render_target2d(world, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    base = unreal.Vector(0, 0, 30000)
    cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, base, unreal.Rotator(0, 0, 0))
    cap.set_actor_label("TMP_VerifCap")
    cc = cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt); cc.set_editor_property("fov_angle", 90.0)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    plane = unreal.EditorLevelLibrary.spawn_actor_from_object(unreal.load_asset("/Engine/BasicShapes/Plane"), base + unreal.Vector(120, 0, 0))
    plane.set_actor_label("TMP_VerifPlano")
    pc = plane.static_mesh_component; pc.set_material(0, unreal.load_asset("/Game/JWN/FX/M_CreditosFinal"))
    plane.set_actor_scale3d(unreal.Vector(0.9, 1.6, 1.0))
    for (rr, pp, yy) in CANDS:
        plane.set_actor_rotation(unreal.Rotator(rr, pp, yy), False)
        cc.capture_scene()
        fn = "cand_r%d_p%d_y%d.png" % (rr, pp, yy)
        unreal.RenderingLibrary.export_render_target(world, rt, DIRP, fn)
        res["files"].append(fn)
    unreal.EditorLevelLibrary.destroy_actor(cap); unreal.EditorLevelLibrary.destroy_actor(plane)
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
