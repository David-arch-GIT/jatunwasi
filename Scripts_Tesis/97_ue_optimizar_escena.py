# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) Optimiza rendimiento Quest SIN perder look: (1) 105 PointLights + 4 SpotLights movable -> max_draw_distance
#   (se apagan las lejanas, enorme ahorro en mobile forward); (2) MoonLight sombra dinamica 3500->1800 + 2 cascadas;
#   (3) foliage HISM cull por categoria (grass cerca, bosque/horizonte lejos) para bajar overdraw manteniendo paisaje.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/optimizar.json"
res = {"lights": 0, "moon": None, "foliage": [], "err": []}
eas = unreal.EditorActorSubsystem()
acts = eas.get_all_level_actors()

# 1) luces: cull por distancia (apaga lejanas). NO tocar intensidad/radio (para no cambiar el look cercano)
for a in acts:
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        if cls in ("PointLightComponent", "SpotLightComponent"):
            try:
                lc.set_editor_property("max_draw_distance", 3000.0)
                lc.set_editor_property("max_distance_fade_range", 600.0)
                lc.set_editor_property("cast_shadows", False)  # asegurar sin sombras dinamicas (caro)
                res["lights"] += 1
            except Exception as e:
                res["err"].append("light %s: %s" % (a.get_actor_label(), e))
        if cls == "DirectionalLightComponent":
            try:
                lc.set_editor_property("dynamic_shadow_distance_movable_light", 1800.0)
                lc.set_editor_property("num_dynamic_shadow_cascades", 2)
                res["moon"] = "shadow 1800 / 2 cascadas"
            except Exception as e:
                res["err"].append("moon: %s" % e)

# 2) foliage HISM: cull por categoria (mantiene paisaje: bosque/horizonte lejos, grass cerca)
def cats(nm):
    n = nm.lower()
    if "horiz" in n:            return (16000, 20000)   # backdrop lejano, casi no cull
    if "bosque" in n or "hacfor" in n or "tree" in n or "arbol" in n: return (8000, 11000)  # bosque lejos
    if "grass" in n or "shrub" in n or "garden" in n or "cesped" in n: return (3000, 4500)  # grass cerca
    return (5000, 7000)
for a in acts:
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            n = comp.get_instance_count()
            if n < 50: continue
            s, e = cats(a.get_actor_label())
            comp.set_editor_property("instance_start_cull_distance", int(s))
            comp.set_editor_property("instance_end_cull_distance", int(e))
            res["foliage"].append({"actor": a.get_actor_label(), "inst": n, "cull": [s, e]})
        except Exception as ex:
            res["err"].append("hism %s: %s" % (a.get_actor_label(), ex))

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("OPTIMIZAR done lights=%d foliage=%d" % (res["lights"], len(res["foliage"])))
