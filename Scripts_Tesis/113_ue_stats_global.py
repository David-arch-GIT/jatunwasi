# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) SOLO LECTURA. Mide el peso de instancias (ISM/HISM) de TODO el mapa, agrupado por prefijo de nombre,
#   para decidir donde adelgazar globalmente (no solo plaza). Reporta total y top grupos.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/stats_global.json"
res = {"total_inst": 0, "total_comps": 0, "grupos": {}, "top_actores": []}
eas = unreal.EditorActorSubsystem()
from collections import defaultdict
grp = defaultdict(lambda: [0, 0])  # prefijo -> [comps, instancias]
actores = []
def prefix(nm):
    n = nm.split("_")[0:2]
    return "_".join(n)
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    tot_a = 0
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            c = comp.get_instance_count()
        except Exception:
            continue
        if c <= 0:
            continue
        res["total_inst"] += c
        res["total_comps"] += 1
        tot_a += c
        p = prefix(lbl)
        grp[p][0] += 1
        grp[p][1] += c
    if tot_a > 300:
        actores.append((lbl, tot_a))
res["grupos"] = {k: {"comps": v[0], "inst": v[1]} for k, v in sorted(grp.items(), key=lambda x: -x[1][1])[:25]}
actores.sort(key=lambda t: -t[1])
res["top_actores"] = actores[:25]
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("STATS GLOBAL total_inst=%d comps=%d" % (res["total_inst"], res["total_comps"]))
