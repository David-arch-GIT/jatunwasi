import unreal, json, re
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
vegmesh = re.compile(r'Bush|Tree|Flower|Grass|Plant|Palm|Shrub|Forest|Maple|Boxwood|Fern|Leaf', re.I)
# plaza garden bbox in world (cm)
def in_plaza(l): return -1700 < l.x < 1700 and -2600 < l.y < 600
rows = []
env = {}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    cls = a.get_class().get_name()
    loc = a.get_actor_location()
    # ISM/HISM containers: count instances whose mesh looks vegetal
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m = c.static_mesh.get_name() if getattr(c, 'static_mesh', None) else '?'
        try: n = c.get_instance_count()
        except Exception: n = -1
        if vegmesh.search(m):
            env.setdefault(lab, []).append({'mesh': m, 'inst': n})
    # plain static mesh actors with vegetal mesh, inside plaza
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent):
            continue
        m = c.static_mesh.get_name() if getattr(c, 'static_mesh', None) else '?'
        if vegmesh.search(m) and in_plaza(loc):
            rows.append({'label': lab, 'cls': cls, 'mesh': m, 'loc': [round(loc.x), round(loc.y)]})
            break
out = {'plaza_smactors_veg': rows, 'plaza_smactors_veg_count': len(rows), 'env_ism_veg': env}
json.dump(out, open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/veg_audit.json", 'w'), indent=1)
unreal.log("VEG_AUDIT_DONE plaza_veg_actors=%d env_containers=%d" % (len(rows), len(env)))
