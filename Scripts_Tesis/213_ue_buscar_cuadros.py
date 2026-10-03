import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cuadros.json"
res = {"cuadros": [], "err": []}
eas = unreal.EditorActorSubsystem()
KEY = ["marco", "cuadro", "foto", "frame", "portrait", "picture", "retrato", "pintura", "painting", "photo"]
for a in eas.get_all_level_actors():
    lab = a.get_actor_label().lower()
    meshes = []
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if m: meshes.append(m.get_name())
    meshstr = " ".join(meshes).lower()
    if not (any(k in lab for k in KEY) or any(k in meshstr for k in KEY)):
        continue
    loc = a.get_actor_location()
    d = {"label": a.get_actor_label(), "loc": [round(loc.x), round(loc.y), round(loc.z)], "meshes": meshes, "mats": []}
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        for i, mi in enumerate(c.get_materials()):
            d["mats"].append([i, (mi.get_name() if mi else "NULL")])
    res["cuadros"].append(d)
res["n"] = len(res["cuadros"])
open(OUT, "w").write(json.dumps(res, indent=1))
