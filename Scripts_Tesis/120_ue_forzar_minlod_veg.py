# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Fuerza un MinLOD mas liviano en la vegetacion de LOD0 altisimo (Hydrangea 65k, Boxwood 44k, etc.).
#   Las plantas cercanas dejan de renderizar el LOD0 carisimo y usan un LOD mucho mas barato (casi igual en Quest).
#   Gran ahorro de vertices/GPU sin cambiar el look apreciablemente. Guarda. Reporta.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/minlod_veg.json"
res = {"comps_ajustados": 0, "detalle": [], "err": []}
eas = unreal.EditorActorSubsystem()
cache = {}  # mesh_name -> (lod0_tris, num_lods)
def mesh_info(m):
    nm = m.get_name()
    if nm in cache:
        return cache[nm]
    try:
        t = m.get_num_triangles(0)
    except Exception:
        t = 0
    try:
        l = m.get_num_lods()
    except Exception:
        try:
            l = m.get_num_l_o_ds()
        except Exception:
            l = 1
    cache[nm] = (t, l)
    return cache[nm]
for a in eas.get_all_level_actors():
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m:
                continue
            t0, nl = mesh_info(m)
            if nl >= 3 and t0 > 8000:
                # forzar LOD2 (o el mas bajo disponible si hay pocos)
                target = 2 if nl > 3 else 1
                comp.set_editor_property("override_min_lod", True)
                comp.set_editor_property("min_lod", target)
                res["comps_ajustados"] += 1
                if len(res["detalle"]) < 20:
                    res["detalle"].append([a.get_actor_label(), m.get_name(), t0, "minlod->%d" % target])
        except Exception as ex:
            res["err"].append(str(ex)[:60])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MINLOD VEG comps=%d" % res["comps_ajustados"])
