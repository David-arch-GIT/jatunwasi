# 200_cartel_direcciones.py - poste de direcciones en la plaza hacia los 3 escenarios
import unreal, json, math, traceback
R={"placed":[], "err":[]}
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","PANEL","POSTE","MALEZA","RUTA","COL_","Cartel","Flecha"]
def groundz(w,x,y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-400),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return None
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    cyl=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    cube=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
    wood=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/BasicShapeMaterial")
    unlit=unreal.EditorAssetLibrary.load_asset("/Engine/EngineMaterials/UnlitText")
    P=unreal.Vector(350.0,-650.0,0.0)   # plaza, lado norte
    fz=groundz(w,P.x,P.y)
    if fz is None: fz=12.0
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith(("CartelDir_","FlechaDir_")): eas.destroy_actor(a)
    # poste
    post=unreal.EditorLevelLibrary.spawn_actor_from_object(cyl, unreal.Vector(P.x,P.y,fz+125), unreal.Rotator(0,0,0))
    post.set_actor_label("CartelDir_Poste")
    post.set_actor_scale3d(unreal.Vector(0.12,0.12,2.5))
    pm=post.get_component_by_class(unreal.StaticMeshComponent)
    if wood: pm.set_material(0, wood)
    pm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    pm.set_editor_property("cast_shadow", False)
    dests={"HACIENDA":(-7250.0,-820.0,245.0),"CONVENTO":(5950.0,4250.0,215.0),"TEMPLO":(50.0,9550.0,185.0)}
    for name,(dx,dy,zz) in dests.items():
        yaw=math.degrees(math.atan2(dy-P.y, dx-P.x))
        # tablero (apunta hacia el destino: eje +X local hacia alla)
        off=65.0
        bx=P.x+math.cos(math.radians(yaw))*off; by=P.y+math.sin(math.radians(yaw))*off
        board=unreal.EditorLevelLibrary.spawn_actor_from_object(cube, unreal.Vector(bx,by,fz+zz), unreal.Rotator(0.0,yaw,0.0))
        board.set_actor_label("FlechaDir_%s"%name)
        board.set_actor_scale3d(unreal.Vector(1.5,0.22,0.16))
        bm=board.get_component_by_class(unreal.StaticMeshComponent)
        if wood: bm.set_material(0, wood)
        bm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        bm.set_editor_property("cast_shadow", False)
        # texto: en la cara del tablero, mira hacia el destino (lees al caminar hacia alla)
        txt=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.TextRenderActor, unreal.Vector(bx,by,fz+zz+2), unreal.Rotator(0.0,yaw-90.0,0.0))
        txt.set_actor_label("CartelDir_Txt_%s"%name)
        trc=txt.get_component_by_class(unreal.TextRenderComponent)
        trc.set_text(unreal.Text(name+"  >>"))
        trc.set_world_size(26.0)
        trc.set_horizontal_alignment(unreal.HorizTextAligment.EHTA_CENTER)
        trc.set_vertical_alignment(unreal.VerticalTextAligment.EVRTA_TEXT_CENTER)
        trc.set_text_render_color(unreal.Color(255,246,210,255))
        if unlit: trc.set_text_material(unlit)
        trc.set_editor_property("cast_shadow", False)
        R["placed"].append({"name":name,"yaw":round(yaw)})
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["fz"]=round(fz); R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cartel_dir.json","w").write(json.dumps(R))
