# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) Lee ajustes de PostProcessVolume(s) que sean caros en Quest (bloom, AO, motion blur, lens flare, DOF,
#   auto-exposure) + reporta si hay volumenes ilimitados. Solo lee, escribe JSON. Para decidir apagar post caro.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/postproc.json"
res = {"volumenes": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if not isinstance(a, unreal.PostProcessVolume):
        continue
    try:
        s = a.get_editor_property("settings")
        unbound = a.get_editor_property("unbound")
        prio = a.get_editor_property("priority")
        info = {"lab": a.get_actor_label()[:30], "unbound": bool(unbound), "prio": prio}
        for key, ov, val in [
            ("bloom", "override_bloom_intensity", "bloom_intensity"),
            ("ao", "override_ambient_occlusion_intensity", "ambient_occlusion_intensity"),
            ("motionblur", "override_motion_blur_amount", "motion_blur_amount"),
            ("dof", "override_depth_of_field_focal_distance", "depth_of_field_focal_distance"),
            ("expo_method", "override_auto_exposure_method", "auto_exposure_method"),
            ("expo_min", "override_auto_exposure_min_brightness", "auto_exposure_min_brightness"),
        ]:
            try:
                o = s.get_editor_property(ov)
                v = s.get_editor_property(val)
                info[key] = [bool(o), str(v)]
            except Exception:
                pass
        res["volumenes"].append(info)
    except Exception as e:
        res["err"].append(str(e)[:50])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("POSTPROC vols=%d" % len(res["volumenes"]))
