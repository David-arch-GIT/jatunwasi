import unreal, json, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_tex.json"
res = {"tex": []}
DEST = "/Game/FotosAntano/Encuadradas"
for a in unreal.EditorAssetLibrary.list_assets(DEST, recursive=False):
    base = a.split(".")[0]
    t = unreal.EditorAssetLibrary.load_asset(base)
    if isinstance(t, unreal.Texture2D):
        try:
            w = t.blueprint_get_size_x(); h = t.blueprint_get_size_y()
        except Exception:
            w = t.get_editor_property("imported_size").x if hasattr(t,"get_editor_property") else 0
            h = 0
        comp = str(t.get_editor_property("compression_settings"))
        res["tex"].append({"n": t.get_name(), "w": int(w), "h": int(h), "comp": comp.split(".")[-1]})
res["count"] = len(res["tex"])
open(OUT,"w").write(json.dumps(res, indent=1))
