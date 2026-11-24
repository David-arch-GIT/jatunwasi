# 481_ue_abrir_paso_convento.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: BUG BLOQUEANTE (previo): la pared invisible de contencion COL_PlazaWall_E_N (x=1400,
#   y -600..400) cruza el CAMINO AL CONVENTO (RUTA_CV sale de la plaza por la esquina NE, y~100..400):
#   el NavMesh tiene un corte de ~1.2 m y la locomocion del visitante se atasca -> no se puede llegar
#   caminando al Convento. Se ACORTA la pared a y -600..100 (abre 3 m justo donde pasa el camino;
#   el resto de la contencion queda igual) y se reconstruye el NavMesh.
#   STEP: "antes" (muestra NavMesh de todo el mapa) | "aplicar" (respaldo + pared + RebuildNavigation)
#         | "despues" (compara cobertura y valida caminos plaza->convento y plaza->hacienda)
import unreal, json, math, traceback, shutil
try:
    STEP
except NameError:
    STEP = "antes"
B = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
w = unreal.EditorLevelLibrary.get_editor_world()
res = {"step": STEP, "err": None}
def proj(x, y, z=150, e=(30, 30, 400)):
    r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(x, y, z), None, None, unreal.Vector(*e))
    return r[0] if isinstance(r, tuple) else r
def muestra():
    boxes = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name() == "NavMeshBoundsVolume":
            o, e = a.get_actor_bounds(False)
            if e.x > 50: boxes.append((o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
    pts = {}
    for (x0, x1, y0, y1) in boxes:
        for gx in range(int(x0 // 150), int(x1 // 150) + 1):
            for gy in range(int(y0 // 150), int(y1 // 150) + 1):
                k = "%d_%d" % (gx * 150, gy * 150)
                if k not in pts: pts[k] = proj(gx * 150 + 75, gy * 150 + 75) is not None
    return pts
try:
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    wall = acts["COL_PlazaWall_E_N"]
    if STEP == "antes":
        p = muestra(); open(B + "nav_antes_481.json", "w").write(json.dumps(p))
        res["n"] = len(p); res["validos"] = sum(1 for v in p.values() if v)
        o, e = wall.get_actor_bounds(False); res["pared"] = {"loc": str(wall.get_actor_location()), "escala": str(wall.get_actor_scale3d()), "y": [o.y - e.y, o.y + e.y]}
    elif STEP == "aplicar":
        # (v2) la pared esta girada (yaw 90): su LARGO es la escala X (10 = 1000 cm) y el grosor la Y (0.3).
        # Original: centro y=-100, escala (10, 0.3, 7) -> y -600..400. Nuevo: y -600..100 -> escala X 7, centro y=-250.
        S = wall.get_actor_scale3d(); L = wall.get_actor_location()
        wall.set_actor_scale3d(unreal.Vector(7.0, 0.3, S.z))
        wall.set_actor_location(unreal.Vector(1400.0, -250.0, L.z), False, False)
        res["rot"] = str(wall.get_actor_rotation())
        o2, e2 = wall.get_actor_bounds(False)
        res["pared_nueva_y"] = [round(o2.y - e2.y), round(o2.y + e2.y)]; res["pared_nueva_x"] = [round(o2.x - e2.x), round(o2.x + e2.x)]
        if "ACORTADA_481_paso_convento" not in [str(x) for x in wall.tags]: wall.tags = list(wall.tags) + ["ACORTADA_481_paso_convento"]
        unreal.SystemLibrary.execute_console_command(w, "RebuildNavigation")
        res["rebuild"] = "lanzado"
    elif STEP == "despues":
        antes = json.loads(open(B + "nav_antes_481.json").read()); desp = muestra()
        diff = [[k, antes.get(k), v] for k, v in desp.items() if antes.get(k) != v]
        res["n"] = len(desp); res["validos"] = sum(1 for v in desp.values() if v); res["diff_n"] = len(diff); res["diff"] = diff[:40]
        def camino(a, b):
            pa = proj(*a, e=(60, 60, 600)); pb = proj(*b, e=(60, 60, 600))
            p = unreal.NavigationSystemV1.find_path_to_location_synchronously(w, pa, pb)
            pts = p.get_editor_property("path_points") if p else []
            return {"n": len(pts), "fin": [round(pts[-1].x), round(pts[-1].y)] if pts else None, "completo": bool(pts) and math.hypot(pts[-1].x - pb.x, pts[-1].y - pb.y) < 60}
        res["plaza_a_barConv_oeste"] = camino((383, -950), (2063, 712))
        res["barConv_este_a_convento"] = camino((2309, 916), (5950, 4250))
        res["bajo_barConv"] = camino((2063, 712), (2309, 916))
        res["plaza_a_barHac_este"] = camino((383, -950), (-1490, -1000))
        res["bajo_barHac"] = camino((-1490, -1000), (-1810, -1000))
        res["barHac_oeste_a_hacienda"] = camino((-1810, -1000), (-7250, -820))
        res["plaza_a_templo"] = camino((383, -950), (50, 9550))
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(B + "paso_convento_%s.json" % STEP, "w").write(json.dumps(res))
