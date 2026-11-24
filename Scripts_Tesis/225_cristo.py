# 225_cristo.py - silueta del Cristo de la Concordia lejos en el horizonte (toque Cochabamba)
import unreal, json, math, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # importar textura
    t=unreal.AssetImportTask()
    t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cristo/T_Cristo.png")
    t.set_editor_property("destination_path","/Game/JWN/Env"); t.set_editor_property("destination_name","T_Cristo")
    t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
    AT.import_asset_tasks([t])
    tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Env/T_Cristo")
    try: tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
    except Exception: pass
    # material unlit, masked, emisivo tenue, two-sided
    mp="/Game/JWN/Env/M_Cristo"
    if not unreal.EditorAssetLibrary.does_asset_exist(mp):
        mat=AT.create_asset("M_Cristo","/Game/JWN/Env",unreal.Material,unreal.MaterialFactoryNew())
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-400,0); ts.set_editor_property("texture",tex)
        mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-150,0); mul.set_editor_property("const_b",0.7)
        mel.connect_material_expressions(ts,"RGB",mul,"A")
        mel.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY_MASK)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_MASKED)
        mat.set_editor_property("two_sided",True)
        mel.recompile_material(mat); unreal.EditorAssetLibrary.save_asset(mp)
    R["steps"].append("mat")
    plano=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    plaza=unreal.Vector(0,-1000,170)
    pos=unreal.Vector(9000.0,-7000.0,1600.0)
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=="ENV_Cristo": eas.destroy_actor(a)
    # mira a la plaza
    n=unreal.Vector(plaza.x-pos.x, plaza.y-pos.y, 0.0)
    nl=math.hypot(n.x,n.y); n=unreal.Vector(n.x/nl,n.y/nl,0.0)
    rot=unreal.MathLibrary.make_rot_from_zy(n, unreal.Vector(0,0,1))
    act=eas.spawn_actor_from_object(plano, pos, rot)
    act.set_actor_label("ENV_Cristo")
    act.set_actor_scale3d(unreal.Vector(26.0,26.0,1.0))
    smc=act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, unreal.EditorAssetLibrary.load_asset(mp))
    smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    smc.set_editor_property("cast_shadow",False)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # capturar desde la plaza mirando al Cristo
    cam=plaza
    rotc=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(pos.x,pos.y,pos.z-200))
    rt=unreal.RenderingLibrary.create_render_target2d(w,1200,700,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rotc)
    cc=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt); cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("fov_angle", 60.0)
    pp=cc.get_editor_property("post_process_settings")
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL); pp.set_editor_property("auto_exposure_bias", 11.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "cristo_vista.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cristo.json","w").write(json.dumps(R))
