# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Sube la niebla nocturna (atmosferica, oculta lo lejano) para poder recortar mas agresivo la
#   vegetacion lejana de la plaza SIN que se note (la niebla la tapa) = fluidez en la zona abierta. Guarda (persiste tapetes).
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_niebla.json"
res = {"fog_density": None, "cull_ajustados": 0, "err": []}
eas = unreal.EditorActorSubsystem()
CX, CY, R = 0.0, -1000.0, 7000.0
# subir niebla (moderada, atmosferica)
for a in eas.get_all_level_actors():
    if "ExponentialHeightFog" in a.get_class().get_name():
        fc = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fc:
            try:
                fc.set_editor_property("fog_density", 0.03)   # 0.015 -> 0.03 (haze nocturno)
                fc.set_editor_property("start_distance", 1500.0)  # cerca nitido, lejos con haze
                res["fog_density"] = 0.03
            except Exception as e:
                res["err"].append("fog: %s" % e)
# recortar mas la vegetacion lejana de la plaza (la niebla tapa el recorte)
def cull(nm):
    n = nm.lower()
    if "grass" in n or "pasto" in n or "shrub" in n: return (1500, 2500)
    if "garden" in n or "flower" in n or "fern" in n or "boxwood" in n or "seto" in n: return (2200, 3200)
    if "hacfor" in n or "bosque" in n or "tree" in n or "forest" in n or "impostor" in n: return (3500, 5000)
    return (2500, 3500)
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
            if comp.get_instance_count() < 20: continue
            s, e = cull(lbl)
            comp.set_editor_property("instance_start_cull_distance", int(s))
            comp.set_editor_property("instance_end_cull_distance", int(e))
            res["cull_ajustados"] += 1
        except Exception as ex:
            res["err"].append(str(ex)[:40])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA NIEBLA density=%s cull=%d" % (res["fog_density"], res["cull_ajustados"]))
