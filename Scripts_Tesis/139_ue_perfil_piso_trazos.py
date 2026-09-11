# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Traza rayos hacia abajo para mapear la altura del piso con COLISION a lo largo de: (A) el eje de la
#   entrada (y=-2500, x de -6000 a -7500) y (B) el cruce escalera->corredor (x=-7588, y de -2600 a -2100). Revela la
#   brecha (donde no hay piso o hay salto de altura) sin depender del visor.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/perfil_piso.json"
res = {"entrada_y-2500": [], "cruce_2piso_x-7588": [], "err": []}
world = unreal.EditorLevelLibrary.get_editor_world()
def floorZ(x, y, ztop, zbot):
    start = unreal.Vector(x, y, ztop); end = unreal.Vector(x, y, zbot)
    hit = unreal.SystemLibrary.line_trace_single(world, start, end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True,
        unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if hit:
        try:
            loc = hit.to_tuple()[4]  # impact point
            return round(loc.z)
        except Exception:
            try: return round(hit.impact_point.z)
            except Exception: return "hit?"
    return None
# (A) entrada: y=-2500, x de -6000 a -7500 cada 100, trazo z600->-100
x = -6000
while x >= -7500:
    res["entrada_y-2500"].append([x, floorZ(x, -2500, 600, -100)])
    x -= 100
# (B) cruce 2do piso: x=-7588, y de -2600 a -2050 cada 50, trazo z520->380
y = -2600
while y <= -2050:
    res["cruce_2piso_x-7588"].append([y, floorZ(-7588, y, 520, 380)])
    y += 50
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("PERFIL ok")
