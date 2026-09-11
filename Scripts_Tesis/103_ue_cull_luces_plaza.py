# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Sube FPS SIN quitar luces: las luces lejanas se APAGAN solas y se encienden al acercarte
#   (max_draw_distance 1400, fade 300). Radio 320 (zona iluminada contenida). Sombras OFF. Skylight sube a 1.4
#   (relleno ambiente para que lo lejano no quede negro). Guarda el nivel. Solo toca LUCES = liviano, sin riesgo.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_luces.json"
res = {"lights": 0, "moon": 0, "sky": 0, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        try:
            if cls in ("PointLightComponent", "SpotLightComponent"):
                lc.set_editor_property("cast_shadows", False)
                lc.set_editor_property("attenuation_radius", 320.0)
                lc.set_editor_property("max_draw_distance", 1400.0)   # se apaga a >14m
                lc.set_editor_property("max_distance_fade_range", 300.0)
                res["lights"] += 1
            elif cls == "DirectionalLightComponent":
                lc.set_editor_property("cast_shadows", False)
                res["moon"] += 1
            elif cls == "SkyLightComponent":
                lc.set_editor_property("intensity", 1.4)   # relleno para que lo lejano no quede negro
                res["sky"] += 1
        except Exception as e:
            res["err"].append("%s: %s" % (a.get_actor_label(), e))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("CULL LUCES lights=%d moon=%d sky=%d" % (res["lights"], res["moon"], res["sky"]))
