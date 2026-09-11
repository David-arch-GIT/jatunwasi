# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: Diagnostica las colisiones de las mallas de la Hacienda (portal) y del Convento (arcos) para hallar cuales bloquean el paso.
# Por que se necesito: El usuario no puede atravesar el portal de la Hacienda ni los arcos del Convento al moverse con el control.
# Resultado obtenido: (pendiente) JSON con mallas candidatas, su collision_trace_flag, profile y tamano.
# ------------------------------------------------------------

import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_colisiones.json"

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

actors = all_actors()
res = {"total_actors": len(actors), "candidatos": [], "blocking_volumes": [], "pawns": []}
kw = ["haci","conv","puerta","portal","arco","arch","door","entrada","ingreso","claustro","patio"]

for a in actors:
    try:
        name = a.get_actor_label()
    except Exception:
        name = a.get_name()
    ln = name.lower()
    cls = a.get_class().get_name()
    loc = a.get_actor_location()

    if "BlockingVolume" in cls:
        res["blocking_volumes"].append({"name": name, "loc": [round(loc.x), round(loc.y), round(loc.z)]})
        continue
    if "Pawn" in cls or "Character" in cls or "XRPawn" in ln or "vrpawn" in ln:
        res["pawns"].append({"name": name, "class": cls})
        continue

    if any(k in ln for k in kw):
        info = {"name": name, "class": cls, "loc": [round(loc.x), round(loc.y), round(loc.z)]}
        smc = a.get_component_by_class(unreal.StaticMeshComponent)
        if smc:
            try:
                info["collision_enabled"] = str(smc.get_collision_enabled())
                info["profile"] = str(smc.get_collision_profile_name())
            except Exception as e:
                info["comp_err"] = str(e)
            sm = smc.get_editor_property("static_mesh")
            if sm:
                info["mesh"] = sm.get_name()
                try:
                    bs = sm.get_editor_property("body_setup")
                    if bs:
                        info["trace_flag"] = str(bs.get_editor_property("collision_trace_flag"))
                except Exception as e:
                    info["bs_err"] = str(e)
            try:
                b = smc.bounds.box_extent
                info["extent"] = [round(b.x), round(b.y), round(b.z)]
            except Exception:
                pass
        res["candidatos"].append(info)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("DIAG OK candidatos=%d blocking=%d pawns=%d" % (len(res["candidatos"]), len(res["blocking_volumes"]), len(res["pawns"])))
