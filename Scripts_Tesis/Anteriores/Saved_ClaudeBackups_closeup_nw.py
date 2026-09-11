import unreal, json
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
# tight top-down over NW garden center (~ -1125, -430)
ues.set_level_viewport_camera_info(unreal.Vector(-1125.0, -430.0, 1500.0), unreal.Rotator(0.0, -90.0, 0.0))

# inspect InstancedFoliageActor instance counts
info = {"foliage": []}
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_class().get_name() == "InstancedFoliageActor":
        comps = a.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for c in comps:
            try:
                n = c.get_instance_count()
            except Exception:
                n = -1
            m = c.static_mesh.get_name() if getattr(c, "static_mesh", None) else "?"
            info["foliage"].append({"mesh": m, "instances": n})
json.dump(info, open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/foliage_info.json", "w"), indent=1)
unreal.log("CLOSEUP_NW_DONE foliage_comps=%d" % len(info["foliage"]))
