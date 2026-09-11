# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) Optimizacion SIN impacto visual para la plaza. El follaje bajo del bosque (pasto/helecho/arbusto/
#   planta pequena) se dibuja hasta 180-250m donde es sub-pixel (invisible). Baja su cull a ~90-120m. NO toca arboles
#   (Oak/Maple/Tropical) ni rocas ni el anillo de horizonte (HORIZ_ISM) ni flores. Solo achica lo invisible. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_follaje.json"
res = {"tocados": [], "instancias_afectadas": 0, "err": []}
SMALL = ["grassforest", "fern", "forestbush", "forestplant", "mossy_grass"]
NEW_START = 9000.0
NEW_END = 12000.0
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name().lower()
            if not any(k in nm for k in SMALL): continue
            end = c.get_editor_property("instance_end_cull_distance")
            if end and end > NEW_END:  # solo apretar, nunca aflojar
                cnt = c.get_instance_count()
                c.set_editor_property("instance_start_cull_distance", int(NEW_START))
                c.set_editor_property("instance_end_cull_distance", int(NEW_END))
                res["tocados"].append([a.get_actor_label()[:20], m.get_name(), cnt, "%d->%d"%(end, NEW_END)])
                res["instancias_afectadas"] += cnt
        except Exception as e:
            res["err"].append(str(e)[:50])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("CULL FOLLAJE %d grupos, %d inst" % (len(res["tocados"]), res["instancias_afectadas"]))
