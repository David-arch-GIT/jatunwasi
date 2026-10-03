# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-11
# Que hace: (UE) ANTI-LENTITUD + ANTI-CUELGUE (frames mas cortos). Pone min_lod=1 en las mallas de ARBOL PESADAS
#   (LOD0>1500 tris, >=4 LODs) para que los cercanos usen LOD1 (mitad de tris) en vez de LOD0. NO bloquea billboards
#   lejanos (min_lod solo limita el detalle maximo, no el minimo) -> el horizonte sigue lleno. Es la version SUAVE del
#   intento de la ronda 16 (que uso min_lod=2, muy agresivo). Guarda cada malla. Reversible (min_lod=0).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/arboles_minlod.json"
res = {"ajustadas": [], "saltadas": [], "err": []}
TREE = ["oak","maple","tropicaltree","birch","willow","pine","dead_tree","deadtree","palm","_tree_"]
ar = unreal.AssetRegistryHelpers.get_asset_registry()
allsm = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "StaticMesh"), True)
def set_minlod1(m):
    # intenta varias formas segun la API de PerPlatformInt
    try:
        ppi = unreal.PerPlatformInt(); ppi.set_editor_property("default", 1)
        m.set_editor_property("min_lod", ppi); return True
    except Exception:
        pass
    try:
        m.set_editor_property("min_lod", unreal.PerPlatformInt(1)); return True
    except Exception:
        pass
    try:
        m.set_editor_property("min_lod", 1); return True
    except Exception:
        return False
seen = set()
for a in allsm:
    pkg = str(a.package_name); nm = str(a.asset_name); low = nm.lower()
    if not pkg.startswith("/Game"): continue
    if nm in seen: continue
    if not any(k in low for k in TREE): continue
    seen.add(nm)
    try:
        m = unreal.EditorAssetLibrary.load_asset(pkg)
        if not m: continue
        nl = m.get_num_lods()
        t0 = m.get_num_triangles(0) if nl >= 1 else 0
        if nl < 4 or t0 <= 1500:
            res["saltadas"].append([nm, t0, nl]); continue
        ok = set_minlod1(m)
        if ok:
            unreal.EditorAssetLibrary.save_asset(pkg, only_if_is_dirty=False)
            res["ajustadas"].append([nm, t0, m.get_num_triangles(1)])
        else:
            res["err"].append("no set minlod:" + nm)
    except Exception as e:
        res["err"].append(nm + ":" + str(e)[:36])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
res["n"] = len(res["ajustadas"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ARBOLES minlod1 n=%d" % len(res["ajustadas"]))
