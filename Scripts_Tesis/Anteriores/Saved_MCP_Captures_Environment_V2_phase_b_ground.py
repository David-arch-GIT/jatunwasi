import json
import os
import unreal

SOURCE_MI = "/Game/Megascans/Surfaces/River_Stone_Wall_vfvkdcto/MI_River_Stone_Wall_vfvkdcto_2K"
MASTER = "/Game/JWN/Environment/Materials/M_JW_Ground_PBR_V2"
INSTANCE = "/Game/JWN/Environment/Materials/MI_JW_Ground_PBR_V2"

source = unreal.load_asset(SOURCE_MI)
if not source:
    raise RuntimeError("Compatible Megascans PBR source instance is unavailable")
source_parent = source.get_editor_property("parent")
if not source_parent:
    raise RuntimeError("Megascans PBR source has no parent material")

asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
if not unreal.EditorAssetLibrary.does_asset_exist(MASTER):
    master = asset_tools.duplicate_asset("M_JW_Ground_PBR_V2", "/Game/JWN/Environment/Materials", source_parent)
else:
    master = unreal.load_asset(MASTER)
if not master:
    raise RuntimeError("Could not create/load ground master material")

if not unreal.EditorAssetLibrary.does_asset_exist(INSTANCE):
    instance = asset_tools.duplicate_asset("MI_JW_Ground_PBR_V2", "/Game/JWN/Environment/Materials", source)
else:
    instance = unreal.load_asset(INSTANCE)
if not instance:
    raise RuntimeError("Could not create/load ground material instance")

instance.set_editor_property("parent", master)
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    instance, "Tiling/Offset", unreal.LinearColor(300.0, 300.0, 0.0, 0.0))
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    instance, "Albedo Tint", unreal.LinearColor(0.48, 0.39, 0.28, 1.0))
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(instance, "Normal Strength", 0.7)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(instance, "Min Roughness", 0.58)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(instance, "Max Roughness", 0.92)
unreal.MaterialEditingLibrary.update_material_instance(instance)

subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ground = next((a for a in subsystem.get_all_level_actors() if a.get_actor_label() == "Ground_Cochabamba"), None)
if not ground:
    raise RuntimeError("Ground_Cochabamba not found")
components = ground.get_components_by_class(unreal.StaticMeshComponent)
if len(components) != 1:
    raise RuntimeError("Ground_Cochabamba does not have exactly one StaticMeshComponent")
before = {
    "location": [ground.get_actor_location().x, ground.get_actor_location().y, ground.get_actor_location().z],
    "scale": [ground.get_actor_scale3d().x, ground.get_actor_scale3d().y, ground.get_actor_scale3d().z],
}
components[0].set_material(0, instance)
ground.modify()
after = {
    "location": [ground.get_actor_location().x, ground.get_actor_location().y, ground.get_actor_location().z],
    "scale": [ground.get_actor_scale3d().x, ground.get_actor_scale3d().y, ground.get_actor_scale3d().z],
}
if before != after:
    raise RuntimeError("Ground transform changed unexpectedly")

report = {
    "source_instance": SOURCE_MI,
    "source_parent": source_parent.get_path_name(),
    "master": master.get_path_name(),
    "instance": instance.get_path_name(),
    "ground_material": components[0].get_material(0).get_path_name(),
    "transform_unchanged": before == after,
}
out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2", "phase_b_ground.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
unreal.log("ENV_V2_PHASE_B_READY=" + json.dumps(report))
