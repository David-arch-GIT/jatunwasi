# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Reajusta MinLOD: tope en LOD3 (NUNCA LOD4 que es degenerado/8tris=desaparece).
#   Vegetacion LOD0 >20k -> LOD3 (seto 3D real, ~90% menos tris); 8k-20k -> LOD2. Mantiene el look. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/minlod_lod3.json"
res = {"comps": 0, "err": []}
eas = unreal.EditorActorSubsystem()
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
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m: continue
            t0, nl = info(m)
            if nl < 3: continue
            if t0 > 20000:
                target = min(3, nl - 2)   # LOD3 pero deja al menos un LOD por debajo (evita el degenerado final)
                target = max(target, 2)
            elif t0 > 8000:
                target = 2
            else:
                continue
            # asegurar que target no sea el LOD final degenerado
            if target >= nl - 1:
                target = nl - 2 if nl >= 3 else 1
            comp.set_editor_property("override_min_lod", True)
            comp.set_editor_property("min_lod", int(target))
            res["comps"] += 1
        except Exception as ex:
            res["err"].append(str(ex)[:50])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MINLOD LOD3 comps=%d" % res["comps"])
