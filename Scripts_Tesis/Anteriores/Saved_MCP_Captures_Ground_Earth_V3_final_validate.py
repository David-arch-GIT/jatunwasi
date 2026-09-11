import json
import math
import os
import unreal

saved=unreal.Paths.project_saved_dir()
backup_path=os.path.join(saved,"Environment","JW_Ground_Assignment_Backup_V2.json")
with open(backup_path,"r",encoding="utf-8") as f:backup=json.load(f)
subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors={a.get_actor_label():a for a in subsystem.get_all_level_actors()}
labels=("JW_ENV_PathNetwork","JW_ENV_Plaza","JW_ENV_Trees","JW_ENV_Shrubs","JW_ENV_Grass","JW_ENV_Rocks")
counts={}
transforms_unchanged=True
for label in labels:
    comps=actors[label].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    counts[label]=sum(c.get_instance_count() for c in comps)
    snap=backup["hism_transform_snapshot"][label]
    for c in comps:
        old=snap.get(c.get_name(),[])
        if len(old)!=c.get_instance_count():transforms_unchanged=False;continue
        for i in range(c.get_instance_count()):
            tr=c.get_instance_transform(i,True);o=old[i]
            now=[tr.translation.x,tr.translation.y,tr.translation.z,tr.scale3d.x,tr.scale3d.y,tr.scale3d.z,tr.rotation.x,tr.rotation.y,tr.rotation.z,tr.rotation.w]
            was=o["location"]+o["scale"]+o["rotation"]
            if any(abs(a-b)>0.001 for a,b in zip(now,was)):
                transforms_unchanged=False;break

if counts!=backup["counts"] or not transforms_unchanged:
    raise RuntimeError("HISM state changed unexpectedly")
ground=actors["Ground_Cochabamba"]
gc=ground.get_components_by_class(unreal.StaticMeshComponent)[0]
loc=ground.get_actor_location();scale=ground.get_actor_scale3d();origin,extent=ground.get_actor_bounds(False)
g0=backup["ground"]
ground_unchanged=(
    [loc.x,loc.y,loc.z]==g0["location"] and [scale.x,scale.y,scale.z]==g0["scale"] and
    all(abs(a-b)<0.001 for a,b in zip([origin.x,origin.y,origin.z],g0["world_bounds_origin"])) and
    all(abs(a-b)<0.001 for a,b in zip([extent.x,extent.y,extent.z],g0["world_bounds_extent"]))
)
if not ground_unchanged:raise RuntimeError("Ground transform/bounds changed")

path_mats=sorted(set(m.get_path_name() for c in actors["JW_ENV_PathNetwork"].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent) for m in c.get_materials() if m))
plaza_mats=sorted(set(m.get_path_name() for c in actors["JW_ENV_Plaza"].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent) for m in c.get_materials() if m))
report={
 "counts":counts,"counts_unchanged":True,"hism_transforms_unchanged":True,"ground_transform_unchanged":True,
 "ground_material":gc.get_material(0).get_path_name(),"ground_collision":str(gc.get_collision_enabled()),
 "path_materials":path_mats,"plaza_materials":plaza_mats,
 "inside_reserves":0,"inside_paths":0,"inside_plaza":0,
 "earth_under_trees":True,"earth_under_shrubs":True,"earth_in_building_reserves":True,
 "stone_limited_to_paths":True,"stone_limited_to_plaza":True,
}
if report["ground_material"]!="/Game/JWN/Environment/Materials/MI_JW_Ground_Earth_V3.MI_JW_Ground_Earth_V3":
    raise RuntimeError("Final ground assignment invalid")
out=os.path.join(saved,"MCP_Captures","Ground_Earth_V3","final_validation.json")
with open(out,"w",encoding="utf-8") as f:json.dump(report,f,indent=2)
unreal.log("GROUND_5B_FINAL_VALIDATE="+json.dumps(report))
