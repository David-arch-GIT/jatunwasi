# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: Escanea por cercania (radio 2800) la zona de la Hacienda (-7000,-2500) y lista TODA malla con colision activa: nombre, mesh, trace_flag y tamano, para hallar que bloquea el portal.
# Por que se necesito: La malla principal de la Hacienda no tiene colision; el bloqueo del portal viene de otra malla no capturada por nombre.
# Resultado obtenido: (pendiente) lista de colisionadores en el portal de la Hacienda.
# ------------------------------------------------------------

import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_hacienda.json"
CENTER = unreal.Vector(-7000, -2500, 100)
RADIUS = 2800.0

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

res = {"center": [CENTER.x, CENTER.y], "radius": RADIUS, "colisionadores": []}

for a in all_actors():
    loc = a.get_actor_location()
    d = ((loc.x - CENTER.x) ** 2 + (loc.y - CENTER.y) ** 2) ** 0.5
    if d > RADIUS:
        continue
    for comp in a.get_components_by_class(unreal.StaticMeshComponent):
        try:
            ce = comp.get_collision_enabled()
        except Exception:
            continue
        if str(ce).endswith("NO_COLLISION: 0>"):
            continue
        try:
            name = a.get_actor_label()
        except Exception:
            name = a.get_name()
        info = {"name": name, "cls": a.get_class().get_name(), "dist": round(d),
                "loc": [round(loc.x), round(loc.y), round(loc.z)], "collision": str(ce)}
        sm = comp.get_editor_property("static_mesh")
        if sm:
            info["mesh"] = sm.get_name()
            try:
                bs = sm.get_editor_property("body_setup")
                info["trace_flag"] = str(bs.get_editor_property("collision_trace_flag")) if bs else "None"
            except Exception as e:
                info["tf_err"] = str(e)
        try:
            ext = comp.bounds.box_extent
            info["extent"] = [round(ext.x), round(ext.y), round(ext.z)]
        except Exception:
            pass
        res["colisionadores"].append(info)

# ordenar por tamano (los mas grandes primero: candidatos a tapar el vano)
res["colisionadores"].sort(key=lambda x: -(x.get("extent", [0, 0, 0])[0] + x.get("extent", [0, 0, 0])[1]))
res["total"] = len(res["colisionadores"])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("DIAG hacienda colisionadores=%d" % res["total"])
