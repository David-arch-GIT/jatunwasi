# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (UE) Inspecciona el BP_Apparition y una instancia (App_Conv_Karisiri): componentes, tipo, malla actual y variables editables detectables.
# Por que se necesito: Decidir si basta con asignar las nuevas mallas a las apariciones existentes o montar un sistema nuevo.
# Resultado obtenido: (pendiente) estructura del BP de aparicion.
# ------------------------------------------------------------
import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inspect_bp_aparicion.json"

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

res = {"instancias": [], "narration_points": []}

for a in all_actors():
    cls = a.get_class().get_name()
    try:
        label = a.get_actor_label()
    except Exception:
        label = a.get_name()
    if "Apparition" in cls:
        info = {"label": label, "class": cls, "componentes": []}
        for c in a.get_components_by_class(unreal.ActorComponent):
            ci = {"nombre": c.get_name(), "tipo": c.get_class().get_name()}
            if isinstance(c, unreal.StaticMeshComponent):
                sm = c.get_editor_property("static_mesh")
                ci["mesh"] = sm.get_name() if sm else None
                ci["mat0"] = None
                try:
                    mats = c.get_materials()
                    ci["mats"] = [m.get_name() if m else None for m in mats]
                except Exception:
                    pass
            info["componentes"].append(ci)
        # intentar variables comunes del BP
        for vn in ["MeshToShow", "ApparitionMesh", "Mesh", "FadeTime", "MoveTarget", "MoveTo",
                   "AppearDistance", "Duration", "Sound", "ApparitionSound", "TargetLocation"]:
            try:
                v = a.get_editor_property(vn)
                info.setdefault("vars", {})[vn] = str(v)
            except Exception:
                pass
        res["instancias"].append(info)
    if "NarrationPoint" in cls:
        ni = {"label": label, "class": cls, "componentes": []}
        for c in a.get_components_by_class(unreal.ActorComponent):
            ni["componentes"].append({"nombre": c.get_name(), "tipo": c.get_class().get_name()})
        res["narration_points"].append(ni)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("INSPECT bp aparicion: %d instancias" % len(res["instancias"]))
