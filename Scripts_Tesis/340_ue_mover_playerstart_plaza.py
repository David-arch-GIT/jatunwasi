# Mueve el PlayerStart a la PLAZA (donde el NavMesh funciona) para que el jugador aparezca pudiendo moverse.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mover_ps.json"
res={}
eas=unreal.EditorActorSubsystem()
acts=eas.get_all_level_actors()
res["n_actores"]=len(acts)
if len(acts) < 400:
    res["estado"]="NIVEL AUN CARGANDO - no muevo"
    open(OUT,"w").write(json.dumps(res,indent=1)); raise SystemExit
world=unreal.EditorLevelLibrary.get_editor_world()
def V(x,y,z): return unreal.Vector(x,y,z)
def nav(x,y,z):
    try:
        loc=unreal.NavigationSystemV1.project_point_to_navigation(world, V(x,y,z), None, None, unreal.Vector(300,300,600))
        d=((loc.x-x)**2+(loc.y-y)**2+(loc.z-z)**2)**0.5
        return {"nav": (not(abs(loc.x)<0.1 and abs(loc.y)<0.1) and d<800), "proj":[round(loc.x),round(loc.y),round(loc.z)]}
    except Exception as e:
        return {"err":str(e)[:50]}
# navmesh comparativo
res["nav_plaza_600_-950"]=nav(600,-950,30)
res["nav_hacienda_-6200_-2500"]=nav(-6200,-2500,205)
# mover PlayerStart
ps=None
for a in acts:
    if a.get_class().get_name()=="PlayerStart":
        ps=a; break
if ps:
    res["ps_antes"]=[round(v) for v in [ps.get_actor_location().x, ps.get_actor_location().y, ps.get_actor_location().z]]
    ps.set_actor_location(unreal.Vector(600,-950,30), False, False)
    ps.set_actor_rotation(unreal.Rotator(0,0,180), False)  # yaw 180 mirando a la fuente
    res["ps_ahora"]=[round(v) for v in [ps.get_actor_location().x, ps.get_actor_location().y, ps.get_actor_location().z]]
    unreal.EditorLoadingAndSavingUtils.save_current_level()
    res["guardado"]=True
else:
    res["err"]="no PlayerStart"
open(OUT,"w").write(json.dumps(res,indent=1))
