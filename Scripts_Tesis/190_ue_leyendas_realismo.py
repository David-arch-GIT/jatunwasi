# 190_ue_leyendas_realismo.py
# Realismo de leyendas: (1) aterrizar (no flotar), (2) confinar nav (no vagar como NPC),
# (3) maleza en la base (arbustos/helechos/pasto) para que emerjan de la vegetacion.
import unreal, json, math, random, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={"grounded":[],"nav":[],"maleza":0,"err":[]}
random.seed(7)
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
    EXCL=["PCG_","Vol","Trig","Narr","Cria","Nav","Snd","App","RELATO","PANEL","POSTE","MALEZA"]
    def groundz(x,y):
        hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,2000),unreal.Vector(x,y,-600),WS,True,[],unreal.DrawDebugTrace.NONE,True)
        if hrs:
            for hr in hrs:
                t=hr.to_tuple(); z=t[5].z; n=(t[9].get_actor_label() if t[9] else "?")
                if any(k in n for k in EXCL): continue
                return z
        return None
    def actor(lbl):
        for a in eas.get_all_level_actors():
            if a.get_actor_label()==lbl: return a
        return None
    # 0) restaurar duende de plaza (billboard viejo, pivote raro) a su Z original
    apz=actor("App_Plz_Duende")
    if apz:
        l=apz.get_actor_location(); apz.set_actor_location(unreal.Vector(l.x,l.y,103.0), False, True)
    # 1) aterrizar SOLO las criaturas 3D (bounds fiables)
    for lbl in ["Cria_Karisiri","Cria_Condenado","Cria_Duende"]:
        a=actor(lbl)
        if not a: R["err"].append("no_"+lbl); continue
        loc=a.get_actor_location()
        org,ext=a.get_actor_bounds(False)
        bottom=org.z-ext.z
        gz=groundz(loc.x,loc.y)
        if gz is None: R["err"].append("noground_"+lbl); continue
        target_bottom=gz-12.0  # pies ligeramente hundidos en el pasto
        dz=bottom-target_bottom
        a.set_actor_location(unreal.Vector(loc.x,loc.y,loc.z-dz), False, True)
        R["grounded"].append({"lbl":lbl,"gz":round(gz),"dz":round(dz),"newZ":round(loc.z-dz)})
    # 2) confinar nav (encoger volumenes de criatura)
    for lbl in ["Nav_Cria_Karisiri","Nav_Cria_Condenado","Nav_Cria_Duende"]:
        a=actor(lbl)
        if a:
            a.set_actor_scale3d(unreal.Vector(0.03,0.03,0.08))
            R["nav"].append(lbl)
    # 3) maleza
    bush=["/Game/StylescapeHD/Foliage/Forest/SM_ForestBush_01","/Game/StylescapeHD/Foliage/Forest/SM_ForestBush_02"]
    grass=["/Game/StylescapeHD/Foliage/Forest/SM_GrassForest_01","/Game/StylescapeHD/Foliage/Forest/SM_GrassForest_02"]
    fern=["/Game/StylescapeHD/Foliage/Alpine/SM_Fern_01","/Game/StylescapeHD/Foliage/Alpine/SM_Fern_02"]
    meshes={}
    for p in bush+grass+fern:
        meshes[p]=unreal.EditorAssetLibrary.load_asset(p)
    # borrar maleza previa
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label().startswith("MALEZA_"): eas.destroy_actor(a)
    def place(mesh_path, x, y, sc, label):
        m=meshes.get(mesh_path)
        if not m: return False
        gz=groundz(x,y)
        if gz is None: gz=-5.0
        act=unreal.EditorLevelLibrary.spawn_actor_from_object(m, unreal.Vector(x,y,gz-5.0), unreal.Rotator(0,random.uniform(0,360),0))
        act.set_actor_label(label)
        act.set_actor_scale3d(unreal.Vector(sc,sc,sc*random.uniform(0.9,1.15)))
        smc=act.get_component_by_class(unreal.StaticMeshComponent)
        smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        smc.set_editor_property("cast_shadow", False)
        smc.set_editor_property("can_ever_affect_navigation", False)
        try: a_cull=smc.set_editor_property("ld_max_draw_distance", 7000.0)
        except Exception: pass
        return True
    i=0
    for lbl in ["Cria_Karisiri","Cria_Condenado","Cria_Duende","App_Plz_Duende"]:
        a=actor(lbl)
        if not a: continue
        loc=a.get_actor_location()
        # anillo de maleza: arbustos grandes al frente/lados cubriendo pies, helechos/pasto delante
        ring=[(bush[0],70,1.15),(bush[1],85,1.05),(bush[0],95,1.1),
              (fern[0],55,0.9),(fern[1],65,0.95),
              (grass[0],45,0.8),(grass[1],50,0.85),(grass[0],75,0.75)]
        for mp,rad,sc in ring:
            ang=random.uniform(0,360); jr=rad+random.uniform(-12,12)
            x=loc.x+math.cos(math.radians(ang))*jr; y=loc.y+math.sin(math.radians(ang))*jr
            if place(mp,x,y,sc,"MALEZA_%s_%d"%(lbl,i)): R["maleza"]+=1
            i+=1
    unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open(out+"/leyendas.json","w").write(json.dumps(R))
