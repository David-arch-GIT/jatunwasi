# 208_faroles_caminos.py - faroles emisivos a lo largo de los 3 caminos (vida + luz, sin luces reales)
import unreal, json, math, re, traceback
R={"faroles":0,"err":[]}
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
    cyl=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cylinder")
    sph=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Sphere")
    dark=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Dark_Wood")
    glow=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/M_JW_NarrationMarker")
    # recoger waypoints
    wps={"HC":[], "CV":[], "TM":[]}
    for a in eas.get_all_level_actors():
        m=re.match(r"PATH_(HC|CV|TM)_nav_(\d+)$", a.get_actor_label())
        if m:
            loc=a.get_actor_location(); wps[m.group(1)].append((int(m.group(2)),loc.x,loc.y))
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("Farol_"): eas.destroy_actor(a)
    i=0
    for route,pts in wps.items():
        pts=sorted(pts)
        # farol en waypoints alternos (no saturar)
        for idx,(wi,x,y) in enumerate(pts):
            if idx%1!=0: continue
            # desplazar el farol al borde del camino (~250cm lateral) alternando lado
            side=300.0 if idx%2==0 else -300.0
            if idx+1<len(pts):
                nx,ny=pts[idx+1][1],pts[idx+1][2]
                ang=math.atan2(ny-y,nx-x)
            else:
                ang=0
            px=x+math.cos(ang+math.pi/2)*side; py=y+math.sin(ang+math.pi/2)*side
            fz=gz(w,px,py)
            post=eas.spawn_actor_from_object(cyl, unreal.Vector(px,py,fz+120), unreal.Rotator(0,0,0))
            if not post: continue
            post.set_actor_label("Farol_%s_%d_post"%(route,i))
            post.set_actor_scale3d(unreal.Vector(0.07,0.07,2.4))
            pm=post.get_component_by_class(unreal.StaticMeshComponent)
            if dark: pm.set_material(0,dark)
            pm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); pm.set_editor_property("cast_shadow",False)
            lamp=eas.spawn_actor_from_object(sph, unreal.Vector(px,py,fz+245), unreal.Rotator(0,0,0))
            lamp.set_actor_label("Farol_%s_%d_luz"%(route,i))
            lamp.set_actor_scale3d(unreal.Vector(0.22,0.22,0.28))
            lm=lamp.get_component_by_class(unreal.StaticMeshComponent)
            if glow: lm.set_material(0,glow)
            lm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); lm.set_editor_property("cast_shadow",False)
            lm.set_editor_property("ld_max_draw_distance", 9000.0)
            R["faroles"]+=1; i+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/faroles.json","w").write(json.dumps(R))
