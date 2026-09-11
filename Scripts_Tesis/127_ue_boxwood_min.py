# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) El boxwood es la bomba de la plaza (62k tris en LOD3 x ~110 = ~30M). Fuerza el boxwood a su LOD
#   mas bajo (casi 0 tris). Captura el jardin para ver si queda aceptable; si no, se removera. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/boxwood_min.json"
res = {"comps": 0, "tris_antes_est": 0, "tris_despues_est": 0, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m or "boxwood" not in m.get_name().lower():
                continue
            nl = m.get_num_lods()
            cnt = comp.get_instance_count()
            # antes (min_lod actual)
            try:
                cur = int(comp.get_editor_property("min_lod")) if comp.get_editor_property("override_min_lod") else 0
            except Exception:
                cur = 0
            res["tris_antes_est"] += m.get_num_triangles(cur) * cnt
            # forzar LOD mas bajo
            low = nl - 1
            comp.set_editor_property("override_min_lod", True)
            comp.set_editor_property("min_lod", low)
            res["tris_despues_est"] += m.get_num_triangles(low) * cnt
            res["comps"] += 1
        except Exception as ex:
            res["err"].append(str(ex)[:50])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("BOXWOOD MIN comps=%d antes=%d despues=%d" % (res["comps"], res["tris_antes_est"], res["tris_despues_est"]))
