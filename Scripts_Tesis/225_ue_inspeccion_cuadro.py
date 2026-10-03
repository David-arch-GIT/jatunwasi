import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/insp_cuadro.json"
res = {}
TARGETS = ["MUS_Cuadro_00", "MUS_Cuadro_dorm0", "COR_Cuadro_00"]
eas = unreal.EditorActorSubsystem()
byl = {}
for a in eas.get_all_level_actors():
    byl[a.get_actor_label()] = a
for tl in TARGETS:
    a = byl.get(tl)
    if not a:
        res[tl] = {"err": "no actor"}; continue
    info = {"class": a.get_class().get_name(), "comps": []}
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        cd = {"comp": c.get_name(), "mesh": None, "slots": []}
        try:
            m = c.get_static_mesh()
            cd["mesh"] = m.get_name() if m else None
            names = c.get_material_slot_names()
            cd["slot_names"] = [str(x) for x in names]
        except Exception as e:
            cd["mesh_err"] = str(e)[:60]
        try:
            n = c.get_num_materials() if hasattr(c, "get_num_materials") else len(c.get_materials())
            for i in range(n):
                mi = c.get_material(i)
                mn = mi.get_name() if mi else None
                # textura del parametro Foto si es MI
                tex = None
                if isinstance(mi, unreal.MaterialInstanceConstant):
                    tv = unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi, "Foto")
                    tex = tv.get_name() if tv else None
                cd["slots"].append({"i": i, "mat": mn, "foto_tex": tex})
        except Exception as e:
            cd["slot_err"] = str(e)[:60]
        info["comps"].append(cd)
    res[tl] = info
open(OUT, "w").write(json.dumps(res, indent=1))
