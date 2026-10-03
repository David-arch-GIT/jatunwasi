import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/twosided.json"
EAL=unreal.EditorAssetLibrary; MEL=unreal.MaterialEditingLibrary
mat=EAL.load_asset("/Game/FotosAntano/M_FotoPlane")
mat.set_editor_property("two_sided", True)
MEL.recompile_material(mat)
EAL.save_asset("/Game/FotosAntano/M_FotoPlane", only_if_is_dirty=False)
res={"two_sided": bool(mat.get_editor_property("two_sided")),
     "shading": str(mat.get_editor_property("shading_model"))}
open(OUT,"w").write(json.dumps(res))
