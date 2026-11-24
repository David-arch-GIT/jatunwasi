# 431_ue_auditoria_relieve_malla.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) auditoria REAL de la malla del relieve (429 solo leia el mapa de alturas y
#   no detecto el espejo norte-sur). Lanza rayos verticales SOLO contra los RLV_* :
#   (a) 900 puntos dentro de los discos del pueblo (plaza/templo/convento/hacienda): ningun RLV debe
#       estar por encima de -4 cm;
#   (b) 600 puntos al azar en el bosque: la z del RLV debe coincidir con -5 + h(x,y) (+-3 cm).
import unreal, json, math, random, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/auditoria_malla.json"
H = json.load(open(ROOT + "/Saved/ClaudeBackups/relieve_heights.json"))
X0, Y0, S, NX, NY, HH = H["x0"], H["y0"], H["step"], H["nx"], H["ny"], H["h"]
def hat(x, y):
    fx = (x - X0) / S; fy = (y - Y0) / S; i = int(fx // 1); j = int(fy // 1)
    if i < 0 or j < 0 or i >= NX - 1 or j >= NY - 1: return 0.0
    tx = fx - i; ty = fy - j
    a = HH[j][i] * (1 - tx) + HH[j][i + 1] * tx; b = HH[j + 1][i] * (1 - tx) + HH[j + 1][i + 1] * tx
    return a * (1 - ty) + b * ty
res = {"err": None}
try:
    rlv = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label().startswith("RLV_")]
    others = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if not a.get_actor_label().startswith("RLV_")]
    world = unreal.EditorLevelLibrary.get_editor_world()
    def rlv_z(x, y):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 600), unreal.Vector(x, y, -100), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, others, unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        t = h.to_tuple(); return t[4].z if t[0] else None
    random.seed(431); bad_town = []; n = 0
    for cx, cy, r in ((0, -1000, 3600), (0, 11500, 2600), (6000, 4800, 3200), (-7000, -2300, 3400)):
        for k in range(225):
            a = random.uniform(0, 6.283); d = r * math.sqrt(random.random())
            x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
            z = rlv_z(x, y); n += 1
            if z is not None and z > -4.5:
                bad_town.append([round(x), round(y), round(z, 1)])
    res["town_samples"] = n; res["town_bad"] = len(bad_town); res["town_bad_ej"] = bad_town[:15]
    errs = []; m = 0
    while m < 600:
        x = random.uniform(-13000, 14000); y = random.uniform(-12500, 19000)
        if hat(x, y) < 20: continue
        z = rlv_z(x, y)
        if z is None: continue
        m += 1; errs.append(abs(z - (-5 + hat(x, y))))
    errs.sort()
    res["forest_samples"] = m; res["forest_err_median_cm"] = round(errs[len(errs) // 2], 2); res["forest_err_p95_cm"] = round(errs[int(len(errs) * 0.95)], 2); res["forest_err_max_cm"] = round(errs[-1], 2)
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
