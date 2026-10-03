import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/limpiar.json"
res={"borrado":[]}
EAL=unreal.EditorAssetLibrary
for p in ["/Game/FotosAntano/Encuadradas/ZZ_CALIB","/Game/FotosAntano/Encuadradas/MI_CALIB"]:
    if EAL.does_asset_exist(p):
        EAL.delete_asset(p); res["borrado"].append(p)
# guardar nivel + assets sucios
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
EAL.save_directory("/Game/FotosAntano", only_if_is_dirty=True, recursive=True)
res["ok"]=True
open(OUT,"w").write(json.dumps(res,indent=1))
