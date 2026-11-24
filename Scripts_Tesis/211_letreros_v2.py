# 211_letreros_v2.py - letreros de madera DECENTES por camino: poste + tabla + texto DOBLE CARA (sin espejo)
import unreal, json, math, traceback
R={"signs":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","Letrero","MALEZA","RUTA","COL_","Farol"]
def gz(w,x,y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-400),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return 12.0
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    light=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Light_Wood")
    dark=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Dark_Wood")
    unlit=unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/UnlitText")
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("Letrero_"): eas.destroy_actor(a)
    plaza=(0.0,-1000.0)
    signs={"HACIENDA":(-1150.0,-1000.0),"CONVENTO":(1250.0,-350.0),"TEMPLO":(0.0,150.0)}
    for name,(sx,sy) in signs.items():
        fz=gz(w,sx,sy)
        P=math.degrees(math.atan2(plaza[1]-sy, plaza[0]-sx))  # dir sign->plaza
        Prad=math.radians(P)
        # POSTE madera oscura (viga cuadrada)
        post=eas.spawn_actor_from_object(cube, unreal.Vector(sx,sy,fz+115), unreal.Rotator(0,0,0))
        post.set_actor_label("Letrero_%s_poste"%name)
        post.set_actor_scale3d(unreal.Vector(0.13,0.13,2.3))
        pm=post.get_component_by_class(unreal.StaticMeshComponent)
        if dark: pm.set_material(0,dark)
        pm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); pm.set_editor_property("cast_shadow",False)
        # TABLA madera clara, cara ancha hacia el camino (±P), centrada en el poste
        board=eas.spawn_actor_from_object(cube, unreal.Vector(sx,sy,fz+200), unreal.Rotator(0.0,P,0.0))
        board.set_actor_label("Letrero_%s_tabla"%name)
        board.set_actor_scale3d(unreal.Vector(0.12,2.0,0.44))  # grosor, ancho, alto
        bm=board.get_component_by_class(unreal.StaticMeshComponent)
        if light: bm.set_material(0,light)
        bm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); bm.set_editor_property("cast_shadow",False)
        # TEXTO doble cara
        for s,tag,tyaw in [(1,"A",P+90.0),(-1,"B",P+90.0+180.0)]:
            tx=sx+math.cos(Prad)*8.0*s; ty=sy+math.sin(Prad)*8.0*s
            txt=eas.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(tx,ty,fz+200), unreal.Rotator(0.0,tyaw,0.0))
            txt.set_actor_label("Letrero_%s_txt%s"%(name,tag))
            trc=txt.get_component_by_class(unreal.TextRenderComponent)
            trc.set_text(unreal.Text(name))
            trc.set_world_size(38.0)
            trc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
            trc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
            trc.set_text_render_color(unreal.Color(40,24,10,255))  # texto oscuro tallado sobre madera clara
            trc.set_editor_property("cast_shadow",False)
        R["signs"].append({"name":name,"P":round(P),"fz":round(fz)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/letreros2.json","w").write(json.dumps(R))
