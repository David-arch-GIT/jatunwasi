# 371_ue_audit_recorrido_barreras.py
# Auditoria del recorrido guiado ordenado (Templo->Convento->Hacienda->creditos).
# Verifica que las barreras BLOQUEEN al inicio (visibles + colision), que los
# triggers del BP_GestorRecorrido esten bien ubicados sobre la ruta, y el PlayerStart.
# Solo LECTURA. No modifica nada. Salida JSON a Saved/ClaudeBackups/.
import unreal, json, os

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_recorrido_371.json"
res = {"barreras": [], "creditos": [], "triggers": [], "playerstart": [], "err": None}

def loc(a):
    v = a.get_actor_location()
    return [round(v.x, 1), round(v.y, 1), round(v.z, 1)]

try:
    acts = unreal.EditorLevelLibrary.get_all_level_actors()

    # Barreras por tag
    for tag in ["BarConvento", "BarHacienda"]:
        for a in acts:
            if a.actor_has_tag(tag):
                info = {"tag": tag, "name": a.get_actor_label(), "loc": loc(a),
                        "hidden": a.is_hidden_ed(), "hidden_game": a.get_editor_property("hidden")}
                # colision del root/mesh
                root = a.root_component
                try:
                    info["collision_enabled"] = str(root.get_collision_enabled())
                    info["collision_profile"] = str(root.get_collision_profile_name())
                except Exception as e:
                    info["collision_enabled"] = "n/a:" + str(e)
                res["barreras"].append(info)

    # Creditos
    for a in acts:
        if a.actor_has_tag("Creditos"):
            res["creditos"].append({"name": a.get_actor_label(), "loc": loc(a),
                                     "hidden_game": a.get_editor_property("hidden")})

    # Gestor + triggers (componentes box)
    for a in acts:
        lbl = a.get_actor_label()
        if "GestorRecorrido" in lbl or "Gestor" in lbl:
            res["triggers"].append({"actor": lbl, "loc": loc(a), "note": "instancia gestor"})
            comps = a.get_components_by_class(unreal.BoxComponent)
            for c in comps:
                wl = c.get_world_location()
                ext = c.get_scaled_box_extent()
                row = {"comp": c.get_name(),
                       "world": [round(wl.x,1), round(wl.y,1), round(wl.z,1)],
                       "extent": [round(ext.x,1), round(ext.y,1), round(ext.z,1)],
                       "gen_overlap": c.get_editor_property("generate_overlap_events"),
                       "collision": str(c.get_collision_enabled())}
                res["triggers"].append(row)

    # PlayerStart
    for a in acts:
        if isinstance(a, unreal.PlayerStart):
            res["playerstart"].append({"name": a.get_actor_label(), "loc": loc(a)})

except Exception as e:
    res["err"] = str(e)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
print("AUDIT_RECORRIDO_DONE")
