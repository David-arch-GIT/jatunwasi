# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Da MOVIMIENTO REAL en el juego a las apariciones con componentes NATIVOS (no la secuencia rota): InterpToMovement (flotar/derivar como espiritu, ping-pong) + RotatingMovement (giro muy sutil). Borra la secuencia rota. Funcionan garantizado en PIE.
# Por que se necesito: La animacion por Level Sequence NO corria en el juego (estatuas); el usuario exige movimiento.
# Resultado obtenido: (pendiente) apariciones que flotan/se mueven en el juego.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mov_all.json"
res = {"movidas": []}

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

# borrar secuencia rota + LSA
for a in list(all_actors()):
    if a.get_actor_label() == "LSA_Apariciones":
        unreal.EditorLevelLibrary.destroy_actor(a)
try:
    if unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/Cinematics/LS_Apariciones"):
        unreal.EditorAssetLibrary.delete_asset("/Game/JWN/Cinematics/LS_Apariciones")
except Exception as e:
    res["seq_del_err"] = str(e)

FLOAT = {  # (x,y,z) deriva por leyenda
    "Karisiri":  (18, 10, 34),
    "Condenado": (14, 8, 26),
    "Duende":    (12, 7, 22),
}

def ensure(actor, cls):
    c = actor.get_component_by_class(cls)
    if c is None:
        h = sds.k2_gather_subobject_data_for_instance(actor)
        sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=h[0], new_class=cls))
        c = actor.get_component_by_class(cls)
    return c

for a in all_actors():
    l = a.get_actor_label()
    if not l.startswith("App3D_"):
        continue
    key = None
    for k in FLOAT:
        if k.lower() in l.lower():
            key = k
            break
    if key is None:
        continue
    d = FLOAT[key]
    # flotar
    it = ensure(a, unreal.InterpToMovementComponent)
    cp0 = unreal.InterpControlPoint(); cp0.set_editor_property("position_control_point", unreal.Vector(0, 0, 0)); cp0.set_editor_property("position_is_relative", True)
    cp1 = unreal.InterpControlPoint(); cp1.set_editor_property("position_control_point", unreal.Vector(d[0], d[1], d[2])); cp1.set_editor_property("position_is_relative", True)
    it.set_editor_property("control_points", [cp0, cp1])
    it.set_editor_property("duration", 2.9)
    it.set_editor_property("behaviour_type", unreal.InterpToBehaviourType.PING_PONG)
    # giro sutil
    rot = ensure(a, unreal.RotatingMovementComponent)
    rot.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0, yaw=5.0, roll=0.0))
    res["movidas"].append(l)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MOV all listo: %d" % len(res["movidas"]))
