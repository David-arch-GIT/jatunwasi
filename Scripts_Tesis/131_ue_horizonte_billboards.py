# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Horizonte lleno pero barato: quita el min_lod FORZADO de los arboles (para que los lejanos usen su
#   LOD billboard = plano barato) y afloja el cull del bosque/horizonte para que llenen la vista. Con r.StaticMeshLODDistanceScale=2
#   los cercanos igual usan LOD ligero. Boxwood/flores/pasto NO se tocan. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/horizonte_bb.json"
res = {"trees_liberados": 0, "cull_bosque": 0, "cull_horiz": 0, "err": []}
eas = unreal.EditorActorSubsystem()
TREE = ["oak","maple","tropicaltree","tropical_tree","dead_tree","palm","pine","pino","arbol","_tree","forest","bosque","hacfor","ptree"]
def is_tree(nm):
    n = nm.lower()
    return any(k in n for k in TREE) and "boxwood" not in n and "grass" not in n
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label(); low = lbl.lower()
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m: continue
            if is_tree(m.get_name()) or is_tree(lbl):
                # liberar min_lod (permitir toda la cadena incl billboard)
                comp.set_editor_property("override_min_lod", False)
                comp.set_editor_property("min_lod", 0)
                res["trees_liberados"] += 1
                # aflojar cull para llenar horizonte
                isinst = comp.get_class().get_name() in ("InstancedStaticMeshComponent","HierarchicalInstancedStaticMeshComponent")
                if isinst:
                    if "horiz" in low:
                        comp.set_editor_property("instance_start_cull_distance", 30000)
                        comp.set_editor_property("instance_end_cull_distance", 42000)
                        res["cull_horiz"] += 1
                    else:
                        comp.set_editor_property("instance_start_cull_distance", 18000)
                        comp.set_editor_property("instance_end_cull_distance", 25000)
                        res["cull_bosque"] += 1
        except Exception as ex:
            res["err"].append(str(ex)[:50])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("HORIZONTE BB trees=%d bosque=%d horiz=%d" % (res["trees_liberados"], res["cull_bosque"], res["cull_horiz"]))
