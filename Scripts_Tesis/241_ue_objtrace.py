import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/objtrace.json"
res = {}
eas = unreal.EditorActorSubsystem()
world = unreal.EditorLevelLibrary.get_editor_world()
OT = [unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1, unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY2,
      unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY3, unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY4]
def gp(h,k):
    try: return h.get_editor_property(k)
    except Exception: return None
def dist(o, dirv, ignore):
    start=unreal.Vector(o.x,o.y,o.z); end=unreal.Vector(o.x+dirv.x*400,o.y+dirv.y*400,o.z+dirv.z*400)
    h=unreal.SystemLibrary.line_trace_single_for_objects(world,start,end,OT,False,ignore,unreal.DrawDebugTrace.NONE,True)
    if h is None: return 400.0, None
    bh=gp(h,"blocking_hit"); d=gp(h,"distance"); act=gp(h,"hit_actor")
    if bh and d is not None: return round(float(d),1), (act.get_actor_label() if act else None)
    return 400.0, None
for lbl in ["COR_Cuadro_07","MUS_Cuadro_00","MUS_Cuadro_03","MUS_Cuadro_coc1"]:
    fa=None
    for a in eas.get_all_level_actors():
        if a.get_actor_label()==lbl: fa=a; break
    o,e=fa.get_actor_bounds(False)
    ig=[fa]
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("FotoPlano_"): ig.append(a)
    yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
    dp,ap=dist(o,unreal.Vector(nx,ny,0),ig)
    dm,am=dist(o,unreal.Vector(-nx,-ny,0),ig)
    res[lbl]={"plusN":[dp,ap],"minusN":[dm,am]}
open(OUT,"w").write(json.dumps(res,indent=1))
