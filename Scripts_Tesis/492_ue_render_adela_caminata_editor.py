# 492_ue_render_adela_caminata_editor.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: verificacion VISUAL (mundo del editor) de como se ve Adela al caminar con el componente de guia:
#   misma orientacion que aplica UJWGuiaComponent (yaw = direccion de marcha + YawOffsetMalla(-90)) y la
#   animacion A_Adela_walk_sitio a mitad de paso. Camara 4.5 m DELANTE en la direccion de marcha (debe verse
#   de frente) y otra de COSTADO. Restaura rotacion y animacion originales y NO guarda.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/render492.json"
DIRP = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_render"
res = {"err": None}
tmp = []
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    a = [x for x in unreal.EditorLevelLibrary.get_all_level_actors() if x.get_actor_label() == "Adela_Convai"][0]
    sk = a.get_component_by_class(unreal.SkeletalMeshComponent)
    rot0 = a.get_actor_rotation()
    walk = unreal.load_asset("/Game/JWN/Characters/AdelaFinal/A_Adela_walk_sitio")
    marcha = 90.0  # camina hacia +Y (norte, como hacia el templo)
    a.set_actor_rotation(unreal.Rotator(0, marcha - 90.0, 0), False)
    sk.set_update_animation_in_editor(True)
    sk.play_animation(walk, True)
    sk.set_position(walk.get_play_length() * 0.25, False)
    sk.set_play_rate(0.0)
    L = a.get_actor_location(); f = math.radians(marcha)
    rt = unreal.RenderingLibrary.create_render_target2d(w, 640, 640, unreal.TextureRenderTargetFormat.RTF_RGBA8)
    for nom, ang in (("frente", 0.0), ("costado", math.pi / 2)):
        P = unreal.Vector(L.x + 450 * math.cos(f + ang), L.y + 450 * math.sin(f + ang), L.z + 120)
        rr = unreal.MathLibrary.find_look_at_rotation(P, unreal.Vector(L.x, L.y, L.z + 90))
        cap = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.SceneCapture2D, P, rr); tmp.append(cap)
        cc = cap.get_component_by_class(unreal.SceneCaptureComponent2D)
        cc.set_editor_property("texture_target", rt); cc.set_editor_property("fov_angle", 50.0)
        cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        cc.capture_scene(); unreal.RenderingLibrary.export_render_target(w, rt, DIRP, "adela_walk_%s.png" % nom)
    res["ok"] = True
except Exception:
    res["err"] = traceback.format_exc()[:1200]
finally:
    for t in tmp: unreal.EditorLevelLibrary.destroy_actor(t)
    try:
        a.set_actor_rotation(rot0, False)
        sk.set_play_rate(1.0)
        sk.play_animation(unreal.load_asset("/Game/JWN/Characters/AdelaFinal/A_Adela_idle"), True)
        sk.set_update_animation_in_editor(False)
    except Exception:
        pass
open(OUT, "w").write(json.dumps(res))
