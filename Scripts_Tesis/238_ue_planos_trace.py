import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/planos_trace.json"
res = {"planos": [], "err": [], "diag": []}
eas = unreal.EditorActorSubsystem()
EAL = unreal.EditorAssetLibrary
plane_mesh = EAL.load_asset("/Engine/BasicShapes/Plane")
world = unreal.EditorLevelLibrary.get_editor_world()
PLDIR = "/Game/FotosAntano/Planos"

mis = {}
for p in EAL.list_assets(PLDIR, recursive=False):
    base = p.split(".")[0]; nm = base.split("/")[-1]
    if nm.startswith("MI_P_"): mis[nm.lower()] = EAL.load_asset(base)
def pick(token, excl):
    for nm, asset in mis.items():
        if token in nm and all(x not in nm for x in excl): return asset
    return None
MAP = {
 "MUS_Cuadro_00": ("calle_comercio", []),
 "MUS_Cuadro_01": ("calles_de_anta", ["cochabamb","del_ayer"]),
 "MUS_Cuadro_02": ("cochabamb", []),
 "MUS_Cuadro_03": ("del_ayer", []),
 "MUS_Cuadro_coc0": ("de_la_plaza", []),
 "MUS_Cuadro_coc1": ("estadio", []),
 "MUS_Cuadro_dorm0": ("fotos_de_anta", ["carnaval","de_casas"]),
 "BALL_Cuadro_0": ("carnaval", []),
 "BALL_Cuadro_1": ("de_casas", []),
 "COR_Cuadro_00": ("tren", []),
 "COR_Cuadro_01": ("merca", []),
 "COR_Cuadro_03": ("calle_2", ["comercio"]),
 "COR_Cuadro_07": ("memorias", []),
}
# borrar planos previos
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label().startswith("FotoPlano_"): eas.destroy_actor(a)
frames = {}
for a in eas.get_all_level_actors():
    if a.get_actor_label() in MAP: frames[a.get_actor_label()] = a

def free_dist(origin, d, ignore):
    start = unreal.Vector(origin.x, origin.y, origin.z)
    end = unreal.Vector(origin.x + d.x*320, origin.y + d.y*320, origin.z)
    hit = unreal.SystemLibrary.line_trace_single(world, start, end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, ignore,
        unreal.DrawDebugTrace.NONE, True)
    try:
        if hit and hit.blocking_hit:
            return float(hit.distance)
    except Exception:
        pass
    return 320.0

down = unreal.Vector(0,0,-1)
for fn, (tok, excl) in MAP.items():
    a = frames.get(fn)
    if not a: res["err"].append("no frame "+fn); continue
    mi = pick(tok, excl)
    if not mi: res["err"].append("no MI "+fn); continue
    o, e = a.get_actor_bounds(False)
    yaw = math.radians(a.get_actor_rotation().yaw)
    nx = -math.sin(yaw); ny = math.cos(yaw)
    ignore = [a]
    dp = free_dist(o, unreal.Vector(nx,ny,0), ignore)     # +normal
    dm = free_dist(o, unreal.Vector(-nx,-ny,0), ignore)   # -normal
    # sala = lado mas abierto
    if dp >= dm: rx, ry, side = nx, ny, "+n"
    else: rx, ry, side = -nx, -ny, "-n"
    room = unreal.Vector(rx, ry, 0.0)
    rot = unreal.MathLibrary.make_rot_from_zy(room, down)
    pos = unreal.Vector(o.x + rx*4.0, o.y + ry*4.0, o.z)
    pl = eas.spawn_actor_from_object(plane_mesh, pos, rot)
    pl.set_actor_label("FotoPlano_" + fn)
    pl.set_actor_scale3d(unreal.Vector(0.62, 0.77, 1.0))
    smc = pl.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, mi); smc.set_cast_shadow(False)
    res["planos"].append(fn)
    res["diag"].append("%s side=%s d+=%.0f d-=%.0f" % (fn, side, dp, dm))
res["n"] = len(res["planos"])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
