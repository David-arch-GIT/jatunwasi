import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/penetracion.json"
res = {"criaturas": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
POS = {"Cria_Karisiri": (3801.0,3281.0,103.0), "Cria_Condenado": (1031.0,8380.0,103.0), "Cria_Duende": (-4135.0,668.0,146.0)}
def sweep(x,y,z,dx,dy,dist,ignore):
    h = unreal.SystemLibrary.sphere_trace_single(w, unreal.Vector(x,y,z), unreal.Vector(x+dx*dist,y+dy*dist,z), 34.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore, unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if h is None: return None
    t = h.to_tuple()
    if not t[0]: return None
    d = round(((t[5].x-x)**2+(t[5].y-y)**2)**0.5)
    return {"dist": d, "actor": (t[9].get_actor_label()[:20] if t[9] else "?")}
# ignorar las propias criaturas
ignore = [a for a in eas.get_all_level_actors() if a.get_actor_label().startswith("Cria_")]
for lab,(x,y,z) in POS.items():
    d = {"lab": lab}
    # overlap: hay algo tocando en las 4 direcciones a media altura del cuerpo (feet+60 = z-5.. usar z de capsula centro)
    for hz, name in [(z-30, "torso"), (z+30, "cabeza")]:
        near = []
        for dx,dy,nm in [(1,0,"+x"),(-1,0,"-x"),(0,1,"+y"),(0,-1,"-y")]:
            r = sweep(x,y,hz,dx,dy,60,ignore)
            if r and r["dist"] < 40:
                near.append(nm+":"+r["actor"]+"("+str(r["dist"])+")")
        d[name+"_pegado"] = near if near else "libre"
    # trace hacia abajo desde el centro para ver el piso y su distancia a los pies (feet=z-88)
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,z), unreal.Vector(x,y,z-400), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore, unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]:
            piso_z = round(t[5].z); pies_z = round(z-88)
            d["piso_z"] = piso_z; d["pies_z"] = pies_z; d["pies_sobre_piso_cm"] = pies_z - piso_z
            d["piso_actor"] = t[9].get_actor_label()[:18] if t[9] else "?"
    res["criaturas"].append(d)
open(OUT, "w").write(json.dumps(res, indent=1))
