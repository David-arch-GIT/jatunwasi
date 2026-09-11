# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) Audita el costo de rendimiento de la escena para Quest 2: luces (tipo/mobility/sombra dinamica),
#   post-process volumes, niebla, foliage/HISM/PCG (conteo de instancias), y actores mas pesados. Reporta a JSON.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/perf_audit.json"
res = {"dir_lights": [], "shadow_lights": 0, "lights_total": 0, "ppv": [], "fog": [], "foliage": [], "hism_top": []}
eas = unreal.EditorActorSubsystem()
acts = eas.get_all_level_actors()
hism_counts = {}
for a in acts:
    cls = a.get_class().get_name()
    # luces
    lc = a.get_component_by_class(unreal.LightComponent)
    if lc:
        res["lights_total"] += 1
        try: casts = lc.get_editor_property("cast_shadows")
        except Exception: casts = None
        try: mob = str(a.root_component.get_editor_property("mobility"))
        except Exception: mob = "?"
        if casts and "MOVABLE" in mob.upper():
            res["shadow_lights"] += 1
        if a.get_component_by_class(unreal.DirectionalLightComponent):
            dl = a.get_component_by_class(unreal.DirectionalLightComponent)
            info = {"label": a.get_actor_label(), "mobility": mob, "cast": bool(casts)}
            for p in ["dynamic_shadow_distance_movable_light", "dynamic_shadow_distance_stationary_light", "num_dynamic_shadow_cascades", "cascade_distribution_exponent"]:
                try: info[p] = round(float(dl.get_editor_property(p)), 1)
                except Exception: pass
            res["dir_lights"].append(info)
    # post process
    if cls == "PostProcessVolume" or a.get_component_by_class(unreal.PostProcessComponent):
        res["ppv"].append(a.get_actor_label())
    # fog
    if "Fog" in cls:
        res["fog"].append(a.get_actor_label() + " [" + cls + "]")
    # foliage / HISM / ISM
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try: n = comp.get_instance_count()
        except Exception: n = 0
        key = a.get_actor_label()
        hism_counts[key] = hism_counts.get(key, 0) + n
foliage_total = sum(hism_counts.values())
res["foliage_total_instances"] = foliage_total
res["hism_top"] = sorted([{"actor": k, "inst": v} for k, v in hism_counts.items()], key=lambda d: -d["inst"])[:15]
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PERF AUDIT done foliage=%d shadowlights=%d" % (foliage_total, res["shadow_lights"]))
