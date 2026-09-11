# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) REHACE el puente escalera->2do piso. El anterior quedo corrido al oeste y muy alto. Segun el mapa de
#   trazos: la rampa topa en ~z414 en x-7438/-7485 (y-2260) y al norte hay vacio hasta el connector (z439, y-2180).
#   Nuevo puente ANCHO (x-7410..-7680) en pendiente suave de z412 (sur, pega con rampa) a z440 (norte, pega connector).
#   Verifica con trazos en 2 x. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/puente_v2.json"
res = {"rot": None, "verif_ramp_x-7460": [], "verif_conn_x-7560": [], "err": []}
CUBE = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
eas = unreal.EditorActorSubsystem()
w = unreal.EditorLevelLibrary.get_editor_world()
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COL_Puente_Escalera2P":
        eas.destroy_actor(a)
a = unreal.EditorLevelLibrary.spawn_actor_from_object(CUBE, unreal.Vector(-7545,-2225,414))
a.set_actor_label("COL_Puente_Escalera2P")
a.set_actor_scale3d(unreal.Vector(2.7,2.1,0.3))  # 270 x 210 x 30
r = unreal.Rotator(); r.pitch=0.0; r.yaw=0.0; r.roll=-14.0
a.set_actor_rotation(r, False)
res["rot"] = [r.pitch, r.yaw, r.roll]
smc = a.get_component_by_class(unreal.StaticMeshComponent)
smc.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
smc.set_collision_profile_name("BlockAll")
a.set_actor_hidden_in_game(True)
try: smc.set_editor_property("cast_shadow", False)
except Exception: pass
def fz(x,y):
    rr=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,520),unreal.Vector(x,y,360),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True,unreal.LinearColor(1,0,0),unreal.LinearColor(0,1,0),0.0)
    if rr is None: return "_"
    t=rr.to_tuple()
    if not t[0]: return "_"
    return "%d|%s"%(round(t[5].z),(t[9].get_actor_label()[:14] if t[9] else "?"))
for xx,key in [(-7460,"verif_ramp_x-7460"),(-7560,"verif_conn_x-7560")]:
    y=-2320
    while y<=-2120:
        res[key].append([y, fz(xx,y)]); y+=20
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
try: unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
except Exception as e: res["err"].append("save:"+str(e)[:60])
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("PUENTE V2 ok")
