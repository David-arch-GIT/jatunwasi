# 221_minimapa.py - importa el mapa, material emisivo, y lo cuelga en la esquina de la vista (hijo de la Camara del Pawn)
import unreal, json, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    # 1) importar textura
    t=unreal.AssetImportTask()
    t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/map/T_Minimapa.png")
    t.set_editor_property("destination_path","/Game/JWN/UI")
    t.set_editor_property("destination_name","T_Minimapa")
    t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
    AT.import_asset_tasks([t])
    R["steps"].append("tex")
    # 2) material unlit emisivo
    mp="/Game/JWN/UI/M_Minimapa"
    if not unreal.EditorAssetLibrary.does_asset_exist(mp):
        mat=AT.create_asset("M_Minimapa","/Game/JWN/UI",unreal.Material,unreal.MaterialFactoryNew())
        tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/T_Minimapa")
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0); ts.set_editor_property("texture",tex)
        mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-150,0); mul.set_editor_property("const_b",1.3)
        mel.connect_material_expressions(ts,"RGB",mul,"A")
        mel.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mel.recompile_material(mat); unreal.EditorAssetLibrary.save_asset(mp)
    R["steps"].append("mat")
    # 3) agregar plano al Pawn, hijo de la Camara
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    bp=unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    handles=sds.k2_gather_subobject_data_for_blueprint(bp)
    cam_h=None; exists=False
    for h in handles:
        d=sds.k2_find_subobject_data_from_handle(h)
        obj=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if not obj: continue
        nm=obj.get_name()
        if nm.startswith("Camera") and cam_h is None: cam_h=h
        if nm.startswith("Minimapa"): exists=True
    R["steps"].append("cam:%s exists:%s"%(cam_h is not None, exists))
    if not exists and cam_h:
        params=unreal.AddNewSubobjectParams()
        params.set_editor_property("parent_handle", cam_h)
        params.set_editor_property("new_class", unreal.StaticMeshComponent)
        params.set_editor_property("blueprint_context", bp)
        nh,fail=sds.add_new_subobject(params)
        sds.rename_subobject(nh, unreal.Text("Minimapa"))
        d=sds.k2_find_subobject_data_from_handle(nh)
        comp=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        plane=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
        matm=unreal.EditorAssetLibrary.load_asset(mp)
        comp.set_static_mesh(plane)
        comp.set_material(0, matm)
        comp.set_editor_property("relative_location", unreal.Vector(130.0, 62.0, -46.0))
        # plano mira a la camara (normal -X), textura arriba = +Z
        rot=unreal.MathLibrary.make_rot_from_zy(unreal.Vector(-1,0,0), unreal.Vector(0,0,1))
        comp.set_editor_property("relative_rotation", rot)
        comp.set_editor_property("relative_scale3d", unreal.Vector(0.22,0.22,0.22))
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        comp.set_editor_property("cast_shadow", False)
        R["steps"].append("minimapa_add fail='%s'"%str(fail))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    R["steps"].append("saved")
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/minimapa.json","w").write(json.dumps(R))
