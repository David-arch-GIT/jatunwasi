import unreal, json, math
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/coc1_diag.json"
eas=unreal.EditorActorSubsystem()
res={}
fa=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="MUS_Cuadro_coc1": fa=a; break
loc=fa.get_actor_location(); rot=fa.get_actor_rotation()
o,e=fa.get_actor_bounds(False)
res["actor_loc"]=[round(loc.x,1),round(loc.y,1),round(loc.z,1)]
res["actor_yaw"]=round(rot.yaw,1)
res["bounds_origin"]=[round(o.x,1),round(o.y,1),round(o.z,1)]
res["bounds_ext"]=[round(e.x,1),round(e.y,1),round(e.z,1)]
open(OUT,"w").write(json.dumps(res,indent=1))
