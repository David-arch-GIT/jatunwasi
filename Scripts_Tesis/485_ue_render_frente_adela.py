# 485_ue_render_frente_adela.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: verificar que el FRENTE de la malla de Adela es el eje +X del actor (lo que asume el
#   componente de guia al caminar/mirar). Dos SceneCapture temporales a 3 m: una en +X del actor y otra en
#   -X, ambas mirando a Adela. Exporta adela_masX.png / adela_menosX.png. Borra los temporales. No guarda.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/render_adela.json"
DIRP = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_render"
res = {"err": None}
tmp = []
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    a = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "Adela_Convai"][0]
    L = a.get_actor_location(); yaw = math.radians(a.get_actor_rotation().yaw)
    rt = unreal.RenderingLibrary.create_render_target2d(w, 640, 640, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    for nom, s in (("adela_masX.png", 1), ("adela_menosX.png", -1)):
        P = unreal.Vector(L.x + s * 300 * math.cos(yaw), L.y + s * 300 * math.sin(yaw), L.z + 130)
        rot = unreal.MathLibrary.find_look_at_rotation(P, unreal.Vector(L.x, L.y, L.z + 100))
        cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, P, rot); tmp.append(cap)
        cc = cap.get_component_by_class(unreal.SceneCaptureComponent2D)
        cc.set_editor_property("texture_target", rt); cc.set_editor_property("fov_angle", 60.0)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        cc.capture_scene(); unreal.RenderingLibrary.export_render_target(w, rt, DIRP, nom)
    res["ok"] = True; res["yaw"] = a.get_actor_rotation().yaw
except Exception:
    res["err"] = traceback.format_exc()[:1200]
finally:
    for t in tmp: unreal.EditorLevelLibrary.destroy_actor(t)
open(OUT, "w").write(json.dumps(res))
