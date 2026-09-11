import json
import os
import unreal

subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=subsystem.get_all_level_actors()
labels=[a.get_actor_label() for a in actors]
env_labels=("JW_ENV_PathNetwork","JW_ENV_Plaza","JW_ENV_Trees","JW_ENV_Shrubs","JW_ENV_Grass","JW_ENV_Rocks")
counts={}
for label in env_labels:
    a=next((x for x in actors if x.get_actor_label()==label),None)
    counts[label]=sum(c.get_instance_count() for c in a.get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)) if a else None

mp={a.get_actor_label():[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z] for a in actors if a.get_actor_label().startswith("MP_")}
probe={
 "level":unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name(),
 "mp":mp,"mp_count":len(mp),"counts":counts,
 "jw9_hac_count":sum(1 for l in labels if l.startswith("JW9_HAC")),
 "hacv3_pilot_count":sum(1 for l in labels if l.startswith("HACV3_Pilot")),
 "environment_actor_count":sum(1 for l in labels if l in env_labels),
 "geometry_script":{
  "DynamicMesh":hasattr(unreal,"DynamicMesh"),
  "DynamicMeshActor":hasattr(unreal,"DynamicMeshActor"),
  "GeometryScriptLibrary_MeshPrimitiveFunctions":hasattr(unreal,"GeometryScriptLibrary_MeshPrimitiveFunctions"),
  "GeometryScriptLibrary_StaticMeshFunctions":hasattr(unreal,"GeometryScriptLibrary_StaticMeshFunctions"),
  "GeometryScriptLibrary_MeshUVFunctions":hasattr(unreal,"GeometryScriptLibrary_MeshUVFunctions"),
  "GeometryScriptLibrary_MeshNormalsFunctions":hasattr(unreal,"GeometryScriptLibrary_MeshNormalsFunctions"),
 }
}
out=os.path.join(unreal.Paths.project_saved_dir(),"Architecture","Hacienda_V4","pipeline_probe.json")
with open(out,"w",encoding="utf-8") as f:json.dump(probe,f,indent=2)
unreal.log("HACV4_PROBE="+json.dumps(probe))
