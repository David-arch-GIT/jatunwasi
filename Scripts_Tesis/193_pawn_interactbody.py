# 193_pawn_interactbody.py (v2)
# Configura la CapsuleComponent "InteractBody" del BP_XRPawn (creada antes) para proximidad.
import unreal, json, traceback
R={"steps":[], "err":[]}
try:
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    bp=unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    handles=sds.k2_gather_subobject_data_for_blueprint(bp)
    parent_h=None; cap=None
    for h in handles:
        d=sds.k2_find_subobject_data_from_handle(h)
        obj=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if not obj: continue
        nm=obj.get_name()
        if nm.startswith("VROrigin") and parent_h is None: parent_h=h
        if nm.startswith("InteractBody"): cap=obj
    if cap is None:
        params=unreal.AddNewSubobjectParams()
        params.set_editor_property("parent_handle", parent_h or handles[0])
        params.set_editor_property("new_class", unreal.CapsuleComponent)
        params.set_editor_property("blueprint_context", bp)
        new_h, fail = sds.add_new_subobject(params)
        sds.rename_subobject(new_h, unreal.Text("InteractBody"))
        d=sds.k2_find_subobject_data_from_handle(new_h)
        cap=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        R["steps"].append("created add_fail='%s'"%str(fail))
    else:
        R["steps"].append("found_existing")
    # configurar (API correcta)
    cap.set_capsule_size(55.0, 95.0, True)
    cap.set_editor_property("relative_location", unreal.Vector(0.0,0.0,-95.0))
    cap.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
    cap.set_collision_object_type(unreal.CollisionChannel.ECC_PAWN)
    cap.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_OVERLAP)
    cap.set_editor_property("generate_overlap_events", True)
    cap.set_editor_property("can_ever_affect_navigation", False)
    cap.set_editor_property("hidden_in_game", True)
    R["steps"].append("configured")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    R["steps"].append("compiled_saved")
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/interactbody.json","w").write(json.dumps(R))
