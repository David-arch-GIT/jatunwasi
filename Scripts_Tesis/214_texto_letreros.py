# 214_texto_letreros.py - texto TextRender auto-iluminado (doble cara) sobre las tablas Blender
import unreal, json, math, traceback
R={"txt":0,"err":[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    unlit=unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/UnlitText")
    plaza=(0.0,-1000.0)
    data={"HACIENDA":(-1150.0,-1000.0),"CONVENTO":(1250.0,-350.0),"TEMPLO":(0.0,150.0)}
    # borrar textos previos
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("LetreroTxt_"): eas.destroy_actor(a)
    for nm,(sx,sy) in data.items():
        # z de la tabla = fz actor + 200. buscar actor
        act=None
        for a in eas.get_all_level_actors():
            if a.get_actor_label()=="LetreroM_%s"%nm: act=a; break
        if not act: R["err"].append("noact_"+nm); continue
        az=act.get_actor_location().z
        bz=az+200.0
        P=math.degrees(math.atan2(plaza[1]-sy, plaza[0]-sx)); Pr=math.radians(P)
        for s,tag,tyaw in [(1,"A",P+90.0),(-1,"B",P+90.0+180.0)]:
            tx=sx+math.cos(Pr)*9.0*s; ty=sy+math.sin(Pr)*9.0*s
            t=eas.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(tx,ty,bz), unreal.Rotator(0.0,tyaw,0.0))
            t.set_actor_label("LetreroTxt_%s_%s"%(nm,tag))
            trc=t.get_component_by_class(unreal.TextRenderComponent)
            trc.set_text(unreal.Text(nm))
            trc.set_world_size(34.0)
            trc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            trc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
            trc.set_text_render_color(unreal.Color(255,244,214,255))
            if unlit: trc.set_text_material(unlit)
            trc.set_editor_property("cast_shadow",False)
            R["txt"]+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # capturar templo
    cam=unreal.Vector(0.0,-380.0,250.0); look=unreal.Vector(0.0,150.0,210.0)
    rot=unreal.MathLibrary.find_look_at_rotation(cam, look)
    rt=unreal.RenderingLibrary.create_render_target2d(w,1100,720,unreal.TextureRenderTargetFormat.RTF_RGBA8)
    cap=eas.spawn_actor_from_class(unreal.SceneCapture2D, cam, rot)
    cc=cap.get_component_by_class(unreal.SceneCaptureComponent2D)
    cc.set_editor_property("texture_target", rt)
    cc.set_editor_property("capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    cc.set_editor_property("fov_angle", 48.0)
    pp=cc.get_editor_property("post_process_settings")
    pp.set_editor_property("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property("auto_exposure_bias", 11.0)
    cc.set_editor_property("post_process_settings", pp)
    cc.capture_scene()
    unreal.RenderingLibrary.export_render_target(w, rt, "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups", "letrero_final.png")
    eas.destroy_actor(cap)
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/txt_letreros.json","w").write(json.dumps(R))
