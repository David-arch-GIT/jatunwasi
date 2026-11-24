# 194_diag_culling.py - diagnostica cull distances de HISM/ISM por zona (hacienda/convento)
import unreal, json, traceback
R={"hism":[], "err":[]}
def zone(x,y):
    if -8600<x<-5800 and -3600<y<-1500: return "HACIENDA"
    if 5000<x<7200 and 3200<y<5200: return "CONVENTO"
    if -800<x<800 and 8800<y<10400: return "TEMPLO"
    if -1600<x<1600 and -2000<y<200: return "PLAZA"
    return None
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                n=c.get_instance_count()
                if n==0: continue
                t=c.get_instance_transform(0, True)
                loc=t.translation if t else None
                z=zone(loc.x,loc.y) if loc else None
                if z not in ("HACIENDA","CONVENTO"): continue
                start=c.get_editor_property("instance_start_cull_distance")
                end=c.get_editor_property("instance_end_cull_distance")
                m=c.get_editor_property("static_mesh")
                R["hism"].append({"actor":a.get_actor_label(),"comp":c.get_name(),
                    "zone":z,"n":n,"start":start,"end":end,
                    "mesh":(m.get_name() if m else "?")})
            except Exception as e:
                R["err"].append(str(e)[:40])
    R["n"]=len(R["hism"]); R["ok"]=True
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-300:]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_diag.json","w").write(json.dumps(R))
