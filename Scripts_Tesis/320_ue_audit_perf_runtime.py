# Auditoria de costo en runtime (anti-cuelgue): luces por movilidad, ticks activos, particulas.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_runtime.json"
res={"luces":{"Static":0,"Stationary":0,"Movable":0}, "luces_dyn_detalle":[],
     "tick_actores":0, "tick_detalle":[], "particulas":0, "skeletals":0, "total_actores":0}
eas=unreal.EditorActorSubsystem()
acts=eas.get_all_level_actors()
res["total_actores"]=len(acts)
MOB={0:"Static",1:"Stationary",2:"Movable"}
for a in acts:
    # luces
    for lc in a.get_components_by_class(unreal.LightComponent):
        try:
            mob=lc.get_editor_property("mobility")
            key=MOB.get(int(mob),"?")
            res["luces"][key]=res["luces"].get(key,0)+1
            if key in ("Stationary","Movable"):
                cast=lc.get_editor_property("cast_shadows")
                res["luces_dyn_detalle"].append({"actor":a.get_actor_label()[:40],"tipo":lc.get_class().get_name(),"mov":key,"sombra":bool(cast)})
        except Exception: pass
    # skeletals
    if a.get_components_by_class(unreal.SkeletalMeshComponent):
        res["skeletals"]+=1
    # particulas
    if a.get_components_by_class(unreal.ParticleSystemComponent):
        res["particulas"]+=1
    try:
        import unreal as u
        if a.get_components_by_class(u.NiagaraComponent):
            res["particulas"]+=1
    except Exception: pass
    # tick a nivel actor
    try:
        if a.get_editor_property("primary_actor_tick").get_editor_property("start_with_tick_enabled") and a.get_editor_property("primary_actor_tick").get_editor_property("can_ever_tick"):
            res["tick_actores"]+=1
            if len(res["tick_detalle"])<25:
                res["tick_detalle"].append(a.get_actor_label()[:40]+" ["+a.get_class().get_name()+"]")
    except Exception: pass
open(OUT,"w").write(json.dumps(res,indent=1))
