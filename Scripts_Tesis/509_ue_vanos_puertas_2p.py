# 509_ue_vanos_puertas_2p.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (solo lectura) localizar los VANOS DE PUERTA del 2do piso de la Hacienda (la usuaria ve
#   "muchas puertas" pero solo entra por la de la cortina). La Hacienda es monolitica y esta girada 12.1
#   grados en torno a (-7000,-2500). En coordenadas locales del edificio, por cada lx se halla el piso del
#   2do nivel (trazas verticales) y desde su centro se traza hacia ambos muros a z 470 (bajo un alfeizar)
#   y z 660 (sobre el dintel). Vano de puerta = a 470 el rayo llega mas lejos que a 660 (hueco) o choca
#   con la hoja (HACV7_EXP_Shutters). Salida: lista de vanos con centro, ancho, lado y que hay detras.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/vanos2p.json"
res = {"err": None}
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    O = (-7000.0, -2500.0); A = math.radians(12.1); c, s = math.cos(A), math.sin(A)
    def mundo(lx, ly, z): return unreal.Vector(O[0] + lx * c - ly * s, O[1] + lx * s + ly * c, z)
    def traza(p0, p1):
        h = unreal.SystemLibrary.line_trace_single(w, p0, p1, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [], unreal.DrawDebugTrace.NONE, True)  # complejo: respeta huecos
        t = h.to_tuple() if h else None
        if t and t[0]:
            return t[3], (t[9].get_actor_label() if t[9] else "?")
        return None, None
    muestras = []
    for lx in range(-2300, 2301, 20):
        # piso del 2do nivel
        piso = []
        for ly in range(-1800, 1801, 25):
            d, a = traza(mundo(lx, ly, 520), mundo(lx, ly, 380))
            if d is not None and 30 < d < 110:
                piso.append(ly)
        if not piso: continue
        # tramo continuo mas largo
        tr, cur = [], [piso[0]]
        for v in piso[1:]:
            if v - cur[-1] <= 25: cur.append(v)
            else: tr.append(cur); cur = [v]
        tr.append(cur)
        for t in tr:
            if len(t) < 6: continue
            yc = (t[0] + t[-1]) / 2.0
            fila = {"lx": lx, "yc": yc, "ancho_piso": t[-1] - t[0]}
            for lado, sg in (("N", 1), ("S", -1)):
                d1, a1 = traza(mundo(lx, yc, 470), mundo(lx, yc + sg * 1500, 470))
                d2, a2 = traza(mundo(lx, yc, 660), mundo(lx, yc + sg * 1500, 660))
                fila[lado] = [round(d1) if d1 else None, a1, round(d2) if d2 else None, a2]
            muestras.append(fila)
    res["muestras"] = len(muestras); res["filas"] = muestras
    # vanos: d470 > d660 + 15 (o d470 None con d660 valido) o golpe en Shutters
    vanos = []
    for lado in ("N", "S"):
        run = []
        for f in muestras:
            d1, a1, d2, a2 = f[lado]
            es = (d2 is not None) and ((d1 is None) or (d1 > d2 + 15) or (a1 == "HACV7_EXP_Shutters"))
            if es and (not run or f["lx"] - run[-1]["lx"] <= 40 and abs(f["yc"] - run[-1]["yc"]) < 200):
                run.append(f)
            else:
                if len(run) >= 3: vanos.append((lado, run))
                run = [f] if es else []
        if len(run) >= 3: vanos.append((lado, run))
    out = []
    for lado, run in vanos:
        lx0, lx1 = run[0]["lx"], run[-1]["lx"]; lxm = (lx0 + lx1) / 2.0
        f = run[len(run) // 2]; sg = 1 if lado == "N" else -1
        d2 = f[lado][2]
        P = mundo(lxm, f["yc"] + sg * d2, 530)
        out.append({"lado": lado, "lx": [lx0, lx1], "ancho": lx1 - lx0 + 20, "yc": f["yc"], "pared_d660": d2, "d470": f[lado][0], "golpe470": f[lado][1], "golpe660": f[lado][3],
                    "centro_mundo": [round(P.x), round(P.y), round(P.z)]})
    res["vanos"] = out
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))


