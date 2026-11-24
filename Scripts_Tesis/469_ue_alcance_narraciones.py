# 469_ue_alcance_narraciones.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) para cada punto de narracion (Narr_* / RELATO_*) comprobar si el visitante
#   PUEDE entrar a su esfera caminando: grilla de 25 cm dentro del radio, proyeccion al NavMesh (extent
#   pequeno) y distancia 3D entre el centro de la esfera y la capsula del pawn (piso + 90 cm). Reporta
#   la distancia minima alcanzable vs radio (+34 cm de capsula). Tambien la mejor posicion encontrada.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/alcance_narr.json"
res = {"err": None, "pts": {}}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        if not lb.startswith(("Narr_", "RELATO_")): continue
        sp = [c for c in a.get_components_by_class(unreal.SphereComponent)]
        if not sp: continue
        C = sp[0].get_world_location(); R = sp[0].get_scaled_sphere_radius()
        best = None
        st = 25
        n = int(R // st) + 1
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                x = C.x + i * st; y = C.y + j * st
                if math.hypot(x - C.x, y - C.y) > R + 40: continue
                r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, C.z), None, None, unreal.Vector(5, 5, 500))
                p = r[0] if isinstance(r, tuple) else r
                if p is None: continue
                d = math.dist([p.x, p.y, p.z + 90], [C.x, C.y, C.z])
                if best is None or d < best[0]:
                    best = (d, [round(p.x), round(p.y), round(p.z)])
        res["pts"][lb] = {"radio": round(R), "centro": [round(C.x), round(C.y), round(C.z)],
                          "dist_min": round(best[0]) if best else None, "mejor": best[1] if best else None,
                          "alcanzable": bool(best and best[0] < R + 34)}
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
