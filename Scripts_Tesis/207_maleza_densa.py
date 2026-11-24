# 207_maleza_densa.py - mas frondosidad alrededor de cada leyenda (densa, variada, aterrizada)
import unreal, json, math, random, traceback
R={"add":0,"err":[]}
random.seed(11)
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","Letrero","MALEZA","RUTA","COL_"]
def gz(w,x,y):
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
            if any(k in n for k in EXCL): continue
            return z
    return -5.0
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    palette=["/Game/StylescapeHD/Foliage/Forest/SM_ForestBush_01","/Game/StylescapeHD/Foliage/Forest/SM_ForestBush_02",
             "/Game/StylescapeHD/Foliage/Alpine/SM_Fern_01","/Game/StylescapeHD/Foliage/Alpine/SM_Fern_02",
             "/Game/StylescapeHD/Foliage/Forest/SM_GrassForest_01","/Game/StylescapeHD/Foliage/Forest/SM_GrassForest_02"]
    meshes={p:unreal.EditorAssetLibrary.load_asset(p) for p in palette}
    loaded={k:(v is not None) for k,v in meshes.items()}
    R["loaded"]=sum(1 for v in loaded.values() if v)
    cria={}
    for x in eas.get_all_level_actors():
        l=x.get_actor_label()
        if l in ("Cria_Karisiri","Cria_Condenado","Cria_Duende"): cria[l]=x.get_actor_location()
    i=0
    for lbl,loc in cria.items():
        # anillo denso: arbustos grandes detras/lados, helechos/pasto delante
        ring=[]
        # arbustos grandes alrededor (parcialmente ocultan, frondoso)
        for a in range(8):
            ring.append((palette[a%2], random.uniform(90,160), random.uniform(1.1,1.7)))
        # helechos medianos
        for a in range(6):
            ring.append((palette[2+a%2], random.uniform(55,110), random.uniform(0.9,1.3)))
        # pasto bajo al frente
        for a in range(6):
            ring.append((palette[4+a%2], random.uniform(40,90), random.uniform(0.7,1.1)))
        for mp,rad,scl in ring:
            m=meshes.get(mp)
            if not m: continue
            ang=random.uniform(0,360)
            x=loc.x+math.cos(math.radians(ang))*rad; y=loc.y+math.sin(math.radians(ang))*rad
            fz=gz(w,x,y)
            act=eas.spawn_actor_from_object(m, unreal.Vector(x,y,fz-4.0), unreal.Rotator(0,random.uniform(0,360),0))
            if not act: continue
            act.set_actor_label("MALEZA2_%s_%d"%(lbl,i))
            act.set_actor_scale3d(unreal.Vector(scl,scl,scl*random.uniform(0.95,1.2)))
            sm=act.get_component_by_class(unreal.StaticMeshComponent)
            sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            sm.set_editor_property("cast_shadow", False)
            sm.set_editor_property("can_ever_affect_navigation", False)
            R["add"]+=1; i+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/maleza2.json","w").write(json.dumps(R))
