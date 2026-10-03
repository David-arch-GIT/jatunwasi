# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Analiza el claustro del convento para ubicar la vitrina: bbox de actores CONV, posiciones de las
#   instancias de arco, y floor-trace en el centro (Z del suelo). Solo mide.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/claustro_layout.json"
res = {"arcos_inst": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
xs = []; ys = []; zs = []
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.upper().startswith("CONV"):
        continue
    loc = a.get_actor_location()
    xs.append(loc.x); ys.append(loc.y); zs.append(loc.z)
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if m and "arch" in m.get_name().lower():
            n = c.get_instance_count()
            k = n if n < 12 else 12
            for i in range(k):
                t = c.get_instance_transform(i, True)
                p = t.translation
                res["arcos_inst"].append([round(p.x), round(p.y), round(p.z)])
if xs:
    n = len(xs)
    cx = sum(xs) / n; cy = sum(ys) / n
    res["claustro_bbox"] = {"xmin": round(min(xs)), "xmax": round(max(xs)), "ymin": round(min(ys)), "ymax": round(max(ys)), "cx": round(cx), "cy": round(cy), "z_tipico": round(sum(zs) / n)}
    res["n_conv"] = n
    rr = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(cx, cy, 600), unreal.Vector(cx, cy, -200), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1, 0, 0), unreal.LinearColor(0, 1, 0), 0.0)
    if rr:
        t = rr.to_tuple()
        if t[0]:
            res["floor_z_centro"] = round(t[5].z)
            res["floor_actor"] = str(t[9].get_actor_label()[:20]) if t[9] else "?"
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("CLAUSTRO layout arcos=%d" % len(res["arcos_inst"]))
