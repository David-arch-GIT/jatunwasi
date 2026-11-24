# 217_flechas.py - placas-flecha de madera, doble cara (masked), apuntando al destino real
import unreal, json, math, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    plano=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    # sign pos + DESTINO real (para apuntar)
    data={
     "HACIENDA":{"pos":(-1150.0,-1000.0),"dest":(-7250.0,-820.0)},
     "CONVENTO":{"pos":(1250.0,-350.0),"dest":(5950.0,4250.0)},
     "TEMPLO":  {"pos":(0.0,150.0),    "dest":(50.0,9550.0)},
    }
    # reimportar texturas flecha (con alfa)
    for nm in data:
        t=unreal.AssetImportTask()
        t.set_editor_property("filename","C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/signtex/sign_%s.png"%nm)
        t.set_editor_property("destination_path","/Game/JWN/Letreros/Tex")
        t.set_editor_property("destination_name","T_Sign_%s"%nm)
        t.set_editor_property("automated",True); t.set_editor_property("replace_existing",True); t.set_editor_property("save",True)
        AT.import_asset_tasks([t])
        tx=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Letreros/Tex/T_Sign_%s"%nm)
        if tx:
            try: tx.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT)
            except Exception: pass
    R["steps"].append("tex")
    def mkmat(nm):
        mp="/Game/JWN/Letreros/M_SignA_%s"%nm
        tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Letreros/Tex/T_Sign_%s"%nm)
        if unreal.EditorAssetLibrary.does_asset_exist(mp): return unreal.EditorAssetLibrary.load_asset(mp)
        mat=AT.create_asset("M_SignA_%s"%nm,"/Game/JWN/Letreros",unreal.Material,unreal.MaterialFactoryNew())
        ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,0)
        ts.set_editor_property("texture",tex)
        mul=mel.create_material_expression(mat,unreal.MaterialExpressionMultiply,-200,0)
        mul.set_editor_property("const_b",1.5)
        mel.connect_material_expressions(ts,"RGB",mul,"A")
        mel.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY_MASK)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_MASKED)
        mat.set_editor_property("two_sided",True)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(mp)
        return mat
    # quitar placas/letras viejas
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("LetreroPlaca_") or a.get_actor_label().startswith("LetreroTxt_"):
            eas.destroy_actor(a)
    for nm,d in data.items():
        sx,sy=d["pos"]; dx,dy=d["dest"]
        act=None
        for a in eas.get_all_level_actors():
            if a.get_actor_label()=="LetreroM_%s"%nm: act=a; break
        az=act.get_actor_location().z if act else 12.0
        bz=az+205.0
        D=math.atan2(dy-sy, dx-sx)
        Dv=unreal.Vector(math.cos(D),math.sin(D),0.0)
        rot=unreal.MathLibrary.make_rot_from_xy(Dv, unreal.Vector(0,0,1))
        pl=unreal.EditorLevelLibrary.spawn_actor_from_object(plano, unreal.Vector(sx,sy,bz), rot)
        pl.set_actor_label("LetreroPlaca_%s"%nm)
        pl.set_actor_scale3d(unreal.Vector(2.4,0.75,1.0))
        smc=pl.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_material(0, mkmat(nm))
        smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        smc.set_editor_property("cast_shadow",False)
        R["steps"].append("flecha_%s D=%d"%(nm,math.degrees(D)))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # capturar templo desde la plaza
    cam=unreal.Vector(-330.0,-250.0,250.0); look=unreal.Vector(0.0,150.0,215.0)
    rot=unreal.MathLibrary.find_look_at_rotation(cam, look)
    rt=unreal.RenderingLibrary.create_render_target2d(w,1100,720,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    cc=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("fov_angle", 55.0)
    pp=cc.get_editor_property("post_process_settings")
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property("auto_exposure_bias", 11.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "flecha_final.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/flechas.json","w").write(json.dumps(R))
