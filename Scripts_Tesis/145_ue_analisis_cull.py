# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) Analiza para optimizacion SIN impacto visual: (1) cada luz point/spot: radio + max_draw_distance actual
#   (para culling per-radio). (2) grupos de instancias (ISM/HISM) con conteo + distancias de culling (para hallar los
#   que se dibujan demasiado lejos). Solo LEE, no cambia nada.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/analisis_cull.json"
res = {"luces": [], "ism": [], "resumen": {}, "err": []}
eas = unreal.EditorActorSubsystem()
n_ism_total = 0
for a in eas.get_all_level_actors():
    cn = a.get_class().get_name()
    try:
        if cn in ("PointLight","SpotLight"):
            lc = a.get_component_by_class(unreal.LocalLightComponent) or a.get_component_by_class(unreal.PointLightComponent)
            if lc:
                res["luces"].append([a.get_actor_label(), round(lc.get_editor_property("attenuation_radius")),
                                     round(lc.get_editor_property("max_draw_distance"))])
        # instancias (ISM/HISM) en cualquier actor
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                cnt = c.get_instance_count()
                n_ism_total += cnt
                m = c.get_editor_property("static_mesh")
                sd = c.get_editor_property("instance_start_cull_distance")
                ed = c.get_editor_property("instance_end_cull_distance")
                if cnt > 50:  # solo grupos grandes
                    res["ism"].append([a.get_actor_label()[:20], m.get_name() if m else "-", cnt, sd, ed])
            except Exception as e:
                res["err"].append("ism:"+str(e)[:40])
    except Exception as e:
        res["err"].append(cn+":"+str(e)[:40])
res["ism"].sort(key=lambda x: -x[2])
res["resumen"] = {"n_luces": len(res["luces"]), "instancias_totales": n_ism_total, "grupos_ism_grandes": len(res["ism"])}
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("ANALISIS CULL ok")
