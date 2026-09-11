# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) ANTI-LENTITUD PLAZA. Reduce distancia de cull del follaje que genera overdraw al recorrer, SIN tocar
#   la vista cercana ni la calidad: (A) arboles horizonte HORIZ_ISM (Maple/Oak/Tropical) cull 42000->24000 (siguen de
#   fondo, pero se dejan de dibujar copas masked lejanas superpuestas). (B) follaje bajo HACFOR/JW_ENV/HACFOR grass
#   (fern/bush/plant/grass) cull 12000->9000. Deja banda de fade (start<end) para que NO haga pop. NO toca flores PCG
#   (3200, ya cerca) ni caminos. Guarda. Reversible (los valores viejos quedan en git/backup del umap).
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_cull.json"
CX, CY, R = 0.0, -1000.0, 4000.0
res = {"arboles": [], "follaje_bajo": [], "err": []}
eas = unreal.EditorActorSubsystem()
def d2(loc): return math.hypot(loc.x - CX, loc.y - CY)
TREES = ["maple","oak","tropicaltree","birch","willow","pine"]
LOW = ["fern","bush","plant","grass","clover","shrub","forestplant"]
def set_cull(c, start, end):
    c.set_editor_property("instance_start_cull_distance", start)
    c.set_editor_property("instance_end_cull_distance", end)
for a in eas.get_all_level_actors():
    try: loc = a.get_actor_location()
    except Exception: continue
    if d2(loc) > R: continue
    lab = a.get_actor_label()
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            nm = m.get_name().lower()
            ce = c.get_editor_property("instance_end_cull_distance")
            if any(k in nm for k in TREES) and ce >= 30000:
                set_cull(c, 20000, 24000)
                res["arboles"].append({"lab": lab[:22], "mesh": nm[:22], "de": ce, "a": 24000})
            elif any(k in nm for k in LOW) and 9000 < ce <= 15000:
                set_cull(c, 7000, 9000)
                res["follaje_bajo"].append({"lab": lab[:22], "mesh": nm[:22], "de": ce, "a": 9000})
        except Exception as e:
            res["err"].append(str(e)[:40])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
res["n_arboles"] = len(res["arboles"]); res["n_follaje"] = len(res["follaje_bajo"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA CULL arboles=%d follaje=%d" % (len(res["arboles"]), len(res["follaje_bajo"])))
