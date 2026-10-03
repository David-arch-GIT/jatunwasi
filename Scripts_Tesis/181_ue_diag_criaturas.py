# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) DIAGNOSTICO de las 3 criaturas (duende/condenado/karisiri/aparicion/app3d). Por cada actor:
#   clase, ubicacion, si tiene SkeletalMeshComponent (rig) o StaticMesh, huesos, anim_class/anim asignada, tris.
#   Ademas: hay NavMeshBoundsVolume y RecastNavMesh en el nivel? (necesario para IA de movimiento). Solo lee.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_criaturas.json"
res = {"criaturas": [], "navmesh_volumes": 0, "recast_navmesh": 0, "nav_bounds_info": [], "err": []}
eas = unreal.EditorActorSubsystem()
KEY = ["duende", "condenado", "karisiri", "aparicion", "apparition", "app3d", "criatura"]
def describe(a):
    lab = a.get_actor_label()
    loc = a.get_actor_location()
    d = {"label": lab, "clase": a.get_class().get_name(), "loc": [round(loc.x), round(loc.y), round(loc.z)], "skeletal": None, "static": None, "components": []}
    # skeletal
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        info = {"comp": c.get_name()}
        try:
            sk = c.get_editor_property("skeletal_mesh") if hasattr(c, "get_editor_property") else None
            if not sk:
                try: sk = c.get_skeletal_mesh_asset()
                except Exception: sk = None
            if sk:
                info["mesh"] = sk.get_name()
                try: info["bones"] = len(sk.get_editor_property("skeleton").get_editor_property("bone_tree")) if sk.get_editor_property("skeleton") else "?"
                except Exception: info["bones"] = "?"
        except Exception as e:
            info["err"] = str(e)[:30]
        try:
            ac = c.get_editor_property("anim_class")
            info["anim_class"] = ac.get_name() if ac else "NINGUNA"
        except Exception: pass
        try:
            am = c.get_editor_property("animation_data")
            info["anim_mode"] = str(c.get_editor_property("animation_mode"))
        except Exception: pass
        d["skeletal"] = info
    # static
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        m = c.get_editor_property("static_mesh")
        if m:
            d["static"] = {"mesh": m.get_name(), "tris": int(m.get_num_triangles(0))}
    # lista de tipos de componentes (para ver si hay movement/AI)
    try:
        for c in a.get_components_by_class(unreal.ActorComponent):
            d["components"].append(c.get_class().get_name())
    except Exception: pass
    d["components"] = list(set(d["components"]))
    return d
for a in eas.get_all_level_actors():
    lab = a.get_actor_label().lower()
    cls = a.get_class().get_name()
    if any(k in lab for k in KEY):
        res["criaturas"].append(describe(a))
    if "NavMeshBoundsVolume" in cls:
        res["navmesh_volumes"] += 1
        loc = a.get_actor_location()
        org, ext = a.get_actor_bounds(False)
        res["nav_bounds_info"].append({"label": a.get_actor_label()[:20], "centro": [round(org.x), round(org.y), round(org.z)], "ext": [round(ext.x), round(ext.y), round(ext.z)]})
    if "RecastNavMesh" in cls or "NavMesh" in cls:
        res["recast_navmesh"] += 1
res["n_criaturas"] = len(res["criaturas"])
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("DIAG CRIATURAS n=%d navvol=%d" % (len(res["criaturas"]), res["navmesh_volumes"]))
