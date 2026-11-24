# 465_ue_compilar_todos_bp.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (verificacion) compilar TODOS los Blueprints del proyecto bajo /Game (excepto packs de terceros
#   Megascans/StylescapeHD) y reportar su estado (status). Cualquier BS_ERROR = bloqueo para el APK.
#   No guarda nada.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/compilar_todos.json"
res = {"err": None, "malos": [], "n": 0}
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ads = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Blueprint"), True)
    for ad in ads:
        p = str(ad.package_name)
        if not p.startswith("/Game/") or p.startswith(("/Game/Megascans", "/Game/StylescapeHD", "/Game/Fab")): continue
        bp = ad.get_asset()
        if bp is None: continue
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        try:
            st = str(bp.get_editor_property("status"))
        except Exception:
            st = "?"
        res["n"] += 1
        if "UP_TO_DATE" not in st.upper():
            res["malos"].append([p, st])
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
