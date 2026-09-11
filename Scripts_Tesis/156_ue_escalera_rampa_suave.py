# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) Escalera 2do piso hacienda - RAMPA SUAVE. Mapa real: escalera sube a z407-441, VACIO y-2220..-1980,
#   corredor z432. Pone una rampa suave (visible madera) que va de z~407 (sur, pega con escalera) a z~432 (norte,
#   corredor), llenando el vacio, sin escalon grande. Verifica escalones en junturas (deben ser chicos).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/rampa_suave.json"
res = {"acc": [], "perfil": [], "err": []}
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
CUBE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
MAT = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Architecture/Hacienda_V7/Materials_ArtPass/MI_HACV7_AP_Dark_Wood")
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COL_Puente_Escalera2P":
        eas.destroy_actor(a)
a = unreal.EditorLevelLibrary.spawn_actor_from_object(CUBE, unreal.Vector(-7545, -2100, 402))
a.set_actor_label("COL_Puente_Escalera2P")
a.set_actor_scale3d(unreal.Vector(2.9, 3.9, 0.3))  # 290 x 390 x 30
r = unreal.Rotator(); r.pitch = 0.0; r.yaw = 0.0; r.roll = -5.0
a.set_actor_rotation(r, False)
smc = a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
smc.set_collision_profile_name("BlockAll")
if MAT: smc.set_material(0, MAT)
try: smc.set_editor_property("cast_shadow", False)
except Exception: pass
res["acc"].append("rampa suave creada roll-5")
# VERIFICAR perfil de piso a lo largo (x-7500) de la escalera al corredor
def fz(x, y):
    rr = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x,y,620), unreal.Vector(x,y,360), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if rr is None: return ["V", "-"]
    t = rr.to_tuple()
    if not t[0]: return ["V", "-"]
    return [round(t[5].z), (t[9].get_actor_label()[:10] if t[9] else "?")]
for yy in range(-2320, -1860, 20):
    res["perfil"].append([yy] + fz(-7500, yy))
# calcular max escalon (salto z entre puntos consecutivos con piso)
mx = 0; prev = None
for p in res["perfil"]:
    z = p[1]
    if isinstance(z, int):
        if prev is not None:
            mx = max(mx, abs(z - prev))
        prev = z
    else:
        prev = None
res["max_escalon"] = mx
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("RAMPA SUAVE max_escalon=%d" % mx)
