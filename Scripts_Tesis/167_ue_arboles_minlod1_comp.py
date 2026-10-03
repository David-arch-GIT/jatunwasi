# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) min_lod=1 a NIVEL DE COMPONENTE (como ronda 15) en los componentes cuyo mesh es un ARBOL PESADO
#   (LOD0>1500, >=4 LODs). Baja los arboles cercanos a LOD1 (mitad de tris); los lejanos siguen a billboard (min_lod
#   solo limita el detalle maximo). Reduce tris de la plaza ~30% (mas fluido + frames mas cortos = menos cuelgue).
#   Guarda el nivel. Reversible (min_lod=0). Reporta cuantos componentes toco.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/arboles_minlod_comp.json"
res = {"comp_tocados": 0, "por_mesh": {}, "err": []}
TREE = ["oak","maple","tropicaltree","dead_tree","pine","palm","birch","willow"]
eas = unreal.EditorActorSubsystem()
# cache de "es pesado?" por mesh
heavy_cache = {}
def is_heavy(m):
    nm = m.get_name()
    if nm in heavy_cache: return heavy_cache[nm]
    low = nm.lower()
    ok = False
    if any(k in low for k in TREE):
        try:
            if m.get_num_lods() >= 4 and m.get_num_triangles(0) > 1500:
                ok = True
        except Exception:
            ok = False
    heavy_cache[nm] = ok
    return ok
def set_comp_minlod(c, val):
    done = False
    for prop in ["override_min_lod", "b_override_min_lod"]:
        try: c.set_editor_property(prop, True); done = True; break
        except Exception: pass
    try:
        c.set_editor_property("min_lod", val); return True
    except Exception as e:
        res["err"].append("minlod:" + str(e)[:34]); return done
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            m = c.get_editor_property("static_mesh")
            if not m or not is_heavy(m): continue
            if set_comp_minlod(c, 1):
                res["comp_tocados"] += 1
                nm = m.get_name()
                res["por_mesh"][nm] = res["por_mesh"].get(nm, 0) + 1
        except Exception as e:
            res["err"].append(str(e)[:34])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ARBOLES minlod comp=%d" % res["comp_tocados"])
