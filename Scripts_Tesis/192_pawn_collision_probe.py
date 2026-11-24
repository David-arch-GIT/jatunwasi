# 192_pawn_collision_probe.py - inspecciona colisiones del BP_XRPawn para overlap
import unreal, json, traceback
R={"comps":[], "has_overlap":False}
try:
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    bp=unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    R["bp_loaded"]=bp is not None
    handles=sds.k2_gather_subobject_data_for_blueprint(bp)
    R["n_handles"]=len(handles)
    for h in handles:
        d=sds.k2_find_subobject_data_from_handle(h)
        obj=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if not obj: continue
        cn=obj.get_class().get_name()
        info={"name":obj.get_name(),"cls":cn}
        try:
            if isinstance(obj, unreal.PrimitiveComponent):
                info["col"]=str(obj.get_collision_enabled()).split(".")[-1]
                info["goe"]=bool(obj.get_editor_property("generate_overlap_events"))
                info["prof"]=str(obj.get_collision_profile_name())
                if info["goe"]: R["has_overlap"]=True
        except Exception as e:
            info["e"]=str(e)[:40]
        R["comps"].append(info)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/pawn_comps.json","w").write(json.dumps(R))
