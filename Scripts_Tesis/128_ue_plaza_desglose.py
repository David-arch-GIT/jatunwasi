# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) SOLO LECTURA. Desglosa la plaza por MALLA: suma de tris RENDERIZADOS (min_lod) x instancias.
#   Muestra los top contribuyentes al ~10M restante, para atacar el proximo cuello.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_desglose.json"
CX, CY, R = 0.0, -1000.0, 5500.0
res = {"total_tris": 0, "por_malla": [], "err": []}
eas = unreal.EditorActorSubsystem()
from collections import defaultdict
agg = defaultdict(lambda: [0, 0])  # mesh -> [tris_totales, instancias]
cache = {}
def rtris(m, ml):
    k = (m.get_name(), ml)
    if k in cache: return cache[k]
    try: t = m.get_num_triangles(ml)
    except Exception: t = 0
    cache[k] = t; return t
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x-CX, loc.y-CY) > R:
        continue
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        m = comp.get_editor_property("static_mesh")
        if not m: continue
        isinst = comp.get_class().get_name() in ("InstancedStaticMeshComponent","HierarchicalInstancedStaticMeshComponent")
        try:
            ml = int(comp.get_editor_property("min_lod")) if comp.get_editor_property("override_min_lod") else 0
        except Exception:
            ml = 0
        cnt = comp.get_instance_count() if isinst else 1
        tt = rtris(m, ml) * cnt
        nm = m.get_name()
        agg[nm][0] += tt; agg[nm][1] += cnt
        res["total_tris"] += tt
items = sorted(agg.items(), key=lambda kv: -kv[1][0])[:20]
res["por_malla"] = [[k, v[0], v[1]] for k, v in items]
res["total_tris_M"] = round(res["total_tris"]/1000000.0, 2)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA DESGLOSE total=%.2fM" % res["total_tris_M"])
