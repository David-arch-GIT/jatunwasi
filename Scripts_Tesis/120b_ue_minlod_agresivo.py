# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) MinLOD AGRESIVO en vegetacion con LOD0 monstruoso (boxwood hasta 398k tris/planta!).
#   >100k tris -> LOD mas bajo; >20k -> LOD3; >8k -> LOD2. Ahorro brutal de vertices sin cambiar el look apreciable
#   (son setos/plantas de fondo). Guarda. Reporta ahorro estimado.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/minlod_agresivo.json"
res = {"comps": 0, "ahorro_est_Mtris": 0.0, "detalle": [], "err": []}
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
    # tris del LOD objetivo (para estimar ahorro)
    cache[nm] = (t0, nl)
    return cache[nm]
for a in eas.get_all_level_actors():
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m: continue
            t0, nl = info(m)
            if nl < 3: continue
            if t0 > 100000:
                target = nl - 1
            elif t0 > 20000:
                target = min(3, nl - 1)
            elif t0 > 8000:
                target = 2
            else:
                continue
            comp.set_editor_property("override_min_lod", True)
            comp.set_editor_property("min_lod", target)
            res["comps"] += 1
            cnt = comp.get_instance_count()
            try:
                tt = m.get_num_triangles(target)
            except Exception:
                tt = 0
            res["ahorro_est_Mtris"] += (t0 - tt) * cnt / 1000000.0
            if len(res["detalle"]) < 12:
                res["detalle"].append([m.get_name()[:30], t0, "LOD%d(%d tris)" % (target, tt), "x%d inst" % cnt])
        except Exception as ex:
            res["err"].append(str(ex)[:50])
res["ahorro_est_Mtris"] = round(res["ahorro_est_Mtris"], 1)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MINLOD AGRESIVO comps=%d ahorro=%.1fM tris" % (res["comps"], res["ahorro_est_Mtris"]))
