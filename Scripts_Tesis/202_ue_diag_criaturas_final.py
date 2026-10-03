import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_final.json"
res = {"criaturas": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
ESPERADO = {
    "Cria_Karisiri": (3801.0, 3281.0, 103.0),
    "Cria_Condenado": (1031.0, 8380.0, 103.0),
    "Cria_Duende": (-4135.0, 668.0, 146.0),
}
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if lab not in ESPERADO: continue
    loc = a.get_actor_location()
    d = {"lab": lab, "clase": a.get_class().get_name(),
         "coord_actual": [round(loc.x,1), round(loc.y,1), round(loc.z,1)],
         "coord_esperada": list(ESPERADO[lab]),
         "coincide": (abs(loc.x-ESPERADO[lab][0])<0.5 and abs(loc.y-ESPERADO[lab][1])<0.5 and abs(loc.z-ESPERADO[lab][2])<0.5)}
    # auto possess
    try: d["auto_possess_ai"] = str(a.get_editor_property("auto_possess_ai"))
    except Exception as e: d["auto_possess_ai"] = "err"
    # variables
    for v in ["RadioZona","VelMin","VelMax","PausaMin","PausaMax"]:
        try: d[v] = a.get_editor_property(v)
        except Exception: d[v] = "err"
    # skeletal mesh
    mc = a.get_component_by_class(unreal.SkeletalMeshComponent)
    if mc:
        try:
            sk = mc.get_skeletal_mesh_asset()
            d["skeletal_mesh"] = sk.get_name() if sk else "NINGUNO"
        except Exception:
            try:
                sk = mc.get_editor_property("skeletal_mesh_asset")
                d["skeletal_mesh"] = sk.get_name() if sk else "NINGUNO"
            except Exception as e: d["skeletal_mesh"] = "err"
        try:
            ac = mc.get_editor_property("anim_class")
            d["anim_class"] = ac.get_name() if ac else "NINGUNA"
        except Exception: d["anim_class"] = "err"
    # navmesh bajo la criatura (project con extent que cubra su altura)
    try:
        pj = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(loc.x,loc.y,loc.z), None, None, unreal.Vector(300,300,300))
        if pj is not None:
            if isinstance(pj, tuple): pj = pj[1] if pj[0] else None
        if pj is not None:
            dz = round(pj.z - loc.z)
            d["navmesh"] = "SI (nav_z=%d, dz=%d)" % (round(pj.z), dz)
        else:
            d["navmesh"] = "NO HAY NAVMESH CERCA"
    except Exception as e:
        d["navmesh"] = "err:" + str(e)[:30]
    # floor trace
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(loc.x,loc.y,loc.z+50), unreal.Vector(loc.x,loc.y,loc.z-400), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        d["piso_debajo"] = ("z=%d %s" % (round(t[5].z), (t[9].get_actor_label()[:16] if t[9] else "?"))) if t[0] else "VACIO(sin piso)"
    res["criaturas"].append(d)
open(OUT, "w").write(json.dumps(res, indent=1))
