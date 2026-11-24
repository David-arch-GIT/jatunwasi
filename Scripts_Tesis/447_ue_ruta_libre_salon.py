# 447_ue_ruta_libre_salon.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) encontrar si existe un paso REAL con holgura entre el corredor alto y la
#   Sala de Baile: grilla de 10 cm (muro = traza corta a 70 cm sobre el piso; libre = NavMesh), se
#   engordan los muros 20 cm y se busca camino (BFS 8-vecinos) de (-7600,-1925) a (-8375,-1600).
#   Devuelve la ruta simplificada (puntos de giro) y el mapa ASCII con la ruta marcada.
import unreal, json, math, traceback
from collections import deque
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ruta_libre.json"
X0, X1, Y0, Y1, S = -8550, -7550, -2100, -1450, 10
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    nx = (X1 - X0) // S + 1; ny = (Y1 - Y0) // S + 1
    wall = [[False] * nx for _ in range(ny)]; free = [[False] * nx for _ in range(ny)]
    for j in range(ny):
        y = Y0 + j * S
        for i in range(nx):
            x = X0 + i * S
            h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x - 5, y, 500), unreal.Vector(x + 5, y, 500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            h2 = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y - 5, 500), unreal.Vector(x, y + 5, 500), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            wall[j][i] = bool((h and h.to_tuple()[0]) or (h2 and h2.to_tuple()[0]))
            r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 435), None, None, unreal.Vector(5, 5, 30))
            p = r[0] if isinstance(r, tuple) else r
            free[j][i] = p is not None
    R = 2  # 20 cm de holgura
    ok = [[free[j][i] and not any(wall[jj][ii] for jj in range(max(0, j - R), min(ny, j + R + 1)) for ii in range(max(0, i - R), min(nx, i + R + 1))) for i in range(nx)] for j in range(ny)]
    def cell(x, y): return (int(round((y - Y0) / S)), int(round((x - X0) / S)))
    s = cell(-7600, -1925); g = cell(-8375, -1600)
    prev = {s: None}; q = deque([s])
    while q:
        c = q.popleft()
        if c == g: break
        for dj in (-1, 0, 1):
            for di in (-1, 0, 1):
                n = (c[0] + dj, c[1] + di)
                if (dj or di) and 0 <= n[0] < ny and 0 <= n[1] < nx and ok[n[0]][n[1]] and n not in prev:
                    prev[n] = c; q.append(n)
    route = []
    if g in prev:
        c = g
        while c: route.append(c); c = prev[c]
        route.reverse()
    res["ok_start"] = ok[s[0]][s[1]]; res["ok_goal"] = ok[g[0]][g[1]]
    res["hay_ruta"] = bool(route)
    pts = [[X0 + c[1] * S, Y0 + c[0] * S] for c in route]
    simp = pts[:1]
    for k in range(1, len(pts) - 1):
        a, b, c2 = pts[k - 1], pts[k], pts[k + 1]
        if (b[0] - a[0], b[1] - a[1]) != (c2[0] - b[0], c2[1] - b[1]): simp.append(b)
    if pts: simp.append(pts[-1])
    res["ruta"] = simp
    rs = set(route); rows = []
    for j in range(ny - 1, -1, -1):
        rows.append("%6d " % (Y0 + j * S) + "".join("o" if (j, i) in rs else ("#" if wall[j][i] else ("." if ok[j][i] else (":" if free[j][i] else " "))) for i in range(nx)))
    res["mapa"] = rows
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
