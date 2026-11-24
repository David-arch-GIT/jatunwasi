# 432_ue_inventario_convento.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) inventario del CONVENTO para enriquecerlo: todos los actores dentro de su
#   caja (x 3300..8800, y 3200..7000), con malla/clase/posicion/altura; NavMesh caminable por celdas
#   de 1 m (para saber que espacios recorre el visitante y estan vacios); assets Tripo/props del
#   convento disponibles en /Game (TripoClean2, Props/Convento, Convento).
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inv_convento.json"
X0, X1, Y0, Y1 = 3300, 8800, 3200, 7000
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    acts = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        L = a.get_actor_location()
        if X0 <= L.x <= X1 and Y0 <= L.y <= Y1:
            sm = a.get_component_by_class(unreal.StaticMeshComponent)
            o, e = a.get_actor_bounds(False)
            acts.append([a.get_actor_label(), a.get_class().get_name(), sm.static_mesh.get_name() if sm and sm.static_mesh else None,
                         [round(L.x), round(L.y), round(L.z)], [round(e.x), round(e.y), round(e.z)], a.is_hidden_ed()])
    res["actors"] = acts
    grid = []
    for y in range(Y1, Y0 - 1, -100):
        row = ""
        for x in range(X0, X1 + 1, 100):
            p = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 50), None, None, unreal.Vector(45, 45, 120))
            p = p[0] if isinstance(p, tuple) else p
            if p is None: row += " "
            elif p.z > 250: row += "^"
            else: row += "."
        grid.append(row)
    res["nav"] = grid
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    av = []
    for path in ("/Game/JWN/TripoClean2", "/Game/JWN/Props/Convento", "/Game/JWN/Convento", "/Game/JWN/Santos"):
        for ad in reg.get_assets_by_path(path, recursive=True):
            if str(ad.asset_class_path.asset_name) == "StaticMesh":
                av.append(str(ad.package_name))
    res["mesh_assets"] = av
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
