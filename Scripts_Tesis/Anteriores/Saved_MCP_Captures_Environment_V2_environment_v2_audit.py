import json
import os
import unreal

world = unreal.EditorLevelLibrary.get_editor_world()
actors = unreal.EditorLevelLibrary.get_all_level_actors()

def vec(v):
    return [v.x, v.y, v.z]
report = {
    "world": world.get_path_name() if world else None,
    "actors": [],
    "texture_candidates": [],
}

for actor in actors:
    label = actor.get_actor_label()
    if label.startswith("JW_ENV_") or label == "Ground_Cochabamba" or label.startswith("MP_"):
        item = {
            "label": label,
            "class": actor.get_class().get_name(),
            "path": actor.get_path_name(),
            "location": vec(actor.get_actor_location()),
            "scale": vec(actor.get_actor_scale3d()),
            "bounds": [vec(v) for v in actor.get_actor_bounds(False)],
            "components": [],
        }
        for comp in actor.get_components_by_class(unreal.ActorComponent):
            c = {"name": comp.get_name(), "class": comp.get_class().get_name()}
            if isinstance(comp, unreal.InstancedStaticMeshComponent):
                mesh = comp.get_editor_property("static_mesh")
                c["instances"] = comp.get_instance_count()
                c["mesh"] = mesh.get_path_name() if mesh else None
                if mesh:
                    c["mesh_bounds_extent"] = vec(mesh.get_bounds().box_extent)
                mats = comp.get_materials()
                c["materials"] = [m.get_path_name() if m else None for m in mats]
            elif isinstance(comp, unreal.StaticMeshComponent):
                mesh = comp.get_editor_property("static_mesh")
                c["mesh"] = mesh.get_path_name() if mesh else None
                c["materials"] = [m.get_path_name() if m else None for m in comp.get_materials()]
            item["components"].append(c)
        report["actors"].append(item)

registry = unreal.AssetRegistryHelpers.get_asset_registry()
terms = ("soil", "dirt", "earth", "ground", "dry_ground", "forest_floor", "rocky_ground")
for root in ("/Game/Megascans", "/Game/StylescapeHD"):
    for data in registry.get_assets_by_path(root, recursive=True):
        name = str(data.asset_name).lower()
        path = str(data.package_name)
        if any(t in name or t in path.lower() for t in terms):
            report["texture_candidates"].append({
                "name": str(data.asset_name),
                "path": path,
                "class": str(data.asset_class_path.asset_name),
            })

out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2", "audit_current.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
unreal.log("ENV_V2_AUDIT_WRITTEN=" + out)
