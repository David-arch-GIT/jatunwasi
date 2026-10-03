# Revierte slope NavMesh a 44 (como build53) + inspecciona BP_XRPawn: componentes y variables de reset/recovery.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/revert_inspect.json"
res={"slope":{}, "pawn_components":[], "pawn_vars":{}}
# 1) revertir slope
eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if "RecastNavMesh" in a.get_class().get_name():
        res["slope"]["antes"]=a.get_editor_property("agent_max_slope")
        a.set_editor_property("agent_max_slope", 44.0)
        res["slope"]["ahora"]=a.get_editor_property("agent_max_slope")
        break
unreal.EditorLoadingAndSavingUtils.save_current_level()
res["slope"]["guardado"]=True

# 2) inspeccionar pawn - componentes via SubobjectData
try:
    bp=unreal.EditorAssetLibrary.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles=sds.k2_gather_subobject_data_for_blueprint(bp)
    for h in handles:
        try:
            data=sds.k2_find_subobject_data_from_handle(h)
            obj=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
            if obj:
                res["pawn_components"].append(obj.get_name()+" ["+obj.get_class().get_name()+"]")
        except Exception:
            pass
except Exception as e:
    res["pawn_components_err"]=str(e)[:80]

# 3) variables de reset/recovery/home
try:
    pc=unreal.EditorAssetLibrary.load_blueprint_class("/Game/XRFramework/Blueprints/BP_XRPawn")
    cdo=unreal.get_default_object(pc)
    CANDS=["RecoveryLocation","HomeLocation","StartLocation","ResetLocation","RespawnLocation","SafeLocation",
     "DefaultLocation","InitialLocation","bResetOnFall","FallThreshold","FallZ","KillZ","MinZ","bTeleportToStart",
     "PlazaLocation","InicioLocation","ReturnLocation","LastValidLocation","bUseNavMeshGate","NavMeshGate",
     "bConstrainToNavMesh","MaxDistanceFromNav","bResetIfOffNav","SnapToNavMesh","bClampToNavMesh"]
    for n in CANDS:
        try:
            v=cdo.get_editor_property(n)
            res["pawn_vars"][n]=str(v)
        except Exception:
            pass
except Exception as e:
    res["pawn_vars_err"]=str(e)[:80]
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
