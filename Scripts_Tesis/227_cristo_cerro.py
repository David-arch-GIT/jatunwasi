import unreal, json, math, traceback
R={"steps":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools(); mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    t=unreal.AssetImportTask()
    t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cristo/T_CristoCerro.png")
    t.set_editor_property("destination_path","/Game/JWN/Env"); t.set_editor_property("destination_name","T_CristoCerro")
    t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
    AT.import_asset_tasks([t])
    tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Env/T_CristoCerro")
    try: tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
    except Exception: pass
    mp="/Game/JWN/Env/M_CristoCerro"
    if unreal.EditorAssetLibrary.does_asset_exist(mp): unreal.EditorAssetLibrary.delete_asset(mp)
    mat=AT.create_asset("M_CristoCerro","/Game/JWN/Env",unreal.Material,unreal.MaterialFactoryNew())
    ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0); ts.set_editor_property("texture",tex)
    mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-150,0); mul.set_editor_property("const_b",1.6)
    mel.connect_material_expressions(ts,"RGB",mul,"A")
    mel.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY_MASK)
    mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_MASKED); mat.set_editor_property("two_sided",True)
    mel.recompile_material(mat); unreal.EditorAssetLibrary.save_asset(mp)
    cr=None
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="ENV_Cristo": cr=a; break
    plaza=unreal.Vector(0,-1000,170); pos=unreal.Vector(7000.0,-5800.0,2050.0)
    n=unreal.Vector(plaza.x-pos.x, plaza.y-pos.y,0.0); nl=math.hypot(n.x,n.y); n=unreal.Vector(n.x/nl,n.y/nl,0.0)
    cr.set_actor_location(pos,False,True)
    cr.set_actor_rotation(unreal.MathLibrary.make_rot_from_zy(n, unreal.Vector(0,0,1)),False)
    cr.set_actor_scale3d(unreal.Vector(74.0,46.0,1.0))
    cr.get_component_by_class(unreal.StaticMeshComponent).set_material(0, mat)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    cam=plaza; rotc=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(pos.x,pos.y,pos.z+300))
    rt=unreal.RenderingLibrary.create_render_target2d(w,1200,750,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rotc)
    cc=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt); cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR); cc.set_editor_property("fov_angle",55.0)
    pp=cc.get_editor_property("post_process_settings"); pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL); pp.set_editor_property("auto_exposure_bias",11.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "cristo_cerro.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cc.json","w").write(json.dumps(R))
