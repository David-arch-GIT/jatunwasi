# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) Mide COSTO de la plaza para hallar lo mas pesado que quede: por cada componente StaticMesh/ISM en
#   radio, calcula tris RENDERIZADOS estimados = tris(min_lod efectivo) x instancias. Tambien draw calls (componentes)
#   y luces movable. Ranking de mallas por tris totales para decidir donde bajar LOD/densidad. Solo mide, escribe JSON.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_tris.json"
CX, CY, R = 0.0, -1000.0, 3500.0
res = {"total_tris_est": 0, "draw_calls": 0, "luces_movable": 0, "por_mesh": {}, "err": []}
eas = unreal.EditorActorSubsystem()
def d2(loc): return math.hypot(loc.x - CX, loc.y - CY)
def tris_at(mesh, lod):
    try: return mesh.get_num_triangles(lod)
    except Exception: return 0
def eff_min_lod(c, mesh):
    # intenta leer override de min_lod del componente; si no, 0
    try:
        v = c.get_editor_property("min_lod")
        # PerPlatformInt -> .default o int
        try: return int(v.get_editor_property("default"))
        except Exception:
            return int(v)
    except Exception:
        return 0
mesh_tris = {}
for a in eas.get_all_level_actors():
    try: loc = a.get_actor_location()
    except Exception: continue
    if d2(loc) > R: continue
    for lc in a.get_components_by_class(unreal.LightComponent):
        try:
            if "MOVABLE" in str(lc.get_editor_property("mobility")): res["luces_movable"] += 1
        except Exception: pass
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m: continue
            res["draw_calls"] += 1
            nm = m.get_name()
            nlods = 1
            try: nlods = m.get_num_lods()
            except Exception: pass
            ml = eff_min_lod(c, m)
            if ml < 0: ml = 0
            if ml > nlods - 1: ml = nlods - 1
            t = tris_at(m, ml)
            if isinstance(c, unreal.InstancedStaticMeshComponent):
                try: n = c.get_instance_count()
                except Exception: n = 1
            else:
                n = 1
            total = t * max(n, 1)
            res["total_tris_est"] += total
            if nm not in mesh_tris:
                mesh_tris[nm] = {"tris_lod0": tris_at(m, 0), "tris_min": t, "min_lod": ml, "nlods": nlods, "inst": 0, "total": 0}
            mesh_tris[nm]["inst"] += n
            mesh_tris[nm]["total"] += total
        except Exception as e:
            res["err"].append(str(e)[:40])
# top 25 por total
top = sorted(mesh_tris.items(), key=lambda kv: -kv[1]["total"])[:25]
res["por_mesh"] = {k: v for k, v in top}
res["total_tris_millones"] = round(res["total_tris_est"] / 1e6, 2)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA TRIS total=%.2fM draws=%d luces=%d" % (res["total_tris_millones"], res["draw_calls"], res["luces_movable"]))
