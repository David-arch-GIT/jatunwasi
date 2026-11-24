# 372_ue_barreras_invisibles.py
# Deja las barreras del recorrido (BarConvento, BarHacienda) INVISIBLES en juego
# pero conservando la colision BlockAll (siguen frenando al usuario). Quita el
# cubo gris visible (regla: no cubos visibles) sin tocar la logica del Blueprint.
# El componente queda visible en el EDITOR (para poder seleccionarlo) y oculto en PLAY/VR.
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/barreras_invis_372.json"
res = {"cambios": [], "errs": []}
try:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
    for a in acts:
        for tag in ["BarConvento", "BarHacienda"]:
            if a.actor_has_tag(tag):
                for c in a.get_components_by_class(unreal.StaticMeshComponent):
                    try:
                        c.set_editor_property("hidden_in_game", True)   # invisible en PLAY/VR
                        # colision intacta (no se toca) -> sigue BlockAll
                        res["cambios"].append({"actor": a.get_actor_label(),
                                               "comp": c.get_name(),
                                               "hidden_in_game": True,
                                               "coll": str(c.get_collision_enabled())})
                    except Exception as e:
                        res["errs"].append(a.get_actor_label() + ":" + str(e))
except Exception as e:
    res["errs"].append("TOP:" + str(e))

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
print("BARRERAS_INVIS_DONE")
