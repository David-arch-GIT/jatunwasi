# 218_flechas_2caras.py - flecha apunta al destino, 2 planos (frente normal + atras espejado) = texto correcto ambos lados
import unreal, json, math, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    plano=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    data={
     "HACIENDA":{"pos":(-1150.0,-1000.0),"dest":(-7250.0,-820.0)},
     "CONVENTO":{"pos":(1250.0,-350.0),"dest":(5950.0,4250.0)},
     "TEMPLO":  {"pos":(0.0,150.0),    "dest":(50.0,9550.0)},
    }
    def imp(nm,suf):
        t=unreal.AssetImportTask()
        t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/signtex/sign_%s%s.png"%(nm,suf))
        t.set_editor_property("destination_path","/Game/JWN/Letreros/Tex")
        t.set_editor_property("destination_name","T_Sign_%s%s"%(nm,suf.replace('_M','_M')))
        t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
        AT.import_asset_tasks([t])
    def mkmat(nm,suf):
        key=nm+suf.replace('_M','M')
        mp="/Game/JWN/Letreros/M_SignX_%s"%key
        tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Letreros/Tex/T_Sign_%s%s"%(nm,suf))
        if unreal.EditorAssetLibrary.does_asset_exist(mp): return unreal.EditorAssetLibrary.load_asset(mp)
        mat=AT.create_asset("M_SignX_%s"%key,"/Game/JWN/Letreros",unreal.Material,unreal.MaterialFactoryNew())
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,0); ts.set_editor_property("texture",tex)
        mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-200,0); mul.set_editor_property("const_b",1.5)
        mel.connect_material_expressions(ts,"RGB",mul,"A")
        mel.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY_MASK)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_MASKED)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(mp); return mat
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("LetreroPlaca_"): eas.destroy_actor(a)
    for nm,d in data.items():
        sx,sy=d["pos"]; dx,dy=d["dest"]
        imp(nm,""); imp(nm,"_M")
        act=None
        for a in eas.get_all_level_actors():
            if a.get_actor_label()=="LetreroM_%s"%nm: act=a; break
        bz=(act.get_actor_location().z if act else 12.0)+205.0
        D=math.atan2(dy-sy, dx-sx); Dv=unreal.Vector(math.cos(D),math.sin(D),0.0)
        rotF=unreal.MathLibrary.make_rot_from_xy(Dv, unreal.Vector(0,0,1))
        # FRENTE
        pf=unreal.EditorLevelLibrary.spawn_actor_from_object(plano, unreal.Vector(sx,sy,bz), rotF)
        pf.set_actor_label("LetreroPlaca_%s_F"%nm); pf.set_actor_scale3d(unreal.Vector(2.4,0.75,1.0))
        pf.get_component_by_class(unreal.StaticMeshComponent).set_material(0, mkmat(nm,""))
        pf.get_component_by_class(unreal.StaticMeshComponent).set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        pf.get_component_by_class(unreal.StaticMeshComponent).set_editor_property("cast_shadow",False)
        # ATRAS (gira 180 en up + textura espejada)
        rb=unreal.Rotator(rotF.pitch, rotF.yaw+180.0, rotF.roll)
        pb=unreal.EditorLevelLibrary.spawn_actor_from_object(plano, unreal.Vector(sx,sy,bz), rb)
        pb.set_actor_label("LetreroPlaca_%s_B"%nm); pb.set_actor_scale3d(unreal.Vector(2.4,0.75,1.0))
        pb.get_component_by_class(unreal.StaticMeshComponent).set_material(0, mkmat(nm,"_M"))
        pb.get_component_by_class(unreal.StaticMeshComponent).set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        pb.get_component_by_class(unreal.StaticMeshComponent).set_editor_property("cast_shadow",False)
        R["steps"].append("%s D=%d"%(nm,math.degrees(D)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # capturar templo desde el LADO (donde se lee al caminar): este del letrero
    cam=unreal.Vector(430.0,150.0,230.0); look=unreal.Vector(0.0,150.0,215.0)
    rot=unreal.MathLibrary.find_look_at_rotation(cam, look)
    rt=unreal.RenderingLibrary.create_render_target2d(w,1100,720,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    cc=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt); cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("fov_angle", 50.0)
    pp=cc.get_editor_property("post_process_settings")
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL); pp.set_editor_property("auto_exposure_bias", 11.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "flecha_2caras.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flechas2.json","w").write(json.dumps(R))
