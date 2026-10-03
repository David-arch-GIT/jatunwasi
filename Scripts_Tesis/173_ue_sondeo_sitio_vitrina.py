# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Sondea el sitio candidato de la vitrina (x=6120, entre arcos de la fila y=4100). Halla: floor Z en
#   varios puntos, y muros en +y/-y/+x/-x a la altura del cuerpo (para saber donde esta la pared y hacia donde mira el
#   patio). Solo mide.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/sitio_vitrina.json"
res = {"floor": {}, "muros": {}, "err": []}
w = unreal.EditorLevelLibrary.get_editor_world()
CX = 6120.0
def floor_z(x, y):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, 500), unreal.Vector(x, y, -200), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]: return [round(t[5].z), str(t[9].get_actor_label()[:16]) if t[9] else "?"]
    return ["VACIO", "-"]
for y in [4300, 4100, 3950, 3800, 3650]:
    res["floor"]["y%d" % y] = floor_z(CX, y)
def sweep(x, y, dx, dy, dist, name):
    r = unreal.SystemLibrary.line_trace_single(w, unreal.Vector(x, y, 130), unreal.Vector(x + dx*dist, y + dy*dist, 130), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True, unreal.LinearColor(1,0,0), unreal.LinearColor(0,1,0), 0.0)
    if r:
        t = r.to_tuple()
        if t[0]:
            return "%s: dist=%d %s" % (name, round(((t[5].x-x)**2+(t[5].y-y)**2)**0.5), str(t[9].get_actor_label()[:18]) if t[9] else "?")
    return "%s: LIBRE(%dm)" % (name, dist//100)
# desde el punto de la arcada, a donde hay pared
res["muros"]["hacia_-y(interior)"] = sweep(CX, 4100, 0, -1, 1500, "-y")
res["muros"]["hacia_+y(patio)"] = sweep(CX, 4100, 0, 1, 2500, "+y")
res["muros"]["hacia_-x"] = sweep(CX, 4100, -1, 0, 600, "-x")
res["muros"]["hacia_+x"] = sweep(CX, 4100, 1, 0, 600, "+x")
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("SONDEO sitio ok")
