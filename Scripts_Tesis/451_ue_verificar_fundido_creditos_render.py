# 451_ue_verificar_fundido_creditos_render.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: verificar VISUALMENTE el instante final: esfera de fundido (M_FadeFinal, opacidad 1 forzando
#   T0 del MPC_Final en el pasado) rodeando la camara + plano de creditos (rot 90,0,90) delante.
#   SceneCapture temporal en z=30000; exporta fundido_creditos.png y fundido_solo.png. Restaura T0=1e6
#   y borra actores temporales. No guarda nada.
import unreal, json, traceback, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fundido_render.json"
DIRP = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_render"
res = {"err": None}
tmp = []
world = unreal.EditorLevelLibrary.get_editor_world()
mpc = unreal.load_asset("/Game/JWN/FX/MPC_Final")
try:
    rt = unreal.RenderingLibrary.create_render_target2d(world, 960, 540, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    base = unreal.Vector(0, 0, 30000)
    cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, base, unreal.Rotator(0, 0, 0)); tmp.append(cap)
    cc = cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt); cc.set_editor_property("fov_angle", 90.0)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    sph = unreal.EditorLevelLibrary.spawn_actor_from_object(unreal.load_asset("/Engine/BasicShapes/Sphere"), base); tmp.append(sph)
    sph.set_actor_scale3d(unreal.Vector(0.6, 0.6, 0.6))
    sc = sph.static_mesh_component; sc.set_material(0, unreal.load_asset("/Game/JWN/FX/M_FadeFinal")); sc.set_translucent_sort_priority(10)
    plane = unreal.EditorLevelLibrary.spawn_actor_from_object(unreal.load_asset("/Engine/BasicShapes/Plane"), base + unreal.Vector(120, 0, 0)); tmp.append(plane)
    plane.set_actor_rotation(unreal.Rotator(90, 0, 90), False); plane.set_actor_scale3d(unreal.Vector(1.4, 0.7875, 1.0))  # escala corregida en 452
    pc = plane.static_mesh_component; pc.set_material(0, unreal.load_asset("/Game/JWN/FX/M_CreditosFinal")); pc.set_translucent_sort_priority(20)
    unreal.MaterialLibrary.set_scalar_parameter_value(world, mpc, "T0", -100000.0)
    pc.set_visibility(False)
    cc.capture_scene(); unreal.RenderingLibrary.export_render_target(world, rt, DIRP, "fundido_solo.png")
    pc.set_visibility(True)
    cc.capture_scene(); unreal.RenderingLibrary.export_render_target(world, rt, DIRP, "fundido_creditos.png")
    res["ok"] = True
except Exception:
    res["err"] = traceback.format_exc()[:1200]
finally:
    unreal.MaterialLibrary.set_scalar_parameter_value(world, mpc, "T0", 1000000.0)
    for a in tmp:
        unreal.EditorLevelLibrary.destroy_actor(a)
open(OUT, "w").write(json.dumps(res))
