import unreal, json

eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
out = []
for a in actors:
    try:
        label = a.get_actor_label()
        name = a.get_name()
        cls = a.get_class().get_name()
        loc = a.get_actor_location()
        rot = a.get_actor_rotation()
        scale = a.get_actor_scale3d()
        try:
            origin, extent = a.get_actor_bounds(False)
        except Exception:
            origin, extent = loc, unreal.Vector(0, 0, 0)
        meshes = []
        try:
            comps = a.get_components_by_class(unreal.StaticMeshComponent)
            for c in comps:
                m = c.static_mesh
                if m:
                    meshes.append(m.get_path_name())
        except Exception:
            pass
        # splines
        has_spline = False
        try:
            sc = a.get_components_by_class(unreal.SplineComponent)
            has_spline = len(sc) > 0
        except Exception:
            pass
        rec = {
            "label": label, "name": name, "class": cls,
            "loc": [round(loc.x, 1), round(loc.y, 1), round(loc.z, 1)],
            "yaw": round(rot.yaw, 1),
            "scale": [round(scale.x, 3), round(scale.y, 3), round(scale.z, 3)],
            "bounds_origin": [round(origin.x, 1), round(origin.y, 1), round(origin.z, 1)],
            "bounds_extent": [round(extent.x, 1), round(extent.y, 1), round(extent.z, 1)],
            "meshes": meshes,
            "has_spline": has_spline,
        }
        out.append(rec)
    except Exception as e:
        out.append({"error": str(e)})

path = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/actors_v08.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
unreal.log("ACTORDUMP_DONE count=%d -> %s" % (len(out), path))
