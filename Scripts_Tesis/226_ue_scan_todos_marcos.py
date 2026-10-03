import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/scan_marcos.json"
res = {"por_mesh": {}, "marcos": [], "canvas_default": [], "err": None}
eas = unreal.EditorActorSubsystem()
# 1) mesh de referencia = el de MUS_Cuadro_00
ref_mesh = None
byl = {}
for a in eas.get_all_level_actors():
    byl[a.get_actor_label()] = a
ref = byl.get("MUS_Cuadro_00")
if ref:
    for c in ref.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if m: ref_mesh = m.get_name()
res["ref_mesh"] = ref_mesh
# 2) escanear todos
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        mn = m.get_name() if m else None
        if not mn: continue
        res["por_mesh"][mn] = res["por_mesh"].get(mn, 0) + 1
        if mn == ref_mesh:
            try:
                s1 = c.get_material(1); s1n = s1.get_name() if s1 else None
            except Exception:
                s1n = "ERR"
            loc = a.get_actor_location()
            entry = {"lbl": lbl, "slot1": s1n, "loc": [round(loc.x), round(loc.y), round(loc.z)]}
            res["marcos"].append(entry)
            # los que NO tienen mi foto (no empiezan por MI_C_) = sin asignar
            if not (s1n and s1n.startswith("MI_C_")):
                res["canvas_default"].append(entry)
res["n_marcos"] = len(res["marcos"])
res["n_sin_asignar"] = len(res["canvas_default"])
open(OUT, "w").write(json.dumps(res, indent=1))
