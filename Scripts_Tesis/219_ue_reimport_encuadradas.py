import unreal, json, os
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reimport.json"
res = {"reimport": [], "err": []}
SRCDIR = r"C:/UnrealProjects/JatunWasiNawpakay/Content/FotosAntano/Encuadradas"
DEST = "/Game/FotosAntano/Encuadradas"
at = unreal.AssetToolsHelpers.get_asset_tools()
for f in sorted(os.listdir(SRCDIR)):
    if not f.lower().endswith(".png"): continue
    try:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", os.path.join(SRCDIR, f))
        task.set_editor_property("destination_path", DEST)
        task.set_editor_property("automated", True); task.set_editor_property("save", True); task.set_editor_property("replace_existing", True)
        at.import_asset_tasks([task])
        for p in list(task.get_editor_property("imported_object_paths")):
            base = p.split(".")[0]
            tex = unreal.EditorAssetLibrary.load_asset(base)
            if isinstance(tex, unreal.Texture2D):
                tex.set_editor_property("max_texture_size", 2048)
                unreal.EditorAssetLibrary.save_asset(base, only_if_is_dirty=False)
                res["reimport"].append(tex.get_name())
    except Exception as e:
        res["err"].append(f[:18]+":"+str(e)[:40])
open(OUT,"w").write(json.dumps(res, indent=1))
