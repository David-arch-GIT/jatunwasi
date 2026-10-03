# Verifica: evento Alternar en BP_Cartela, compilacion de ambos BPs, nivel actual.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_bps.json"
res={}
EAL=unreal.EditorAssetLibrary
# nivel actual
try:
    w=unreal.EditorLevelLibrary.get_editor_world()
    res["nivel"]=w.get_name()
    res["actores"]=len(unreal.EditorActorSubsystem().get_all_level_actors())
except Exception as e:
    res["nivel_err"]=str(e)[:50]
# BP_Cartela: existe Alternar?
try:
    cls=EAL.load_blueprint_class("/Game/Cartelas/BP_Cartela")
    cdo=unreal.get_default_object(cls)
    metodos=[m for m in dir(cdo) if not m.startswith("_")]
    res["cartela_tiene_alternar"]= ("alternar" in [m.lower() for m in metodos])
    res["cartela_metodos_custom"]=[m for m in metodos if "altern" in m.lower() or "abr" in m.lower() or "toggle" in m.lower()]
except Exception as e:
    res["cartela_err"]=str(e)[:60]
# compilar ambos
for name,path in [("BP_Cartela","/Game/Cartelas/BP_Cartela"),("BP_XRPawn","/Game/XRFramework/Blueprints/BP_XRPawn")]:
    try:
        bp=EAL.load_asset(path)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        res[name+"_compile"]="compilado (sin excepcion)"
    except Exception as e:
        res[name+"_compile"]="ERR:"+str(e)[:50]
open(OUT,"w").write(json.dumps(res,indent=1))
