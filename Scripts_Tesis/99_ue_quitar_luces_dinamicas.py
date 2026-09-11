# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) Golpe REAL de rendimiento: DESACTIVA (visibility off) las 105 PointLights + 4 SpotLights movable
#   (su costo CPU/render-thread por-frame es el cuello de botella; los emisivos mantienen el brillo del look).
#   Devuelve la sombra dinamica de la luna a dist 2500 (grounding, la GPU ya tiene espacio) y afloja el cull de
#   vegetacion (menos popping). Guarda un JSON con conteos. REVERSIBLE (visibility).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/quitar_luces.json"
res = {"apagadas": 0, "moon": None, "foliage": 0, "err": []}
eas = unreal.EditorActorSubsystem()
acts = eas.get_all_level_actors()
for a in acts:
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        if cls in ("PointLightComponent", "SpotLightComponent"):
            try:
                lc.set_visibility(False, False)   # apaga (reversible), quita costo por-frame
                res["apagadas"] += 1
            except Exception as e:
                res["err"].append("off %s: %s" % (a.get_actor_label(), e))
        if cls == "DirectionalLightComponent":
            try:
                lc.set_editor_property("cast_shadows", True)
                lc.set_editor_property("dynamic_shadow_distance_movable_light", 2500.0)
                res["moon"] = "sombra ON dist 2500"
            except Exception as e:
                res["err"].append("moon: %s" % e)

def cull(nm):
    n = nm.lower()
    if "horiz" in n: return (16000, 20000)
    if "bosque" in n or "hacfor" in n or "tree" in n or "arbol" in n: return (9000, 13000)
    if "grass" in n or "shrub" in n or "garden" in n or "cesped" in n: return (4000, 5500)
    return (6000, 8000)
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
unreal.log("QUITAR LUCES done apagadas=%d moon=%s" % (res["apagadas"], res["moon"]))
