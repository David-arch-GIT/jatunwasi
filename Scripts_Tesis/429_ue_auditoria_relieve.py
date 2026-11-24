# 429_ue_auditoria_relieve.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) AUDITORIA de lo que el relieve (RLV_*, 420/421) afecto: para cada actor
#   del nivel que NO fue acomodado (no es vegetacion instanciada) calcula la altura del terreno nuevo
#   bajo su huella (centro + 4 esquinas de su caja, interpolacion bilineal de relieve_heights.json).
#   Si la loma pasa > 5 cm por encima de la base del actor -> el actor queda ENTERRADO/CORTADO.
#   Tambien revisa instancias de RELLENO_Campos que eran pircas (excluidas del acomodo).
import unreal, json, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/auditoria_relieve.json"
H = json.load(open(ROOT + "/Saved/ClaudeBackups/relieve_heights.json"))
X0, Y0, S, NX, NY, HH = H["x0"], H["y0"], H["step"], H["nx"], H["ny"], H["h"]
SNAPPED = ("JW_ENV_", "PCG_BosqueVol", "PCG_RelieveVol", "HACFOR_ISM_", "HORIZ_ISM_", "RELLENO_", "RLV_", "Ground_", "NOCHE_", "ENV_", "StarDome")
def hat(x, y):
    fx = (x - X0) / S; fy = (y - Y0) / S; i = int(fx // 1); j = int(fy // 1)
    if i < 0 or j < 0 or i >= NX - 1 or j >= NY - 1: return 0.0
    tx = fx - i; ty = fy - j
    a = HH[j][i] * (1 - tx) + HH[j][i + 1] * tx; b = HH[j + 1][i] * (1 - tx) + HH[j + 1][i + 1] * tx
    h = a * (1 - ty) + b * ty
    return h if h > 1.0 else 0.0
res = {"err": None, "afectados": []}
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        if lb.startswith(SNAPPED) or isinstance(a, (unreal.Volume, unreal.TriggerBase, unreal.Light, unreal.AmbientSound)):
            continue
        o, e = a.get_actor_bounds(True)
        if e.x <= 0 and e.y <= 0: continue
        if e.x > 6000 or e.y > 6000: continue
        base = o.z - e.z
        pts = [(o.x, o.y), (o.x - e.x, o.y - e.y), (o.x + e.x, o.y - e.y), (o.x - e.x, o.y + e.y), (o.x + e.x, o.y + e.y)]
        hs = [hat(x, y) for x, y in pts]
        terr = max(hs) - 5.0   # suelo nuevo (z del piso = -5 + h)
        if max(hs) > 5 and terr > base + 5:
            res["afectados"].append([lb, a.get_class().get_name(), [round(o.x), round(o.y)], round(base), round(max(hs)), [round(e.x), round(e.y), round(e.z)]])
    # pircas no acomodadas
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "RELLENO_Campos":
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                if c.static_mesh and "Fence" in c.static_mesh.get_name():
                    n = 0
                    for k in range(c.get_instance_count()):
                        t = c.get_instance_transform(k, True)
                        if hat(t.translation.x, t.translation.y) > 5: n += 1
                    res.setdefault("pircas_enterradas", 0); res["pircas_enterradas"] += n
    res["afectados"].sort(key=lambda r: -r[4])
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
