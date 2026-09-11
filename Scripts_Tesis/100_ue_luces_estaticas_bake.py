# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) Prepara la iluminacion para HORNEAR (baked): re-enciende las 109 point/spot lights, las pone STATIC
#   (su luz se hornea en lightmaps = casi cero costo en runtime), restaura su radio/alcance y quita el cull.
#   Pone el MoonLight en STATIONARY (hornea sombras del sol/luna). Asi: iluminado como antes, pero fluido tras el bake.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luces_estaticas.json"
res = {"static_lights": 0, "moon": None, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        if cls in ("PointLightComponent", "SpotLightComponent"):
            try:
                lc.set_visibility(True, False)                 # re-encender
                lc.set_editor_property("attenuation_radius", 700.0)  # restaurar alcance
                lc.set_editor_property("max_draw_distance", 0.0)     # sin cull (horneado = gratis)
                lc.set_editor_property("cast_shadows", True)         # sombras horneadas OK
                a.root_component.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
                res["static_lights"] += 1
            except Exception as e:
                res["err"].append("%s: %s" % (a.get_actor_label(), e))
        if cls == "DirectionalLightComponent":
            try:
                a.root_component.set_editor_property("mobility", unreal.ComponentMobility.STATIONARY)
                lc.set_editor_property("cast_shadows", True)
                res["moon"] = "moon STATIONARY (sombra horneada)"
            except Exception as e:
                res["err"].append("moon: %s" % e)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("LUCES ESTATICAS done static=%d moon=%s" % (res["static_lights"], res["moon"]))
