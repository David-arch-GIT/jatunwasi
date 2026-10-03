import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/trace_diag.json"
res = {}
eas = unreal.EditorActorSubsystem()
world = unreal.EditorLevelLibrary.get_editor_world()
def gp(h,k):
    try: return h.get_editor_property(k)
    except Exception: return None
def trace(o, dirv):
    start = unreal.Vector(o.x,o.y,o.z)
    end = unreal.Vector(o.x+dirv.x*400, o.y+dirv.y*400, o.z+dirv.z*400)
    h = unreal.SystemLibrary.line_trace_single(world, start, end, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    if h is None: return {"hit": False}
    bh = gp(h,"blocking_hit"); dist = gp(h,"distance")
    act = gp(h,"hit_actor")
    lbl = act.get_actor_label() if act else None
    return {"hit": bool(bh), "dist": round(float(dist),1) if dist is not None else None, "actor": lbl}
for lbl in ["COR_Cuadro_07","MUS_Cuadro_00","MUS_Cuadro_03","MUS_Cuadro_coc1"]:
    fa=None
    for a in eas.get_all_level_actors():
        if a.get_actor_label()==lbl: fa=a; break
    o,e = fa.get_actor_bounds(False)
    yaw = math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
    res[lbl] = {"plusN": trace(o, unreal.Vector(nx,ny,0)), "minusN": trace(o, unreal.Vector(-nx,-ny,0))}
open(OUT,"w").write(json.dumps(res, indent=1))
