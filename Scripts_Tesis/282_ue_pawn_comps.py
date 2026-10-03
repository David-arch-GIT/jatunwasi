import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/pawncomps.json"
res={"comps":[], "err":None}
try:
    EAL=unreal.EditorAssetLibrary
    bp=EAL.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles=sds.k2_gather_subobject_data_for_blueprint(bp)
    for h in handles:
        try:
            data=sds.k2_find_subobject_data_from_handle(h)
            obj=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
            if obj:
                res["comps"].append(obj.get_name()+" ["+obj.get_class().get_name()+"]")
        except Exception as ex:
            res["comps"].append("errnode:"+str(ex)[:40])
except Exception as e:
    res["err"]=str(e)[:200]
open(OUT,"w").write(json.dumps(res,indent=1))
