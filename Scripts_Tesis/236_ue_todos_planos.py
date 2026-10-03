import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/todos_planos.json"
res = {"planos": [], "err": []}
eas = unreal.EditorActorSubsystem()
EAL = unreal.EditorAssetLibrary
plane_mesh = EAL.load_asset("/Engine/BasicShapes/Plane")
PLDIR = "/Game/FotosAntano/Planos"

# listar MI_P_ existentes (nombre -> asset)
mis = {}
for p in EAL.list_assets(PLDIR, recursive=False):
    base = p.split(".")[0]
    nm = base.split("/")[-1]
    if nm.startswith("MI_P_"):
        mis[nm.lower()] = EAL.load_asset(base)

def pick(token, excl):
    for nm, asset in mis.items():
        if token in nm and all(x not in nm for x in excl):
            return asset
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
    if a.get_actor_label().startswith("FotoPlano_"):
        eas.destroy_actor(a)
frames = {}
for a in eas.get_all_level_actors():
    if a.get_actor_label() in MAP:
        frames[a.get_actor_label()] = a
down = unreal.Vector(0,0,-1)
for fn, (tok, excl) in MAP.items():
    a = frames.get(fn)
    if not a: res["err"].append("no frame "+fn); continue
    mi = pick(tok, excl)
    if not mi: res["err"].append("no MI "+fn+" tok="+tok); continue
    o, e = a.get_actor_bounds(False)
    yaw = math.radians(a.get_actor_rotation().yaw)
    nx = -math.sin(yaw); ny = math.cos(yaw)
    rx = -nx; ry = -ny
    room = unreal.Vector(rx, ry, 0.0)
    rot = unreal.MathLibrary.make_rot_from_zy(room, down)
    pos = unreal.Vector(o.x + rx*4.0, o.y + ry*4.0, o.z)
    pl = eas.spawn_actor_from_object(plane_mesh, pos, rot)
    pl.set_actor_label("FotoPlano_" + fn)
    pl.set_actor_scale3d(unreal.Vector(0.62, 0.77, 1.0))
    smc = pl.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, mi)
    smc.set_cast_shadow(False)
    res["planos"].append(fn + " <- " + mi.get_name())
c07 = frames.get("COR_Cuadro_07")
if c07:
    mc = EAL.load_asset("/Game/FotosAntano/Encuadradas/MI_C_memorias_del_ayer")
    if mc:
        for c in c07.get_components_by_class(unreal.StaticMeshComponent):
            c.set_material(1, mc)
res["n"] = len(res["planos"]); res["n_mi_found"] = len(mis)
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
