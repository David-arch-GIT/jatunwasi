# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) AJUSTE FINO del cull de arboles de horizonte HORIZ_ISM. En script 159 los baje a 24000 (240m) pero la
#   ronda 16 los fijo a proposito en 300-420m para que el horizonte NO se vea pelado/plano. Los subo a 30000 (300m,
#   start 26000): mantiene el horizonte lleno y aun recorta la banda mas lejana (300-420m) de overdraw. El follaje bajo
#   (9000) NO se toca. Solo HORIZ_ISM. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/horiz_ajuste.json"
res = {"ajustados": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("HORIZ_ISM"):
        continue
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            ce = c.get_editor_property("instance_end_cull_distance")
            c.set_editor_property("instance_start_cull_distance", 26000)
            c.set_editor_property("instance_end_cull_distance", 30000)
            res["ajustados"].append({"lab": lab[:22], "de": ce, "a": 30000})
        except Exception as e:
            res["err"].append(str(e)[:40])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
res["n"] = len(res["ajustados"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("HORIZ AJUSTE n=%d" % len(res["ajustados"]))
