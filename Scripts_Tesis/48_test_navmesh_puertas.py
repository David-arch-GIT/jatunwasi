# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: Lista los NavMeshBoundsVolume (origen y tamano) y prueba rutas de afuera->adentro en Hacienda y Convento para ver si el NavMesh conecta.
# Por que se necesito: Confirmar si el bloqueo del portal Hacienda / arcos Convento es por falta de NavMesh interior o por conexion.
# Resultado obtenido: (pendiente) bounds de navmesh + resultado de pathfinding por zona.
# ------------------------------------------------------------

import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test_navmesh.json"
world = unreal.EditorLevelLibrary.get_editor_world()

def all_actors():
    try:
        return unreal.EditorActorSubsystem().get_all_level_actors()
    except Exception:
        return unreal.EditorLevelLibrary.get_all_level_actors()

res = {"navbounds": [], "rutas": []}

for a in all_actors():
    if "NavMeshBoundsVolume" in a.get_class().get_name():
        try:
            origin, ext = a.get_actor_bounds(False)
            res["navbounds"].append({
                "name": a.get_actor_label(),
                "origin": [round(origin.x), round(origin.y), round(origin.z)],
                "extent": [round(ext.x), round(ext.y), round(ext.z)]
            })
        except Exception as e:
            res["navbounds"].append({"name": a.get_actor_label(), "err": str(e)})

def project(p):
    try:
        r = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(*p), unreal.Vector(400, 400, 400))
        return [round(r.x), round(r.y), round(r.z)]
    except Exception as e:
        return "no_nav:" + str(e)

def test_ruta(nombre, start, end):
    entry = {"zona": nombre, "start": start, "end": end}
    entry["start_proj"] = project(start)
    entry["end_proj"] = project(end)
    try:
        path = unreal.NavigationSystemV1.find_path_to_location_synchronously(world, unreal.Vector(*start), unreal.Vector(*end))
        if path:
            entry["valida"] = bool(path.is_valid())
            try:
                entry["parcial"] = bool(path.is_partial())
            except Exception:
                entry["parcial"] = "n/a"
            try:
                pts = path.get_path_points() if hasattr(path, "get_path_points") else path.path_points
                entry["num_puntos"] = len(pts)
            except Exception:
                pass
        else:
            entry["valida"] = False
    except Exception as e:
        entry["error"] = str(e)
    res["rutas"].append(entry)

# Hacienda: entrada norte (apron) -> interior patio
test_ruta("Hacienda_entrada_a_interior", [-7500, -100, 80], [-7000, -2500, 60])
test_ruta("Hacienda_portal_a_patio",    [-7000, -1000, 90], [-7050, -2300, 60])
# Convento: afuera oeste -> claustro centro
test_ruta("Convento_afuera_a_claustro", [5300, 5000, 60], [6200, 5000, 60])
test_ruta("Convento_arco_a_centro",     [5600, 5000, 60], [6200, 5000, 60])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("TEST navmesh: bounds=%d rutas=%d" % (len(res["navbounds"]), len(res["rutas"])))
