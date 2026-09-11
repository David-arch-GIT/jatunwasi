# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) ALIGERA FUERTE la plaza para que cargue confiable y vaya fluida en Quest 2.
#   Recorta MUY cerca la vegetacion pesada (impostores de arbol, jardin, pasto) = menos shaders pesados a compilar
#   al entrar + menos carga por frame. Luces: radio 250 + apagado lejano (siguen encendidas, menos solape/permutaciones).
#   NO borra nada (solo cull + radio, reversible). Guarda.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/aligerar_plaza.json"
CX, CY, R = 0.0, -1000.0, 7000.0
res = {"forest": 0, "garden": 0, "grass": 0, "other": 0, "lights": 0, "err": []}
eas = unreal.EditorActorSubsystem()
def cull_for(nm):
    n = nm.lower()
    if "grass" in n or "pasto" in n or "cesped" in n:
        return (1500, 2500, "grass")
    if "garden" in n or "jardin" in n or "boxwood" in n or "seto" in n or "flower" in n or "fern" in n or "helecho" in n:
        return (2000, 3000, "garden")
    if "hacfor" in n or "bosque" in n or "tree" in n or "arbol" in n or "forest" in n or "impostor" in n:
        return (2500, 3800, "forest")
    return (2500, 3500, "other")
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
                lc.set_editor_property("attenuation_radius", 250.0)
                lc.set_editor_property("cast_shadows", False)
                lc.set_editor_property("max_draw_distance", 900.0)
                lc.set_editor_property("max_distance_fade_range", 200.0)
                res["lights"] += 1
            except Exception as ex:
                res["err"].append("luz %s: %s" % (lbl, ex))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ALIGERAR PLAZA forest=%d garden=%d grass=%d lights=%d" % (res["forest"], res["garden"], res["grass"], res["lights"]))
