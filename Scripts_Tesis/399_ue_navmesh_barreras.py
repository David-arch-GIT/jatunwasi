# 399_ue_navmesh_barreras.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: preparar movimiento fluido. Las barreras BAR_Convento/BAR_Hacienda recortan
#   el NavMesh (estatico): al abrirse en juego el hueco NO se rellena y el jugador quedaria
#   atascado. Se quita can_ever_affect_navigation de las barreras (el bloqueo mientras
#   esten cerradas lo hace el trazo de colision del movimiento) y se compara la
#   cobertura del NavMesh antes/despues para verificar que solo cambia en las barreras.
# Uso: STEP = "sample_before" | "apply" | "sample_after"
import unreal, json, traceback
try:
    STEP
except NameError:
    STEP = "sample_before"
B = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"step": STEP, "err": None}

def proj(x, y):
    r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 150), None, None,
                                                              unreal.Vector(30, 30, 400))
    loc = r[0] if isinstance(r, tuple) else r
    return loc is not None

def sample():
    boxes = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_class().get_name() == "NavMeshBoundsVolume":
            o, e = a.get_actor_bounds(False)
            if e.x > 50:
                boxes.append((o.x - e.x, o.x + e.x, o.y - e.y, o.y + e.y))
    pts = {}
    for (x0, x1, y0, y1) in boxes:
        x = x0
        while x <= x1:
            y = y0
            while y <= y1:
                k = "%d_%d" % (int(x // 300) * 300, int(y // 300) * 300)
                if k not in pts:
                    pts[k] = proj(int(x // 300) * 300 + 150, int(y // 300) * 300 + 150)
                y += 300
            x += 300
    return pts

try:
    if STEP == "sample_before":
        pts = sample(); open(B + "nav_before.json", "w").write(json.dumps(pts))
        res["n"] = len(pts); res["valid"] = sum(1 for v in pts.values() if v)
    elif STEP == "apply":
        for a in unreal.EditorLevelLibrary.get_all_level_actors():
            if a.get_actor_label() in ("BAR_Convento", "BAR_Hacienda"):
                for c in a.get_components_by_class(unreal.PrimitiveComponent):
                    c.set_editor_property("can_ever_affect_navigation", False)
                res.setdefault("done", []).append(a.get_actor_label())
    elif STEP == "sample_after":
        before = json.loads(open(B + "nav_before.json").read())
        after = sample()
        diff = [[k, before.get(k), v] for k, v in after.items() if before.get(k) != v]
        res["n"] = len(after); res["valid"] = sum(1 for v in after.values() if v)
        res["diff_count"] = len(diff); res["diff"] = diff[:60]
        res["barrier_ok"] = {"BAR_Convento": proj(2186, 814), "BAR_Hacienda": proj(-1650, -1000)}
except Exception:
    res["err"] = traceback.format_exc()[:600]
open(B + "nav_step.json", "w").write(json.dumps(res, indent=1))
