# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) SOLO LECTURA. Mide lo que le queda PESADO a la plaza tras adelgazar: mallas estaticas (no-instancia)
#   con sus triangulos, luces, y foliage restante. Para atacar el cuello real de fluidez.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_resto.json"
CX, CY, R = 0.0, -1000.0, 5000.0
res = {"lights": 0, "sm_actors": 0, "sm_top_tris": [], "foliage_inst": 0, "foliage_comps": 0, "materiales_unicos": 0}
eas = unreal.EditorActorSubsystem()
sms = []
mats = set()
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x - CX, loc.y - CY) > R:
        continue
    for lc in a.get_components_by_class(unreal.LightComponent):
        if lc.get_class().get_name() in ("PointLightComponent", "SpotLightComponent"):
            res["lights"] += 1
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        n = comp.get_instance_count()
        if n > 0:
            res["foliage_inst"] += n; res["foliage_comps"] += 1
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        if comp.get_class().get_name() in ("InstancedStaticMeshComponent", "HierarchicalInstancedStaticMeshComponent"):
            continue
        m = comp.get_editor_property("static_mesh")
        if m is None:
            continue
        res["sm_actors"] += 1
        try:
            tris = m.get_num_triangles(0) if hasattr(m, "get_num_triangles") else 0
        except Exception:
            tris = 0
        sms.append((a.get_actor_label(), tris))
        for mi in comp.get_materials():
            if mi:
                mats.add(mi.get_name())
sms.sort(key=lambda t: -t[1])
res["sm_top_tris"] = sms[:20]
res["materiales_unicos"] = len(mats)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA RESTO lights=%d sm=%d foliage=%d mats=%d" % (res["lights"], res["sm_actors"], res["foliage_inst"], res["materiales_unicos"]))
