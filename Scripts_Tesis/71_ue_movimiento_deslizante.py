# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Quita el GIRO tieso (RotatingMovement rate=0) y reconfigura InterpToMovement con un DESLIZAMIENTO de aparicion: sale de los arboles, AVANZA hacia el jugador (acecha), y se RETIRA a la oscuridad, flotando. Movimiento de terror, no un trompo.
# Por que se necesito: El usuario odio el giro sobre el eje; quiere movimiento vivo/deslizante de terror.
# Resultado obtenido: (pendiente) apariciones que se deslizan acechando.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/mov_desliz.json"
res = {"apps": []}

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

# retreat dir (hacia los arboles) por leyenda; -retreat = hacia el jugador
RETREAT = {
    "Karisiri":  (-1.0, 0.2),
    "Condenado": (0.8, -0.5),
    "Duende":    (-0.4, 1.0),
}
DUR = 7.5  # lento, eerie

for a in all_actors():
    l = a.get_actor_label()
    if not l.startswith("App3D_"):
        continue
    key = None
    for k in RETREAT:
        if k.lower() in l.lower():
            key = k
            break
    if key is None:
        continue
    rx, ry = RETREAT[key]
    mag = math.hypot(rx, ry) or 1.0
    rx, ry = rx / mag, ry / mag

    # 1) matar el giro (rate 0) en TODOS los RotatingMovement del actor
    for rot in a.get_components_by_class(unreal.RotatingMovementComponent):
        rot.set_editor_property("rotation_rate", unreal.Rotator(pitch=0.0, yaw=0.0, roll=0.0))

    # 2) reconfigurar el deslizamiento: edge -> avanza al jugador -> retira a arboles (ping-pong), con flotar
    it = a.get_component_by_class(unreal.InterpToMovementComponent)
    if it is None:
        continue
    def cp(x, y, z):
        c = unreal.InterpControlPoint()
        c.set_editor_property("position_control_point", unreal.Vector(x, y, z))
        c.set_editor_property("position_is_relative", True)
        return c
    pts = [
        cp(0.0, 0.0, 0.0),                       # borde (inicio)
        cp(-rx * 190, -ry * 190, 28.0),          # AVANZA hacia el jugador, flotando arriba
        cp(rx * 320, ry * 320, 8.0),             # RETIRA profundo a los arboles
    ]
    it.set_editor_property("control_points", pts)
    it.set_editor_property("duration", DUR)
    it.set_editor_property("behaviour_type", unreal.InterpToBehaviourType.PING_PONG)
    res["apps"].append(l)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MOV deslizante listo: %d" % len(res["apps"]))
