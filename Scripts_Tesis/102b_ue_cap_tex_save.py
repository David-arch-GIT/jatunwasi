# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) Re-capa Texture2D /Game/ a max 1024 y GUARDA correctamente (pasando OBJETOS a save_loaded_assets).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_tex2.json"
res = {"capadas": 0, "guardadas": 0, "err": 0, "total": 0}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
assets = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Texture2D"), True)
res["total"] = len(assets)
CAP = 1024
objs = []
for d in assets:
    try:
        p = str(d.package_name)
        if not p.startswith("/Game/"):
            continue
        t = unreal.load_asset(p + "." + str(d.asset_name))
        if t is None:
            continue
        cur = int(t.get_editor_property("max_texture_size"))
        if cur == 0 or cur > CAP:
            t.set_editor_property("max_texture_size", CAP)
            objs.append(t)
            res["capadas"] += 1
    except Exception:
        res["err"] += 1
# guardar en lotes de 100 (objetos)
try:
    B = 100
    for i in range(0, len(objs), B):
        unreal.EditorAssetLibrary.save_loaded_assets(objs[i:i+B], False)
        res["guardadas"] += len(objs[i:i+B])
except Exception as e:
    res["save_err"] = str(e)
open(OUT, "w").write(json.dumps(res))
unreal.log("CAP TEX2 capadas=%d guardadas=%d" % (res["capadas"], res["guardadas"]))
