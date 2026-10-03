# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) Auditoria GLOBAL (todo el mapa, sin radio): top mallas por tris renderizados estimados
#   (tris(min_lod efectivo) x instancias). Para hallar cosas pesadas fuera de la plaza (bosque, otras zonas).
#   Tambien total de draw calls (componentes con mesh). Solo mide, escribe JSON.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_global.json"
res = {"total_tris_M": 0.0, "draw_calls": 0, "por_mesh": {}, "err": []}
eas = unreal.EditorActorSubsystem()
def tris_at(m, l):
    try: return m.get_num_triangles(l)
    except Exception: return 0
def eff_min_lod(c, nlods):
    try:
        v = c.get_editor_property("min_lod")
        try: ml = int(v.get_editor_property("default"))
        except Exception: ml = int(v)
    except Exception:
        ml = 0
    if ml < 0: ml = 0
    if ml > nlods - 1: ml = nlods - 1
    return ml
mesh = {}
total = 0
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            res["draw_calls"] += 1
            nm = m.get_name()
            nl = 1
            try: nl = m.get_num_lods()
            except Exception: pass
            ml = eff_min_lod(c, nl)
            t = tris_at(m, ml)
            n = c.get_instance_count() if isinstance(c, unreal.InstancedStaticMeshComponent) else 1
            tot = t * max(n, 1)
            total += tot
            if nm not in mesh:
                mesh[nm] = {"lod0": tris_at(m, 0), "min_lod": ml, "tris_min": t, "inst": 0, "total": 0, "nlods": nl}
            mesh[nm]["inst"] += n
            mesh[nm]["total"] += tot
        except Exception as e:
            res["err"].append(str(e)[:30])
top = sorted(mesh.items(), key=lambda kv: -kv[1]["total"])[:25]
res["por_mesh"] = {k: v for k, v in top}
res["total_tris_M"] = round(total / 1e6, 2)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("AUDIT GLOBAL total=%.1fM draws=%d" % (res["total_tris_M"], res["draw_calls"]))
