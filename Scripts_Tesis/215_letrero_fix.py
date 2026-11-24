# 215_letrero_fix.py - madera visible de noche (emisiva suave) + un solo texto (sin encimar)
import unreal, json, traceback
R={"steps":[],"err":[]}
try:
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    mel=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # 1) material madera visible de noche (unlit emisivo calido suave)
    mp="/Game/JWN/Letreros/M_JW_SignWood"
    if not unreal.EditorAssetLibrary.does_asset_exist(mp):
        mat=AT.create_asset("M_JW_SignWood","/Game/JWN/Letreros",unreal.Material,unreal.MaterialFactoryNew())
        c=mel.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-300,0)
        c.set_editor_property("constant",unreal.LinearColor(0.28,0.17,0.08,1.0))
        mel.connect_material_property(c,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
        mel.recompile_material(mat)
        unreal.EditorAssetLibrary.save_asset(mp)
    R["steps"].append("mat_ok")
    wood=unreal.EditorAssetLibrary.load_asset(mp)
    # 2) asignar madera visible a los letreros
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("LetreroM_"):
            smc=a.get_component_by_class(unreal.StaticMeshComponent)
            for i in range(smc.get_num_materials()):
                smc.set_material(i, wood)
    R["steps"].append("wood_assigned")
    # 3) quitar el texto de ATRAS (deja solo el que mira a la plaza)
    rem=0
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("LetreroTxt_") and a.get_actor_label().endswith("_B"):
            eas.destroy_actor(a); rem+=1
    R["steps"].append("back_removed:%d"%rem)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # capturar templo
    cam=unreal.Vector(0.0,-360.0,250.0); look=unreal.Vector(0.0,150.0,210.0)
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
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "letrero_ok.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/letrero_fix.json","w").write(json.dumps(R))
