# 510_ue_hojas_puerta_2p.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (solo lectura) ubicar las HOJAS DE PUERTA del 2do piso de la Hacienda (malla monolitica
#   HACV7_EXP_Shutters, madera clara) y los VANOS visuales de ExteriorWalls_Upper, con trazas contra la
#   geometria compleja de cada componente (line_trace_component), en una rejilla a z=470 (altura de
#   puerta, bajo los alfeizares). Agrupa los impactos en hojas/vanos con centro, ancho y orientacion.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hojas2p.json"
res = {"err": None}
try:
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    O = (-7000.0, -2500.0); A = math.radians(12.1); c, s = math.cos(A), math.sin(A)
    def mundo(lx, ly, z): return unreal.Vector(O[0] + lx * c - ly * s, O[1] + lx * s + ly * c, z)
    def local(p): dx, dy = p.x - O[0], p.y - O[1]; return (dx * c + dy * s, -dx * s + dy * c)
    def golpes(comp, z, paso=25):
        pts = []
        for lx in range(-2400, 2401, paso):          # rayos en Y local, por tramos de 200 (varios impactos)
            for y0 in range(-2000, 2000, 200):
                r = comp.line_trace_component(mundo(lx, y0, z), mundo(lx, y0 + 200, z), True, False, False)
                if r and r[0]: pts.append(("y", lx, local(r[1])))
        for ly in range(-2000, 2001, paso):          # rayos en X local
            for x0 in range(-2400, 2400, 200):
                r = comp.line_trace_component(mundo(x0, ly, z), mundo(x0 + 200, ly, z), True, False, False)
                if r and r[0]: pts.append(("x", ly, local(r[1])))
        return pts
    sh = acts["HACV7_EXP_Shutters"].get_component_by_class(unreal.StaticMeshComponent)
    res["probe_ret"] = str(sh.line_trace_component(mundo(0, -2000, 470), mundo(0, 2000, 470), True, False, False))[:300]
    out = {}
    for z in (470, 560):
        p = golpes(sh, z)
        out[str(z)] = [[d, k, round(q[0]), round(q[1])] for (d, k, q) in p]
    res["shutters"] = out
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))

