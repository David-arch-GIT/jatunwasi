# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) Capa la resolucion MAXIMA de todas las Texture2D a 1024 (el Quest no muestra mas) -> baja memoria y
#   tiempo de carga (arregla el "se traba al inicio" y "sin texturas") SIN tocar luces ni geometria ni el look.
#   NO borra nada (solo set max_texture_size + save). Reporta cuantas cambio.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_tex.json"
res = {"capadas": 0, "ya_ok": 0, "err": 0, "total": 0}
ar = unreal.AssetRegistryHelpers.get_asset_registry()
assets = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Texture2D"), True)
res["total"] = len(assets)
CAP = 1024
saved = []
for d in assets:
    try:
        p = str(d.package_name)
        # saltar texturas de engine/plugins
        if not p.startswith("/Game/"):
            continue
        t = unreal.load_asset(str(d.package_name) + "." + str(d.asset_name))
        if t is None:
            continue
        cur = int(t.get_editor_property("max_texture_size"))
        # tamano real
        w = t.blueprint_get_size_x() if hasattr(t, "blueprint_get_size_x") else 0
        if (cur == 0 or cur > CAP):
            t.set_editor_property("max_texture_size", CAP)
            saved.append(str(d.package_name))
            res["capadas"] += 1
        else:
            res["ya_ok"] += 1
    except Exception:
        res["err"] += 1
# guardar en lote
try:
    unreal.EditorAssetLibrary.save_loaded_assets(saved, only_if_is_dirty=False) if saved else None
except Exception as e:
    res["save_err"] = str(e)
open(OUT, "w").write(json.dumps(res))
unreal.log("CAP TEX capadas=%d de %d" % (res["capadas"], res["total"]))
