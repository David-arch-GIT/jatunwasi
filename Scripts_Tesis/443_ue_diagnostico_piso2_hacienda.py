# 443_ue_diagnostico_piso2_hacienda.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) diagnosticar por que el visitante sube la escalera de la hacienda pero NO
#   puede entrar al 2do piso (Sala de Baile). Reporta:
#   - caja/rotacion de la escalera y de la rampa de colision
#   - perfil del NavMesh a lo largo de la rampa (z) completo
#   - mapa del NavMesh del 2do piso (z 380-480) en grilla de 50 cm -> PNG
#   - actores con colision (COL_*, muros) en z>250 dentro de la hacienda
import unreal, json, math, traceback, zlib, struct
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/piso2_diag.json"
PNG = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/piso2_nav.png"
X0, X1, Y0, Y1, S = -9300, -4900, -4100, -500, 50
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
    def info(a):
        o, e = a.get_actor_bounds(False); r = a.get_actor_rotation(); L = a.get_actor_location(); s = a.get_actor_scale3d()
        c = a.get_component_by_class(unreal.PrimitiveComponent)
        return {"loc": [round(L.x), round(L.y), round(L.z)], "rot": [round(r.pitch, 1), round(r.yaw, 1), round(r.roll, 1)], "scale": [round(s.x, 2), round(s.y, 2), round(s.z, 2)],
                "bmin": [round(o.x - e.x), round(o.y - e.y), round(o.z - e.z)], "bmax": [round(o.x + e.x), round(o.y + e.y), round(o.z + e.z)],
                "coll": str(c.get_collision_enabled()) if c else None, "nav": c.get_editor_property("can_ever_affect_navigation") if c else None,
                "mesh": (c.static_mesh.get_name() if isinstance(c, unreal.StaticMeshComponent) and c.static_mesh else None)}
    res["escalera"] = {a.get_actor_label(): info(a) for a in acts if a.get_actor_label() in ("HACV7_EXP_Staircase", "COL_HACV7_StairRamp", "COL_Baile_navfloor")}
    cols = []
    for a in acts:
        o, e = a.get_actor_bounds(False)
        if X0 <= o.x <= X1 and Y0 <= o.y <= Y1 and o.z + e.z > 250 and (a.get_actor_label().startswith(("COL_", "BAR_", "HACV7_", "INV_", "BLOCK", "Block")) or "COL" in a.get_actor_label()):
            cols.append([a.get_actor_label(), info(a)])
    res["colisiones_altas"] = cols
    # perfil de nav a lo largo de la rampa extendida
    ramp = [a for a in acts if a.get_actor_label() == "COL_HACV7_StairRamp"][0]
    o, e = ramp.get_actor_bounds(False)
    prof = []
    for k in range(0, 41):
        t = k / 40.0
        x = (o.x - e.x) + 2 * e.x * t; y = (o.y - e.y) + 2 * e.y * t
        for (xx, yy) in ((x, o.y), (o.x, y)):
            pass
    # perfil a lo largo del eje mayor de la caja de la rampa
    ax = "x" if e.x > e.y else "y"
    for k in range(0, 41):
        t = -1 + 2 * k / 40.0
        x = o.x + (e.x * t if ax == "x" else 0); y = o.y + (e.y * t if ax == "y" else 0)
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 600), None, None, unreal.Vector(30, 30, 700))
        p = r[0] if isinstance(r, tuple) else r
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 900), unreal.Vector(x, y, -50), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)
        tt = h.to_tuple() if h else None
        prof.append([round(x), round(y), round(p.z) if p else None, round(tt[4].z) if tt and tt[0] else None, (tt[10].get_owner().get_actor_label() if tt and tt[0] and tt[10] else None)])
    res["perfil_rampa"] = prof
    # mapa nav 2do piso
    nx = (X1 - X0) // S + 1; ny = (Y1 - Y0) // S + 1; grid = []
    for j in range(ny):
        y = Y1 - j * S; row = []
        for i in range(nx):
            x = X0 + i * S
            r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 430), None, None, unreal.Vector(25, 25, 60))
            p = r[0] if isinstance(r, tuple) else r
            row.append(0 if p is None else (2 if p.z > 300 else 1))
        grid.append(row)
    K = 3; rows = []
    for j in range(ny):
        line = bytearray()
        for i in range(nx):
            v = grid[j][i]; c = (30, 30, 30) if v == 0 else ((90, 90, 90) if v == 1 else (230, 200, 60))
            if i % 20 == 0 or j % 20 == 0: c = tuple(min(255, q + 35) for q in c)
            line += bytes(c) * K
        for _ in range(K): rows.append(b"\x00" + bytes(line))
    def ch(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(PNG, "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", nx * K, ny * K, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(b"".join(rows), 9)) + ch(b"IEND", b""))
    res["piso2_celdas"] = sum(r.count(2) for r in grid)
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
