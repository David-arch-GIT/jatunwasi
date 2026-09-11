# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) ARREGLO FINAL escalera 2do piso hacienda. Diagnostico (sphere-sweep con normales): el
#   HACV7_UpperLandingConnector daba piso PERO tenia un MURO (z500-546) que bloqueaba el cuerpo. Fix: (1) colision del
#   conector OFF (visual queda). (2) reconstruir COL_Puente_Escalera2P como losa PLANA VISIBLE de madera que cubre todo
#   el tramo escalera(y-2410,z441)->corredor(y-1890,z432), piso continuo z440, SIN muro. Verifica sphere-sweep + piso.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/escalera_final.json"
res = {"acc": [], "verif_muro": {}, "verif_piso": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
CUBE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
MAT = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Dark_Wood")
# (1) conector colision OFF
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "HACV7_UpperLandingConnector":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        res["acc"].append("conector colision OFF")
    if a.get_actor_label() == "COL_Puente_Escalera2P":
        eas.destroy_actor(a); res["acc"].append("puente viejo borrado")
# (2) losa plana visible madera, cubre escalera->corredor
a = unreal.EditorLevelLibrary.spawn_actor_from_object(CUBE, unreal.Vector(-7565, -2150, 425))
a.set_actor_label("COL_Puente_Escalera2P")
a.set_actor_scale3d(unreal.Vector(2.5, 5.2, 0.3))  # 250 x 520 x 30, top z440
smc = a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
smc.set_collision_profile_name("BlockAll")
if MAT: smc.set_material(0, MAT)
try: smc.set_editor_property("cast_shadow", False)
except Exception: pass
res["acc"].append("losa plana visible creada")
# VERIFICAR: sphere sweep norte (muro?) a body height
def sph(x, y, z, dist=450, r=34):
    h = unreal.SystemLibrary.sphere_trace_single(w, unreal.Vector(x,y,z), unreal.Vector(x,y+dist,z), r, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if h is None: return "LIBRE"
    t = h.to_tuple()
    if not t[0]: return "LIBRE"
    nz = t[7].z; tipo = "MURO" if abs(nz) < 0.35 else "piso"
    return "%s dy=%d %s" % (tipo, round(t[5].y-y), (t[9].get_actor_label()[:16] if t[9] else "?"))
for xx in [-7500, -7565, -7620]:
    res["verif_muro"]["x%d" % xx] = sph(xx, -2350, 500)
# VERIFICAR: piso continuo z (down-trace) de y-2410 a -1880
def fz(x, y):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,560), unreal.Vector(x,y,380), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r is None: return "VACIO"
    t = r.to_tuple()
    if not t[0]: return "VACIO"
    return "%d" % round(t[5].z)
y = -2410
while y <= -1880:
    res["verif_piso"].append([y, fz(-7560, y)]); y += 30
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ESCALERA FINAL ok")
