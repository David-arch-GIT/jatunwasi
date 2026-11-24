# 407_ue_inventario_sonidos_noche.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: INVENTARIO (solo lectura) previo a colocar los sonidos nocturnos: posiciones de
#   RELLENO_Campos (para grillos), torres/campanario del Templo (campanas), limites de los
#   NavMeshBoundsVolume (borde del bosque para la lechuza), PlayerStart, BP_GestorRecorrido y
#   sonidos ambiente existentes (AMB_*). No modifica nada.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inv_sonidos.json"
res = {"err": None}
try:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
    res["torres"] = []; res["amb"] = []; res["nav"] = []; res["misc"] = []
    for a in acts:
        lb = a.get_actor_label(); L = a.get_actor_location()
        p = [round(L.x), round(L.y), round(L.z)]
        low = lb.lower()
        if any(k in low for k in ("torre", "campan", "tower", "bell", "cupula", "templo")):
            o, e = a.get_actor_bounds(False)
            res["torres"].append([lb, p, [round(o.x), round(o.y), round(o.z)], [round(e.x), round(e.y), round(e.z)]])
        if isinstance(a, unreal.AmbientSound) or lb.startswith("AMB_"):
            res["amb"].append([lb, p])
        if isinstance(a, unreal.NavMeshBoundsVolume):
            o, e = a.get_actor_bounds(False)
            res["nav"].append([round(o.x), round(o.y), round(e.x), round(e.y)])
        if lb in ("RELLENO_Campos", "RELLENO_Horizonte", "PlayerStart") or "Gestor" in lb or lb.startswith("RELATO_") or lb.startswith("Trig"):
            res["misc"].append([lb, p])
        if lb == "RELLENO_Campos":
            pts = []
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                n = c.get_instance_count()
                for i in range(0, n, max(1, n // 300)):
                    t = c.get_instance_transform(i, True); pts.append([round(t.translation.x), round(t.translation.y), round(t.translation.z)])
            res["campos_pts"] = pts
    res["torres"] = res["torres"][:60]
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res))
