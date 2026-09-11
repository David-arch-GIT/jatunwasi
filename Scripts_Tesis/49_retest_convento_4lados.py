# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: Prueba si el NavMesh conecta hacia el centro del claustro del Convento desde los 4 lados (tras el fix de arcos y el rebuild).
# Por que se necesito: Confirmar que al menos un arco quedo transitable para entrar al claustro.
# Resultado obtenido: (pendiente) ruta valida/parcial por cada lado.
# ------------------------------------------------------------

import unreal, json

OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/retest_convento.json"
world = unreal.EditorLevelLibrary.get_editor_world()
CENTER = [6200, 5000, 60]
res = {"rutas": []}

def test(nombre, start):
    e = {"lado": nombre, "start": start}
    try:
        p = unreal.NavigationSystemV1.find_path_to_location_synchronously(world, unreal.Vector(*start), unreal.Vector(*CENTER))
        if p:
            e["valida"] = bool(p.is_valid())
            e["parcial"] = bool(p.is_partial())
            try:
                pts = p.get_path_points() if hasattr(p, "get_path_points") else p.path_points
                e["puntos"] = len(pts)
            except Exception:
                pass
        else:
            e["valida"] = False
    except Exception as ex:
        e["error"] = str(ex)
    res["rutas"].append(e)

test("Sur",   [6200, 4300, 60])
test("Norte", [6200, 5700, 60])
test("Oeste", [5400, 5000, 60])
test("Este",  [7000, 5000, 60])
test("Sur_lejos_camino", [6300, 3200, 60])

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
unreal.log("RETEST convento listo")
