import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nav_criaturas.json"
res = {"borrados": [], "nuevos": [], "reach": {}, "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
ell = unreal.EditorLevelLibrary
# posiciones actuales de las Cria_
pos = {}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab.startswith("Cria_"):
        loc = a.get_actor_location()
        pos[lab] = (loc.x, loc.y, loc.z)
# borrar CRIA_Nav viejos (mal ubicados)
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label().startswith("CRIA_Nav_"):
        try: eas.destroy_actor(a); res["borrados"].append(a.get_actor_label())
        except Exception as e: res["err"].append("del:"+str(e)[:30])
# nav nuevo centrado en cada criatura
for lab, (x, y, z) in pos.items():
    try:
        vol = ell.spawn_actor_from_class(unreal.NavMeshBoundsVolume, unreal.Vector(x, y, z))
        vol.set_actor_label("Nav_" + lab)
        vol.set_actor_scale3d(unreal.Vector(16.0, 16.0, 8.0))  # ~1600x1600x800
        res["nuevos"].append("Nav_" + lab)
    except Exception as e:
        res["err"].append("spawn nav "+lab+":"+str(e)[:30])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
# verificar reachability (probar API)
for lab, (x, y, z) in pos.items():
    got = None
    for call in ["A", "B"]:
        try:
            if call == "A":
                r = unreal.NavigationSystemV1.get_random_reachable_point_in_radius(w, unreal.Vector(x,y,z), 400.0)
            else:
                nav = unreal.NavigationSystemV1.get_navigation_system(w)
                r = nav.get_random_reachable_point_in_radius(unreal.Vector(x,y,z), 400.0)
            got = str(r)[:60]; break
        except Exception as e:
            got = "err:" + str(e)[:45]
    res["reach"][lab] = got
open(OUT, "w").write(json.dumps(res, indent=1))
