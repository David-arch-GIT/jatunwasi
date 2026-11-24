# 522_ue_auditoria_overdraw.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: (solo lectura) auditoria de sobredibujado para los senderos (visor: 33-52 FPS fuera de la
#   plaza, GPU 97 %, 98 % del tiempo en fragmentos). Por componente instanciado (ISM/HISM) y por actor
#   con material MASKED o TRANSLUCIDO: actor, malla, instancias, modo de mezcla, cull start/end, sombra.
#   Ordena por instancias para elegir recortes sin perdida visual (noche + niebla).
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/auditoria_overdraw.json"
res = {"err": None, "ism": [], "sma_mask": {}, "fog": None}
def modo(m):
    try:
        b = m.get_blend_mode() if hasattr(m, "get_blend_mode") else None
        if b is None:
            base = m.get_base_material() if hasattr(m, "get_base_material") else m
            b = base.get_editor_property("blend_mode")
        return str(b).split(".")[-1].split(":")[0].replace(">", "")
    except Exception:
        return "?"
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            n = c.get_instance_count()
            if n == 0 or not c.static_mesh: continue
            mats = [modo(m) for m in c.get_materials() if m]
            res["ism"].append([a.get_actor_label(), c.static_mesh.get_name(), n, mats, c.get_editor_property("instance_start_cull_distance"), c.get_editor_property("instance_end_cull_distance"), c.get_editor_property("cast_shadow"), c.is_visible()])
        if isinstance(a, unreal.StaticMeshActor):
            c = a.static_mesh_component
            if not c or not c.static_mesh or not c.is_visible() or a.is_hidden_ed(): continue
            mats = [modo(m) for m in c.get_materials() if m]
            if any(("MASKED" in x or "TRANSLUCENT" in x or "ADDITIVE" in x) for x in mats):
                k = (c.static_mesh.get_name(), str(mats))
                e = res["sma_mask"].setdefault(str(k), [0, c.get_editor_property("ld_max_draw_distance"), a.get_actor_label()])
                e[0] += 1
        if isinstance(a, unreal.ExponentialHeightFog):
            f = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
            res["fog"] = {p: str(f.get_editor_property(p)) for p in ("fog_density", "fog_height_falloff", "start_distance", "fog_max_opacity", "fog_cutoff_distance")}
    res["ism"].sort(key=lambda r: -r[2])
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
