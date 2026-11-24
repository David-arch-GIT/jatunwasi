# 209_maleza_estrategica.py - vegetacion DISCRETA: detras/lados enmarca, pasto bajo en pies, frente despejado
import unreal, json, math, random, traceback
R={"del":0,"add":0,"err":[]}
random.seed(5)
EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","Letrero","MALEZA","MALEZA2","RUTA","COL_","Farol"]
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
    bush=["/Game/StylescapeHD/Foliage/Forest/SM_ForestBush_01","/Game/StylescapeHD/Foliage/Forest/SM_ForestBush_02"]
    fern=["/Game/StylescapeHD/Foliage/Alpine/SM_Fern_01","/Game/StylescapeHD/Foliage/Alpine/SM_Fern_02"]
    grass=["/Game/StylescapeHD/Foliage/Forest/SM_GrassForest_01","/Game/StylescapeHD/Foliage/Forest/SM_GrassForest_02"]
    M={p:unreal.EditorAssetLibrary.load_asset(p) for p in bush+fern+grass}
    # borrar TODA maleza previa
    for a in list(eas.get_all_level_actors()):
        l=a.get_actor_label()
        if l.startswith("MALEZA_") or l.startswith("MALEZA2_"):
            eas.destroy_actor(a); R["del"]+=1
    cria={}
    for x in eas.get_all_level_actors():
        l=x.get_actor_label()
        if l in ("Cria_Karisiri","Cria_Condenado","Cria_Duende"):
            cria[l]=(x.get_actor_location(), x.get_actor_rotation().yaw)
    i=0
    def place(mp,x,y,scl,lbl):
        m=M.get(mp)
        if not m: return False
        fz=gz(w,x,y)
        act=eas.spawn_actor_from_object(m, unreal.Vector(x,y,fz-4.0), unreal.Rotator(0,random.uniform(0,360),0))
        if not act: return False
        act.set_actor_label(lbl)
        act.set_actor_scale3d(unreal.Vector(scl,scl,scl*random.uniform(0.95,1.1)))
        sm=act.get_component_by_class(unreal.StaticMeshComponent)
        sm.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        sm.set_editor_property("cast_shadow",False); sm.set_editor_property("can_ever_affect_navigation",False)
        return True
    for lbl,(loc,yaw) in cria.items():
        back=yaw+180.0  # detras de la figura (frente = yaw, despejado)
        # 3 arbustos medianos en arco TRASERO (enmarcan)
        for k,da in enumerate([-35,0,35]):
            ang=math.radians(back+da); rad=random.uniform(75,105)
            x=loc.x+math.cos(ang)*rad; y=loc.y+math.sin(ang)*rad
            if place(bush[k%2],x,y,random.uniform(1.0,1.25),"MALEZA_%s_%d"%(lbl,i)): R["add"]+=1
            i+=1
        # 2 helechos a los LADOS
        for da in [90,-90]:
            ang=math.radians(yaw+da); rad=random.uniform(70,95)
            x=loc.x+math.cos(ang)*rad; y=loc.y+math.sin(ang)*rad
            if place(fern[i%2],x,y,random.uniform(0.85,1.05),"MALEZA_%s_%d"%(lbl,i)): R["add"]+=1
            i+=1
        # 3 pasto BAJO cerca de los pies (cubre base, no el cuerpo)
        for k in range(3):
            ang=random.uniform(0,360); rad=random.uniform(25,45)
            x=loc.x+math.cos(ang)*rad; y=loc.y+math.sin(ang)*rad
            if place(grass[k%2],x,y,random.uniform(0.55,0.8),"MALEZA_%s_%d"%(lbl,i)): R["add"]+=1
            i+=1
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/maleza_estra.json","w").write(json.dumps(R))
