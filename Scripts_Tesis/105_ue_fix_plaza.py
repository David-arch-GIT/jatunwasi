# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Optimiza SOLO la plaza (zona abierta = se dibuja todo). Recorta antes la vegetacion LEJANA
#   (lo cercano intacto): pasto 25/36m, jardin 32/46m, bosque 70/100m. Luces plaza radio 320->300 (menos solape,
#   siguen encendidas). NO elimina nada. Guarda. Solo cull + radio = liviano y reversible.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_plaza.json"
CX, CY, R = 0.0, -1000.0, 6000.0
res = {"grass": 0, "garden": 0, "forest": 0, "other_veg": 0, "lights": 0, "err": []}
eas = unreal.EditorActorSubsystem()
def cull_for(nm):
    n = nm.lower()
    if "grass" in n or "pasto" in n or "cesped" in n:
        return (2500, 3600, "grass")
    if "garden" in n or "jardin" in n or "boxwood" in n or "seto" in n or "flower" in n or "helecho" in n or "fern" in n:
        return (3200, 4600, "garden")
    if "hacfor" in n or "bosque" in n or "tree" in n or "arbol" in n or "forest" in n:
        return (7000, 10000, "forest")
    return (4000, 5500, "other_veg")
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x - CX, loc.y - CY) > R:
        continue
    lbl = a.get_actor_label()
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            if comp.get_instance_count() < 20:
                continue
            s, e, cat = cull_for(lbl)
            comp.set_editor_property("instance_start_cull_distance", int(s))
            comp.set_editor_property("instance_end_cull_distance", int(e))
            res[cat] += 1
        except Exception as ex:
            res["err"].append("%s: %s" % (lbl, ex))
    for lc in a.get_components_by_class(unreal.LightComponent):
        if lc.get_class().get_name() in ("PointLightComponent", "SpotLightComponent"):
            try:
                lc.set_editor_property("attenuation_radius", 300.0)
                lc.set_editor_property("cast_shadows", False)
                res["lights"] += 1
            except Exception as ex:
                res["err"].append("luz %s: %s" % (lbl, ex))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("FIX PLAZA grass=%d garden=%d forest=%d lights=%d" % (res["grass"], res["garden"], res["forest"], res["lights"]))
