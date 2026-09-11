# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Remata la plaza: quita instancias de boxwood que siguen pesadas (LOD renderizado >5000 tris, no bajan mas)
#   y adelgaza el pasto 40%. Baja la plaza a ~3.5M. El jardin conserva flores + boxwood liviano. Guarda.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_remate.json"
CX, CY, R = 0.0, -1000.0, 6000.0
res = {"boxwood_quitado": 0, "grass_quitado": 0, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x-CX, loc.y-CY) > R:
        continue
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            m = comp.get_editor_property("static_mesh")
            if not m: continue
            low = m.get_name().lower()
            cnt = comp.get_instance_count()
            if cnt < 4: continue
            # boxwood pesado que no baja mas de LOD -> quitar todas
            if "boxwood" in low:
                try:
                    ml = int(comp.get_editor_property("min_lod")) if comp.get_editor_property("override_min_lod") else 0
                except Exception:
                    ml = 0
                if m.get_num_triangles(ml) > 5000:
                    comp.remove_instances(list(range(cnt)))
                    res["boxwood_quitado"] += cnt
            # pasto: adelgazar 40%
            elif "grass" in low or "pasto" in low:
                rem = [i for i in range(cnt) if (i % 100) >= 60]
                if rem:
                    comp.remove_instances(rem)
                    res["grass_quitado"] += len(rem)
        except Exception as ex:
            res["err"].append(str(ex)[:50])
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA REMATE boxwood=%d grass=%d" % (res["boxwood_quitado"], res["grass_quitado"]))
