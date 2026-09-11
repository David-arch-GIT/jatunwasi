# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Fuerza LOD mas liviano en los ARBOLES de la plaza (Oak/Maple/Tropical/DeadTree) y boxwood restante.
#   Estan en LOD0 completo (4-6k tris x cientos). A LOD2 cuestan ~4x menos y siguen viendose como arboles 3D.
#   Global (afecta todas las zonas = mejora todo). Guarda. Reporta ahorro.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/arboles_lod.json"
res = {"comps": 0, "ahorro_est": 0, "err": []}
eas = unreal.EditorActorSubsystem()
KW = ["oak", "maple", "tropicaltree", "tropical_tree", "_tree", "dead_tree", "palm", "boxwood", "elderberry", "hydrangea", "bush", "shrub"]
cache = {}
def info(m):
    nm = m.get_name()
    if nm in cache: return cache[nm]
    try: t0 = m.get_num_triangles(0)
    except Exception: t0 = 0
    try: nl = m.get_num_lods()
    except Exception:
        try: nl = m.get_num_l_o_ds()
        except Exception: nl = 1
    cache[nm] = (t0, nl); return cache[nm]
for a in eas.get_all_level_actors():
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m: continue
            low = m.get_name().lower()
            if not any(k in low for k in KW): continue
            t0, nl = info(m)
            if nl < 3: continue
            # target: LOD2, pero no el ultimo (degenerado)
            target = min(2, nl - 2)
            if target < 1: target = 1
            isinst = comp.get_class().get_name() in ("InstancedStaticMeshComponent","HierarchicalInstancedStaticMeshComponent")
            cnt = comp.get_instance_count() if isinst else 1
            try:
                curml = int(comp.get_editor_property("min_lod")) if comp.get_editor_property("override_min_lod") else 0
            except Exception:
                curml = 0
            if target <= curml:
                continue
            before = m.get_num_triangles(curml) * cnt
            comp.set_editor_property("override_min_lod", True)
            comp.set_editor_property("min_lod", int(target))
            after = m.get_num_triangles(target) * cnt
            res["ahorro_est"] += (before - after)
            res["comps"] += 1
        except Exception as ex:
            res["err"].append(str(ex)[:50])
res["ahorro_est_M"] = round(res["ahorro_est"]/1000000.0, 2)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ARBOLES LOD comps=%d ahorro=%.2fM" % (res["comps"], res["ahorro_est_M"]))
