import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/seleccion.json"
res = {"sel": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_selected_level_actors():
    info = {"lbl": a.get_actor_label(), "class": a.get_class().get_name(), "comps": []}
    loc = a.get_actor_location(); info["loc"] = [round(loc.x), round(loc.y), round(loc.z)]
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        cd = {"mesh": m.get_name() if m else None, "slots": []}
        try:
            n = c.get_num_materials()
        except Exception:
            n = 0
        for i in range(n):
            mi = c.get_material(i)
            tex = None
            if isinstance(mi, unreal.MaterialInstanceConstant):
                for pn in ["Foto", "BaseColor", "Texture", "Albedo", "Diffuse"]:
                    try:
                        tv = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi, pn)
                        if tv: tex = pn+"="+tv.get_name(); break
                    except Exception: pass
            cd["slots"].append({"i": i, "mat": mi.get_name() if mi else None, "tex": tex})
        info["comps"].append(cd)
    res["sel"].append(info)
res["n"] = len(res["sel"])
open(OUT, "w").write(json.dumps(res, indent=1))
