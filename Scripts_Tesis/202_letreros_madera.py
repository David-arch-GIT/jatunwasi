# 202_letreros_madera.py - 3 letreros de MADERA separados, uno por camino, texto mirando al jugador
import unreal, json, math, traceback
R={"signs":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","MALEZA","RUTA","COL_","Letrero","Cartel","Flecha"]
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
    cyl=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    light=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Light_Wood")
    dark=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Dark_Wood")
    unlit=unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/UnlitText")
    # limpiar previos (poste amontonado + estos)
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith(("CartelDir_","FlechaDir_","Letrero_")): eas.destroy_actor(a)
    plaza=unreal.Vector(0.0,-1000.0,0.0)
    signs={
      "HACIENDA":{"pos":(-1150.0,-1000.0),"dest":(-7250.0,-820.0)},
      "CONVENTO":{"pos":(1250.0,-350.0),"dest":(5950.0,4250.0)},
      "TEMPLO":  {"pos":(0.0,150.0),    "dest":(50.0,9550.0)},
    }
    for name,d in signs.items():
        sx,sy=d["pos"]; dx,dy=d["dest"]
        fz=gz(w,sx,sy)
        board_yaw=math.degrees(math.atan2(dy-sy, dx-sx))         # tablero apunta al destino
        text_yaw=math.degrees(math.atan2(plaza.y-sy, plaza.x-sx))+90.0  # texto mira al jugador (plaza)
        # poste madera oscura
        post=eas.spawn_actor_from_object(cyl, unreal.Vector(sx,sy,fz+110), unreal.Rotator(0,0,0))
        post.set_actor_label("Letrero_%s_Poste"%name)
        post.set_actor_scale3d(unreal.Vector(0.09,0.09,2.2))
        pm=post.get_component_by_class(unreal.StaticMeshComponent)
        if dark: pm.set_material(0, dark)
        pm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); pm.set_editor_property("cast_shadow",False)
        # tablero madera clara, apunta al destino, montado adelante del poste
        off=70.0
        bx=sx+math.cos(math.radians(board_yaw))*off; by=sy+math.sin(math.radians(board_yaw))*off
        board=eas.spawn_actor_from_object(cube, unreal.Vector(bx,by,fz+185), unreal.Rotator(0.0,board_yaw,0.0))
        board.set_actor_label("Letrero_%s_Tabla"%name)
        board.set_actor_scale3d(unreal.Vector(1.7,0.12,0.30))
        bm=board.get_component_by_class(unreal.StaticMeshComponent)
        if light: bm.set_material(0, light)
        bm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); bm.set_editor_property("cast_shadow",False)
        # texto mirando al jugador, delante del tablero
        tx=sx+math.cos(math.radians(board_yaw))*(off+2); ty=sy+math.sin(math.radians(board_yaw))*(off+2)
        txt=eas.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(sx,sy,fz+185), unreal.Rotator(0.0,text_yaw,0.0))
        txt.set_actor_label("Letrero_%s_Txt"%name)
        trc=txt.get_component_by_class(unreal.TextRenderComponent)
        trc.set_text(unreal.Text(name))
        trc.set_world_size(34.0)
        trc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        trc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        trc.set_text_render_color(unreal.Color(255,248,225,255))
        if unlit: trc.set_text_material(unlit)
        trc.set_editor_property("cast_shadow",False)
        R["signs"].append({"name":name,"fz":round(fz),"board_yaw":round(board_yaw),"text_yaw":round(text_yaw)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/letreros.json","w").write(json.dumps(R))
