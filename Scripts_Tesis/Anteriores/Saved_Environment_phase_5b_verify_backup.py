import json
import math
import os
import unreal

subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = {a.get_actor_label(): a for a in subsystem.get_all_level_actors()}
labels = ("JW_ENV_PathNetwork","JW_ENV_Plaza","JW_ENV_Trees","JW_ENV_Shrubs","JW_ENV_Grass","JW_ENV_Rocks")
counts = {}
component_transforms = {}
for label in labels:
    actor = actors.get(label)
    if not actor:
        raise RuntimeError(label + " missing")
    comps = actor.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    counts[label] = sum(c.get_instance_count() for c in comps)
    component_transforms[label] = {
        c.get_name(): [
            {
                "location":[c.get_instance_transform(i,True).translation.x,c.get_instance_transform(i,True).translation.y,c.get_instance_transform(i,True).translation.z],
                "scale":[c.get_instance_transform(i,True).scale3d.x,c.get_instance_transform(i,True).scale3d.y,c.get_instance_transform(i,True).scale3d.z],
                "rotation":[c.get_instance_transform(i,True).rotation.x,c.get_instance_transform(i,True).rotation.y,c.get_instance_transform(i,True).rotation.z,c.get_instance_transform(i,True).rotation.w],
            } for i in range(c.get_instance_count())
        ] for c in comps
    }

expected={"JW_ENV_PathNetwork":170,"JW_ENV_Plaza":43,"JW_ENV_Trees":525,"JW_ENV_Shrubs":1350,"JW_ENV_Grass":3300,"JW_ENV_Rocks":210}
if counts != expected:
    raise RuntimeError("Starting counts mismatch: "+str(counts))

ground=actors.get("Ground_Cochabamba")
if not ground:
    raise RuntimeError("Ground_Cochabamba missing")
comps=ground.get_components_by_class(unreal.StaticMeshComponent)
if len(comps)!=1:
    raise RuntimeError("Ground must have exactly one StaticMeshComponent")
comp=comps[0]
origin,extent=ground.get_actor_bounds(False)
loc=ground.get_actor_location(); scale=ground.get_actor_scale3d()
materials=[m.get_path_name() if m else None for m in comp.get_materials()]
mp_count=sum(1 for a in actors.values() if a.get_actor_label().startswith("MP_"))
if mp_count != 7:
    raise RuntimeError("MP target count mismatch: %d"%mp_count)

report={
    "level":"/Game/JWN/MAP_JatunWasi_MCP_V01",
    "counts":counts,
    "mp_target_count":mp_count,
    "ground":{
        "actor_path":ground.get_path_name(),
        "component":comp.get_name(),
        "world_bounds_origin":[origin.x,origin.y,origin.z],
        "world_bounds_extent":[extent.x,extent.y,extent.z],
        "dimensions_cm":[extent.x*2,extent.y*2,extent.z*2],
        "material_slots":materials,
        "material_slot_count":len(materials),
        "location":[loc.x,loc.y,loc.z],
        "scale":[scale.x,scale.y,scale.z],
        "static_mesh":comp.get_editor_property("static_mesh").get_path_name(),
        "collision":str(comp.get_collision_enabled()),
    },
    "hism_transform_snapshot":component_transforms,
    "verified_exclusions_from_environment_v2":{"inside_reserves":0,"inside_paths":0,"inside_plaza":0},
}
out=os.path.join(unreal.Paths.project_saved_dir(),"Environment","JW_Ground_Assignment_Backup_V2.json")
with open(out,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
unreal.log("GROUND_5B_BACKUP="+out)
