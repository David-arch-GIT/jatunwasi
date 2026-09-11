# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) Audita las transiciones camino->edificio de CONVENTO y TEMPLO (como la entrada de hacienda que tenia
#   escalon de 60cm). Traza el perfil de piso a lo largo del acceso y reporta z+actor para detectar escalones/vacios.
#   Solo LEE. Convento ~(6200,5100), path llega por y~2750. Templo ~(50,12155), path llega por y~7600.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_entradas.json"
res = {"convento": {}, "templo": {}, "err": []}
w = unreal.EditorLevelLibrary.get_editor_world()
def fz(x,y,zt,zb):
    r=unreal.SystemLibrary.line_trace_single(w,unreal.Vector(x,y,zt),unreal.Vector(x,y,zb),unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,True,[],unreal.DrawDebugTrace.NONE,True,unreal.LinearColor(1,0,0),unreal.LinearColor(0,1,0),0.0)
    if r is None: return "_"
    t=r.to_tuple()
    if not t[0]: return "_"
    return "%d|%s"%(round(t[5].z),(t[9].get_actor_label()[:16] if t[9] else "?"))
# CONVENTO: acercarse por y creciente en 3 lineas x
for xx in [6000,6200,6400]:
    col=[]; y=3200
    while y<=5400:
        col.append([y, fz(xx,y,900,-200)]); y+=100
    res["convento"]["x%d"%xx]=col
# TEMPLO: acercarse por y creciente
for xx in [-150,50,250]:
    col=[]; y=8800
    while y<=11600:
        col.append([y, fz(xx,y,1100,-200)]); y+=100
    res["templo"]["x%d"%xx]=col
open(OUT,"w").write(json.dumps(res, indent=0))
unreal.log("AUDIT ENTRADAS ok")
