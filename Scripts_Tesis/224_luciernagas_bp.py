# 224_luciernagas_bp.py - BP con HISM para luciernagas + colocar + instancias
import unreal, json, math, random, traceback
R={"steps":[],"n":0,"err":[]}
random.seed(21)
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    fmat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/FX/M_Firefly")
    sph=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    bpp="/Game/JWN/FX/BP_Fireflies"
    if not unreal.EditorAssetLibrary.does_asset_exist(bpp):
        f=unreal.BlueprintFactory(); f.set_editor_property("parent_class", unreal.Actor)
        bp=AT.create_asset("BP_Fireflies","/Game/JWN/FX",unreal.Blueprint,f)
        handles=sds.k2_gather_subobject_data_for_blueprint(bp)
        root=handles[0]
        for h in handles:
            d=sds.k2_find_subobject_data_from_handle(h); o=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
            if o and o.get_name().startswith("DefaultSceneRoot"): root=h
        params=unreal.AddNewSubobjectParams()
        params.set_editor_property("parent_handle", root)
        params.set_editor_property("new_class", unreal.HierarchicalInstancedStaticMeshComponent)
        params.set_editor_property("blueprint_context", bp)
        nh,fail=sds.add_new_subobject(params)
        sds.rename_subobject(nh, unreal.Text("Enjambre"))
        d=sds.k2_find_subobject_data_from_handle(nh); hism=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        hism.set_static_mesh(sph); hism.set_material(0, fmat)
        hism.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        hism.set_editor_property("cast_shadow", False)
        hism.set_editor_property("instance_start_cull_distance", 4000)
        hism.set_editor_property("instance_end_cull_distance", 6000)
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        unreal.EditorAssetLibrary.save_asset(bpp)
    R["steps"].append("bp")
    gen=unreal.EditorAssetLibrary.load_blueprint_class(bpp)
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="FX_Luciernagas": eas.destroy_actor(a)
    act=eas.spawn_actor_from_class(gen, unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    act.set_actor_label("FX_Luciernagas")
    hism=act.get_component_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    centers=[(0,-1000,900),(-750,-400,500),(3400,1750,500),(600,-520,400),(5950,4250,600),(50,9550,600),(-4135,668,500),(-7250,-820,500)]
    for cx,cy,rad in centers:
        for i in range(22):
            ang=random.uniform(0,6.283); r=random.uniform(80,rad)
            x=cx+math.cos(ang)*r; y=cy+math.sin(ang)*r; z=random.uniform(50,210)
            hism.add_instance(unreal.Transform(unreal.Vector(x,y,z), unreal.Rotator(0,0,0), unreal.Vector(0.035,0.035,0.035)))
            R["n"]+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luc_bp.json","w").write(json.dumps(R))
