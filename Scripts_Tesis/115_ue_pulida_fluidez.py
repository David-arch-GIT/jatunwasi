# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Pulida final de fluidez SEGURA (no cambia el look, no quita instancias):
#   - Cull global coherente por categoria (lo lejano se deja de dibujar, lo cercano intacto).
#   - Confirma cast_shadows=False en TODAS las luces point/spot + luna (sombras dinamicas = caras).
#   - No toca cantidad de plantas ni materiales. Guarda. Reporta.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/pulida.json"
res = {"cull": 0, "luces_sombra_off": 0, "luna": 0, "err": []}
eas = unreal.EditorActorSubsystem()
def cull_for(nm):
    n = nm.lower()
    if "grass" in n or "pasto" in n or "shrub" in n or "arbust" in n or "cesped" in n:
        return (2500, 3500)
    if "garden" in n or "jardin" in n or "flower" in n or "fern" in n or "helecho" in n or "boxwood" in n or "seto" in n:
        return (3500, 4800)
    if "horiz" in n:
        return (16000, 20000)
    if "bosque" in n or "hacfor" in n or "tree" in n or "arbol" in n or "forest" in n or "impostor" in n:
        return (7000, 9500)
    return (5000, 6500)
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            if comp.get_instance_count() < 20:
                continue
            s, e = cull_for(lbl)
            comp.set_editor_property("instance_start_cull_distance", int(s))
            comp.set_editor_property("instance_end_cull_distance", int(e))
            res["cull"] += 1
        except Exception as ex:
            res["err"].append("%s: %s" % (lbl, str(ex)[:50]))
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        try:
            if cls in ("PointLightComponent", "SpotLightComponent"):
                lc.set_editor_property("cast_shadows", False)
                res["luces_sombra_off"] += 1
            elif cls == "DirectionalLightComponent":
                lc.set_editor_property("cast_shadows", False)
                res["luna"] += 1
        except Exception as ex:
            res["err"].append("luz %s: %s" % (lbl, str(ex)[:50]))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PULIDA cull=%d sombras_off=%d luna=%d" % (res["cull"], res["luces_sombra_off"], res["luna"]))
