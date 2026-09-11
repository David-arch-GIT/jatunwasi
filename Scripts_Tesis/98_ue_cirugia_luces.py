# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) CIRUGIA de rendimiento (golpe grande) SIN perder look cercano:
#   (1) 105 PointLights + 4 SpotLights: reduce attenuation_radius (glow local, no wide) + max_draw_distance 1500 + sin sombra;
#   (2) MoonLight: DESACTIVA sombra dinamica (cast_shadows=False) = gran ahorro GPU (sombras sutiles de noche);
#   (3) foliage: cull mas agresivo (bosque 6000, grass 2000) para bajar overdraw manteniendo paisaje.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cirugia.json"
res = {"lights_shrunk": 0, "radii_antes": [], "moon": None, "foliage": 0, "err": []}
eas = unreal.EditorActorSubsystem()
acts = eas.get_all_level_actors()

for a in acts:
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        if cls in ("PointLightComponent", "SpotLightComponent"):
            try:
                r = float(lc.get_editor_property("attenuation_radius"))
                if len(res["radii_antes"]) < 8: res["radii_antes"].append(round(r))
                nr = min(r, 400.0)          # cap: glow local, no ilumina medio mapa
                lc.set_editor_property("attenuation_radius", nr)
                lc.set_editor_property("max_draw_distance", 1500.0)
                lc.set_editor_property("max_distance_fade_range", 400.0)
                lc.set_editor_property("cast_shadows", False)
                res["lights_shrunk"] += 1
            except Exception as e:
                res["err"].append("light %s: %s" % (a.get_actor_label(), e))
        if cls == "DirectionalLightComponent":
            try:
                lc.set_editor_property("cast_shadows", False)   # sin sombra dinamica = gran ahorro
                res["moon"] = "sombra dinamica OFF"
            except Exception as e:
                res["err"].append("moon: %s" % e)

def cull(nm):
    n = nm.lower()
    if "horiz" in n: return (14000, 18000)
    if "bosque" in n or "hacfor" in n or "tree" in n or "arbol" in n: return (5500, 8000)
    if "grass" in n or "shrub" in n or "garden" in n or "cesped" in n: return (2000, 3200)
    return (3500, 5000)
for a in acts:
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            if comp.get_instance_count() < 50: continue
            s, e = cull(a.get_actor_label())
            comp.set_editor_property("instance_start_cull_distance", int(s))
            comp.set_editor_property("instance_end_cull_distance", int(e))
            res["foliage"] += 1
        except Exception as ex:
            res["err"].append("hism %s: %s" % (a.get_actor_label(), ex))

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("CIRUGIA done lights=%d foliage=%d moon=%s" % (res["lights_shrunk"], res["foliage"], res["moon"]))
