# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) (1) Quita colisiones a los tapetes/alfombras de la hacienda. (2) Mide que le queda pesado a la plaza
#   (mallas por tris del LOD renderizado, foliage, luces, materiales masked/translucent = overdraw). (3) Revisa niebla.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza2.json"
res = {"tapetes_sin_colision": [], "plaza_lights": 0, "plaza_foliage_inst": 0, "plaza_top_sm": [], "fog": None, "err": []}
eas = unreal.EditorActorSubsystem()
CX, CY, R = 0.0, -1000.0, 5000.0
# (1) tapetes: quitar colision (en toda la hacienda / mapa)
rug_kw = ["tapete", "alfombra", "rug", "carpet", "mat_", "_mat", "kilim", "estera"]
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label(); low = lbl.lower()
    if any(k in low for k in rug_kw):
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
                res["tapetes_sin_colision"].append(lbl)
            except Exception as e:
                res["err"].append("%s: %s" % (lbl, str(e)[:40]))
# (2) plaza: medir
sm_tris = []
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x - CX, loc.y - CY) > R:
        continue
    for lc in a.get_components_by_class(unreal.LightComponent):
        if lc.get_class().get_name() in ("PointLightComponent", "SpotLightComponent"):
            if lc.is_visible():
                res["plaza_lights"] += 1
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        res["plaza_foliage_inst"] += comp.get_instance_count()
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        if comp.get_class().get_name() in ("InstancedStaticMeshComponent", "HierarchicalInstancedStaticMeshComponent"):
            continue
        m = comp.get_editor_property("static_mesh")
        if not m:
            continue
        try:
            ml = comp.get_editor_property("min_lod") if comp.get_editor_property("override_min_lod") else 0
        except Exception:
            ml = 0
        try:
            tr = m.get_num_triangles(int(ml))
        except Exception:
            tr = 0
        sm_tris.append((a.get_actor_label(), tr))
sm_tris.sort(key=lambda t: -t[1])
res["plaza_top_sm"] = sm_tris[:15]
# (3) niebla
for a in eas.get_all_level_actors():
    if "ExponentialHeightFog" in a.get_class().get_name():
        fc = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if fc:
            try:
                res["fog"] = {"density": float(fc.get_editor_property("fog_density")), "start": float(fc.get_editor_property("start_distance"))}
            except Exception as e:
                res["err"].append("fog: %s" % e)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA2 tapetes=%d luces=%d foliage=%d" % (len(res["tapetes_sin_colision"]), res["plaza_lights"], res["plaza_foliage_inst"]))
