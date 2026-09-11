# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Rellena el horizonte pelado: afloja el cull del bosque/horizonte para que los arboles LEJANOS
#   se dibujen (llenan la vista) — son baratos porque estan lejos (usan LOD bajo). No agrega instancias, solo
#   permite que las existentes se vean mas lejos. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/horizonte.json"
res = {"horiz": 0, "bosque": 0, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label(); n = lbl.lower()
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            if comp.get_instance_count() < 20: continue
            if "horiz" in n:
                comp.set_editor_property("instance_start_cull_distance", 40000)
                comp.set_editor_property("instance_end_cull_distance", 55000)
                res["horiz"] += 1
            elif "bosque" in n or "hacfor" in n or "forest" in n:
                # bosque general: llenar mas lejos (arboles distantes baratos)
                comp.set_editor_property("instance_start_cull_distance", 14000)
                comp.set_editor_property("instance_end_cull_distance", 20000)
                res["bosque"] += 1
        except Exception as ex:
            res["err"].append(str(ex)[:50])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("HORIZONTE horiz=%d bosque=%d" % (res["horiz"], res["bosque"]))
