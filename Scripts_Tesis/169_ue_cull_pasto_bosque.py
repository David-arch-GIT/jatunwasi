# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) ANTI-LENTITUD bosque/caminos. El pasto/helecho/arbusto/planta del bosque (PCG_BosqueVol) tenia cull
#   12000 (120m): a esa distancia el ground-cover no se distingue, solo overdraw+tris. Baja SOLO los de cull>=10000 a
#   5000 (start 4000) -> el cercano NO se toca (cero thinning visible), quita el lejano invisible. Gran baja de tris
#   del bosque. NO toca arboles ni flores ni los ya cerca (<10000). Guarda nivel. Reversible.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_pasto.json"
res = {"tocados": [], "err": []}
GROUND = ["grassforest", "fern", "forestbush", "forestplant", "clover", "_grass", "shrub"]
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name().lower()
            if not any(k in nm for k in GROUND): continue
            ce = c.get_editor_property("instance_end_cull_distance")
            if ce is None or ce < 10000: continue
            n = c.get_instance_count()
            c.set_editor_property("instance_start_cull_distance", 4000)
            c.set_editor_property("instance_end_cull_distance", 5000)
            res["tocados"].append([a.get_actor_label()[:18], m.get_name(), n, ce])
        except Exception as e:
            res["err"].append(str(e)[:36])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
res["n"] = len(res["tocados"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("CULL PASTO n=%d" % len(res["tocados"]))
