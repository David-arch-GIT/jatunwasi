import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mesh_fisica.json"
res = {"instancias": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    if not a.get_actor_label().startswith("Cria_"): continue
    mc = a.get_component_by_class(unreal.SkeletalMeshComponent)
    if not mc: continue
    d = {"cria": a.get_actor_label()}
    for prop in ["simulate_physics", "collision_enabled", "collision_profile_name"]:
        try:
            if prop == "collision_enabled": d[prop] = str(mc.get_collision_enabled())
            elif prop == "collision_profile_name": d[prop] = str(mc.get_collision_profile_name())
            else: d[prop] = mc.get_editor_property(prop)
        except Exception as e:
            d[prop] = "err:"+str(e)[:20]
    # physics asset
    try:
        pa = mc.get_editor_property("physics_asset_override")
        sk = mc.get_skeletal_mesh_asset()
        d["mesh"] = sk.get_name() if sk else "?"
    except Exception: pass
    # tick / update
    try: d["rel_loc_z"] = round(mc.get_relative_location().z)
    except Exception: pass
    res["instancias"].append(d)
open(OUT, "w").write(json.dumps(res, indent=1))
