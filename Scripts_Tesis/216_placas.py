# 216_placas.py - placa de madera (textura) auto-iluminada en cada letrero, quita letras flotantes
import unreal, json, math, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    plano=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    plaza=(0.0,-1000.0)
    data={"HACIENDA":(-1150.0,-1000.0),"CONVENTO":(1250.0,-350.0),"TEMPLO":(0.0,150.0)}
    # 1) importar texturas
    for nm in data:
        t=unreal.AssetImportTask()
        t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/signtex/sign_%s.png"%nm)
        t.set_editor_property("destination_path","/Game/JWN/Letreros/Tex")
        t.set_editor_property("destination_name","T_Sign_%s"%nm)
        t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
        AT.import_asset_tasks([t])
    R["steps"].append("tex_imported")
    # 2) material por placa (unlit, emissive = tex * 1.5, opaco)
    def mkmat(nm):
        mp="/Game/JWN/Letreros/M_Sign_%s"%nm
        tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Letreros/Tex/T_Sign_%s"%nm)
        if unreal.EditorAssetLibrary.does_asset_exist(mp):
            return unreal.EditorAssetLibrary.load_asset(mp)
        mat=AT.create_asset("M_Sign_%s"%nm,"/Game/JWN/Letreros",unreal.Material,unreal.MaterialFactoryNew())
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,0)
        ts.set_editor_property("texture",tex)
        mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-200,0)
        mul.set_editor_property("const_b",1.5)
        mel.connect_material_expressions(ts,"RGB",mul,"A")
        mel.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(mp)
        return mat
    # 3) quitar letras flotantes
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("LetreroTxt_") or a.get_actor_label().startswith("LetreroPlaca_"):
            eas.destroy_actor(a)
    # 4) placa (plano) en la cara de cada letrero, mirando a la plaza
    for nm,(sx,sy) in data.items():
        act=None
        for a in eas.get_all_level_actors():
            if a.get_actor_label()=="LetreroM_%s"%nm: act=a; break
        az=act.get_actor_location().z if act else 12.0
        bz=az+200.0
        P=math.degrees(math.atan2(plaza[1]-sy, plaza[0]-sx)); Pr=math.radians(P)
        n=unreal.Vector(math.cos(Pr),math.sin(Pr),0.0)
        rot=unreal.MathLibrary.make_rot_from_zy(n, unreal.Vector(0,0,-1))
        loc=unreal.Vector(sx+math.cos(Pr)*9.0, sy+math.sin(Pr)*9.0, bz)
        pl=unreal.EditorLevelLibrary.spawn_actor_from_object(plano, loc, rot)
        pl.set_actor_label("LetreroPlaca_%s"%nm)
        pl.set_actor_scale3d(unreal.Vector(1.9,0.63,1.0))
        smc=pl.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_material(0, mkmat(nm))
        smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        smc.set_editor_property("cast_shadow",False)
        R["steps"].append("placa_%s"%nm)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # capturar templo
    cam=unreal.Vector(0.0,-360.0,250.0); look=unreal.Vector(0.0,150.0,215.0)
    rot=unreal.MathLibrary.find_look_at_rotation(cam, look)
    rt=unreal.RenderingLibrary.create_render_target2d(w,1100,720,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    cc=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("fov_angle", 46.0)
    pp=cc.get_editor_property("post_process_settings")
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property("auto_exposure_bias", 11.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "placa_final.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/placas.json","w").write(json.dumps(R))
