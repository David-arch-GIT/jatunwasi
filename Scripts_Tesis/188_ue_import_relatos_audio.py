# 188_ue_import_relatos_audio.py
# Importa las 4 voces de relato (TTS Sabina) a /Game/JWN/Audio/Relatos como SoundWave,
# en MONO, con streaming activado (optimizado Quest 2). No cablea nada, solo crea assets.
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"importados":[], "err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    src="C:/UnrealProjects/JatunWasiNawpakay/Content/JWN/Audio/Relatos"
    dst="/Game/JWN/Audio/Relatos"
    for z in ["plaza","hacienda","convento","templo"]:
        task=unreal.AssetImportTask()
        task.filename="%s/relato_%s.wav"%(src,z)
        task.destination_path=dst
        task.destination_name="A_Relato_%s"%z
        task.automated=True; task.replace_existing=True; task.save=True
        AT.import_asset_tasks([task])
        ap="%s/A_Relato_%s"%(dst,z)
        sw=unreal.EditorAssetLibrary.load_asset(ap)
        if sw:
            try: sw.set_editor_property("streaming", True)
            except Exception as e: R["err"].append("stream_%s:%s"%(z,str(e)[:40]))
            try: sw.set_editor_property("compression_quality", 40)
            except Exception as e: R["err"].append("cq_%s:%s"%(z,str(e)[:40]))
            unreal.EditorAssetLibrary.save_asset(ap)
            R["importados"].append(z)
        else:
            R["err"].append("no_load_%s"%z)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/import_relatos.json","w").write(json.dumps(R))
print("IMPORT_RELATOS", json.dumps({"ok":R.get("ok"),"n":len(R["importados"]),"err":R["err"][:4]}))
