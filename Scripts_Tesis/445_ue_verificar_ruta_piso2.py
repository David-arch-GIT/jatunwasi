# 445_ue_verificar_ruta_piso2.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) verificar que el 2do piso de la hacienda quedo CONECTADO: camino completo
#   (no parcial) desde la entrada de la hacienda, desde el patio y desde el pie de la escalera hasta el
#   centro de la Sala de Baile (y hasta el corredor alto); perfil de NavMesh en la rampa y el descanso.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ruta_piso2.json"
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    goals = {"salon": (-8375, -1600, 430), "corredor": (-6500, -1600, 432)}
    starts = {"entrada": (-7317, -1100, 60), "patio": (-7050, -2300, 60), "pie_escalera": (-7448, -3000, 60)}
    for gn, g in goals.items():
        for sn, s in starts.items():
            p = unreal.NavigationSystemV1.find_path_to_location_synchronously(world, unreal.Vector(*s), unreal.Vector(*g))
            pts = list(p.get_editor_property("path_points")) if p else []
            res[sn + "->" + gn] = {"parcial": p.is_partial() if p else None, "fin": [round(pts[-1].x), round(pts[-1].y), round(pts[-1].z)] if pts else None,
                                   "len_m": round(sum(((pts[i+1].x-pts[i].x)**2 + (pts[i+1].y-pts[i].y)**2 + (pts[i+1].z-pts[i].z)**2) ** 0.5 for i in range(len(pts)-1)) / 100, 1) if pts else None}
    prof = []
    for k in range(0, 31):
        y = -2600 + k * 25
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(-7448, y, 600), None, None, unreal.Vector(30, 30, 700))
        q = r[0] if isinstance(r, tuple) else r
        prof.append([y, round(q.z) if q else None])
    res["perfil"] = prof
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
