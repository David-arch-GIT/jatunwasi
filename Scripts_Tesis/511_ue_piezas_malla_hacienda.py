# 511_ue_piezas_malla_hacienda.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (solo lectura) separar en PIEZAS la malla monolitica HACV7_EXP_Shutters (hojas de puerta y
#   postigos, madera clara) leyendo sus vertices (ProceduralMeshLibrary.get_section_from_static_mesh) y
#   uniendo triangulos que comparten vertices. Por pieza: caja en coordenadas del actor (sin girar) y en
#   mundo. Las PUERTAS del 2do piso = piezas altas (>170 cm) cuyo pie esta cerca del piso alto (z mundo ~430).
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/piezas_shutters.json"
try:
    MALLA
except NameError:
    MALLA = "HACV7_EXP_Shutters"
res = {"err": None, "malla": MALLA}
try:
    act = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == MALLA][0]
    smc = act.get_component_by_class(unreal.StaticMeshComponent); sm = smc.static_mesh
    T = act.get_actor_transform()
    piezas = []
    ns = sm.get_num_sections(0); res["secciones"] = ns
    for si in range(ns):
        r = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, si)
        V, Tr = r[0], r[1]
        n = len(V)
        par = list(range(n))
        def f(i):
            while par[i] != i:
                par[i] = par[par[i]]; i = par[i]
            return i
        # soldar vertices coincidentes (las costuras de UV duplican vertices)
        clave = {}
        for i, v in enumerate(V):
            k = (round(v.x), round(v.y), round(v.z))
            if k in clave:
                a, b = f(i), f(clave[k])
                if a != b: par[a] = b
            else:
                clave[k] = i
        for t in range(0, len(Tr), 3):
            a, b, c = f(Tr[t]), f(Tr[t + 1]), f(Tr[t + 2])
            if a != b: par[a] = b
            b = f(b)
            if c != b: par[c] = b
        grupos = {}
        for i, v in enumerate(V):
            g = f(i)
            bb = grupos.get(g)
            if bb is None: grupos[g] = [v.x, v.y, v.z, v.x, v.y, v.z, 1]
            else:
                bb[0] = min(bb[0], v.x); bb[1] = min(bb[1], v.y); bb[2] = min(bb[2], v.z)
                bb[3] = max(bb[3], v.x); bb[4] = max(bb[4], v.y); bb[5] = max(bb[5], v.z); bb[6] += 1
        for g, bb in grupos.items():
            cl = unreal.Vector((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
            cw = T.transform_location(cl)
            piezas.append({"sec": si, "loc_min": [round(bb[0]), round(bb[1]), round(bb[2])], "loc_max": [round(bb[3]), round(bb[4]), round(bb[5])],
                           "dim": [round(bb[3] - bb[0]), round(bb[4] - bb[1]), round(bb[5] - bb[2])], "centro_mundo": [round(cw.x), round(cw.y), round(cw.z)],
                           "zmin_mundo": round(T.transform_location(unreal.Vector(cl.x, cl.y, bb[2])).z), "nv": bb[6]})
    res["n_piezas"] = len(piezas)
    piezas.sort(key=lambda p: (p["zmin_mundo"], p["centro_mundo"][0]))
    res["piezas"] = piezas
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
