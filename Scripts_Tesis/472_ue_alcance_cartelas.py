# 472_ue_alcance_cartelas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) para cada cartela: distancia 3D MINIMA alcanzable entre la mano del visitante
#   (punto del NavMesh + 120 cm) y su posicion (Casa), barriendo una grilla de 25 cm en 8 m a la redonda.
#   El BP_Cartela abre solo si dist < 450 cm -> las que den >= 450 NUNCA se podrian abrir.
#   Tambien reporta la altura de la cartela sobre el piso navegable mas cercano.
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/alcance_cartelas.json"
res = {"err": None, "c": {}}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name() != "BP_Cartela_C": continue
        C = a.get_actor_location()
        best = None
        for i in range(-32, 33):
            for j in range(-32, 33):
                x = C.x + i * 25; y = C.y + j * 25
                r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, C.z), None, None, unreal.Vector(5, 5, 800))
                p = r[0] if isinstance(r, tuple) else r
                if p is None: continue
                d = math.dist([p.x, p.y, p.z + 120], [C.x, C.y, C.z])
                if best is None or d < best[0]: best = (d, p)
        res["c"][a.get_actor_label()] = {"loc": [round(C.x), round(C.y), round(C.z)],
            "dmin": round(best[0]) if best else None,
            "piso": [round(best[1].x), round(best[1].y), round(best[1].z)] if best else None,
            "altura_sobre_piso": round(C.z - best[1].z) if best else None}
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
