# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) Revisa cuales criaturas estan VISIBLES: hidden_in_game de los App_ (estaticos) y AppSK_ (skeletal),
#   la animacion actual en single-node de los skeletal, y si los InterpToMovement tienen puntos (movimiento robotico).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/visibilidad.json"
res = {"actores": [], "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not (lab.startswith("App_") or lab.startswith("AppSK_")):
        continue
    d = {"label": lab, "hidden": bool(a.get_editor_property("hidden") if a.has_editor_property("hidden") else a.is_hidden_ed())}
    try: d["hidden_game"] = bool(a.get_editor_property("actor_hidden_in_game"))
    except Exception: pass
    # skeletal: anim actual + interp
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        try:
            seq = c.get_editor_property("animation_data").get_editor_property("anim_to_play")
            d["anim_actual"] = seq.get_name() if seq else "NINGUNA(T-pose)"
        except Exception as e:
            d["anim_actual"] = "err:" + str(e)[:20]
    for c in a.get_components_by_class(unreal.InterpToMovementComponent):
        try:
            pts = c.get_editor_property("control_points")
            d["interp_puntos"] = len(pts) if pts else 0
            d["interp_duracion"] = round(float(c.get_editor_property("duration")), 1)
        except Exception as e:
            d["interp"] = "err:" + str(e)[:20]
    res["actores"].append(d)
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("VISIBILIDAD n=%d" % len(res["actores"]))
