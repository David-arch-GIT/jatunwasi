# 438_ue_plano_convento.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) PLANO de planta del convento a 1.5 m de altura: grilla de 50 cm; en cada
#   punto se prueba si hay muro (esfera de 8 cm que solapa geometria de arquitectura). Se combina con
#   el NavMesh y la posicion de los props existentes -> PNG del plano para decidir donde amoblar.
#   Tambien borra el muestrario temporal TMPKIT_* (437).
import unreal, json, traceback, zlib, struct
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plano_convento.json"
PNG = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plano_convento.png"
X0, X1, Y0, Y1, S = 4300, 8900, 3300, 6800, 50
res = {"err": None}
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("TMPKIT_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    world = unreal.EditorLevelLibrary.get_editor_world()
    nx = (X1 - X0) // S + 1; ny = (Y1 - Y0) // S + 1
    grid = []
    for j in range(ny):
        y = Y1 - j * S; row = []
        for i in range(nx):
            x = X0 + i * S
            h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x - 8, y, 150), unreal.Vector(x + 8, y, 150), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            h2 = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y - 8, 150), unreal.Vector(x, y + 8, 150), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
            wall = (h and h.to_tuple()[0]) or (h2 and h2.to_tuple()[0])
            p = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 50), None, None, unreal.Vector(30, 30, 120))
            p = p[0] if isinstance(p, tuple) else p
            row.append(2 if wall else (1 if p is not None and p.z < 250 else 0))
        grid.append(row)
    props = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        L = a.get_actor_location(); lb = a.get_actor_label()
        if X0 <= L.x <= X1 and Y0 <= L.y <= Y1 and lb.startswith(("CVT_", "VIT_", "CONV_Altar", "Cartela", "APL_", "PUERTA_", "RELATO", "CNVP")):
            props.append([lb, round(L.x), round(L.y)])
    res.update({"nx": nx, "ny": ny, "props": props})
    K = 4; rows = []
    pc = {}
    for lb, x, y in props:
        pc[((x - X0) // S, (Y1 - y) // S)] = lb
    for j in range(ny):
        line = bytearray()
        for i in range(nx):
            v = grid[j][i]
            c = (40, 40, 40) if v == 0 else ((200, 190, 160) if v == 1 else (180, 40, 40))
            if (i, j) in pc: c = (40, 120, 255)
            if i % 20 == 0 or j % 20 == 0: c = tuple(min(255, k + 40) for k in c)   # lineas cada 10 m
            line += bytes(c) * K
        for _ in range(K): rows.append(b"\x00" + bytes(line))
    raw = b"".join(rows)
    def ch(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(PNG, "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", nx * K, ny * K, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw, 9)) + ch(b"IEND", b""))
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
