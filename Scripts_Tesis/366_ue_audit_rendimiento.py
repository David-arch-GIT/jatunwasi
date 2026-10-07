import unreal, json, traceback
res={}
try:
    eas=unreal.EditorActorSubsystem()
    w=unreal.EditorLevelLibrary.get_editor_world()
    # LUCES
    lights={"PointLight":{"total":0,"Static":0,"Stationary":0,"Movable":0,"shadow":0},
            "SpotLight":{"total":0,"Static":0,"Stationary":0,"Movable":0,"shadow":0},
            "RectLight":{"total":0,"Static":0,"Stationary":0,"Movable":0,"shadow":0},
            "DirectionalLight":{"total":0,"shadow":0}}
    mobmap={0:"Static",1:"Stationary",2:"Movable"}
    for a in eas.get_all_level_actors():
        cn=a.get_class().get_name()
        if cn in ("PointLight","SpotLight","RectLight","DirectionalLight"):
            lights.setdefault(cn,{"total":0,"shadow":0})
            lights[cn]["total"]+=1
            comp=None
            for c in a.get_components_by_class(unreal.LightComponent):
                comp=c; break
            if comp:
                try:
                    mob=comp.get_editor_property("mobility")
                    mn=mobmap.get(int(mob),"?")
                    if mn in lights[cn]: lights[cn][mn]=lights[cn].get(mn,0)+1
                except: pass
                try:
                    if comp.get_editor_property("cast_shadows"): lights[cn]["shadow"]+=1
                except: pass
    res["luces"]=lights
    # INSTANCIAS + actores
    hism=0;ism_tot=0;sma=0
    for a in eas.get_all_level_actors():
        if a.get_class().get_name()=="StaticMeshActor": sma+=1
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try: ism_tot+=c.get_instance_count()
            except: pass
    res["StaticMeshActors"]=sma
    res["instancias_ISM_total"]=ism_tot
    # NAV re-check
    def fp(a,b):
        p=unreal.NavigationSystemV1.find_path_to_location_synchronously(w, unreal.Vector(a[0],a[1],a[2]), unreal.Vector(b[0],b[1],b[2]))
        if not p: return "no"
        try: return ("OK" if (p.is_valid() and not p.is_partial()) else "PARCIAL")
        except: return "?"
    res["nav"]={
     "plaza-hac_entrada":fp([600,-950,30],[-7300,-995,20]),
     "hac_base-2piso":fp([-7085,-620,20],[-7590,-2300,447]),
     "conv_zaguan-norte":fp([6300,3550,20],[6300,6800,20]),
     "plaza-convento":fp([600,-950,30],[6300,4000,20]),
     "plaza-templo":fp([600,-950,30],[50,10355,20]),
    }
except Exception as e:
    res["err"]=traceback.format_exc()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/perf_audit.json","w").write(json.dumps(res,indent=1,default=str))
