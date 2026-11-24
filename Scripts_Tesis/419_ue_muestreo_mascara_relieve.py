# 419_ue_muestreo_mascara_relieve.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) muestrear una grilla de 2 m sobre la zona del bosque/campos para saber
#   DONDE NO puede haber colinas: (a) celdas sobre el NavMesh (caminos, plaza, interiores),
#   (b) celdas con estructura encima (traza vertical que pega en algo que NO es vegetacion:
#   muros, casas, cercas, props), (c) campos RELLENO_Campos y leyendas (se agregan en Blender).
#   Ademas lee el mapeo UV de la cara superior del cubo del piso (Ground_Cochabamba) para que las
#   colinas usen EXACTAMENTE la misma textura/alineacion que el piso.
#   Salida: Saved/ClaudeBackups/relieve_mask.json
import unreal, json, math, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_mask.json"
X0, X1, Y0, Y1, STEP = -13600, 14200, -13000, 19400, 200
VEG_PREFIX = ("JW_ENV_", "PCG_", "HORIZ_", "HACFOR_", "RELLENO_", "NOCHE_", "ENV_", "StarDome")
res = {"err": None}
try:
    world = unreal.EditorLevelLibrary.get_editor_world()
    acts = unreal.EditorLevelLibrary.get_all_level_actors()
    ignore = [a for a in acts if a.get_actor_label().startswith(VEG_PREFIX)]
    ground = [a for a in acts if a.get_actor_label() == "Ground_Cochabamba"][0]
    ignore.append(ground)
    # UV del cubo: cara superior
    sm = unreal.load_asset("/Engine/BasicShapes/Cube")
    top = []
    for sec in range(1):
        out = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(sm, 0, sec)
        verts, tris, normals, uvs, tangents = out[0], out[1], out[2], out[3], out[4]
        for v, n, uv in zip(verts, normals, uvs):
            if n.z > 0.9:
                top.append([v.x, v.y, v.z, uv.x, uv.y])
    res["cube_top_uv"] = top
    gt = ground.get_actor_transform()
    res["ground"] = {"loc": [gt.translation.x, gt.translation.y, gt.translation.z], "scale": [gt.scale3d.x, gt.scale3d.y, gt.scale3d.z],
                     "yaw": ground.get_actor_rotation().yaw}
    nx = (X1 - X0) // STEP + 1; ny = (Y1 - Y0) // STEP + 1
    nav = []; struct = []
    ext = unreal.Vector(70, 70, 400)
    for j in range(ny):
        y = Y0 + j * STEP
        rn = []; rs = []
        for i in range(nx):
            x = X0 + i * STEP
            p = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 0), None, None, ext)
            loc = p[0] if isinstance(p, tuple) else p
            rn.append(1 if loc is not None else 0)
            h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 2500), unreal.Vector(x, y, -60),
                    unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, ignore, unreal.DrawDebugTrace.NONE, True)
            t = h.to_tuple() if h else None
            rs.append(1 if (t and t[0] and t[4].z > 10) else 0)
        nav.append(rn); struct.append(rs)
    res.update({"x0": X0, "y0": Y0, "step": STEP, "nx": nx, "ny": ny, "nav": nav, "struct": struct})
    res["nav_cells"] = sum(map(sum, nav)); res["struct_cells"] = sum(map(sum, struct))
    # puntos de exclusion extra
    camp = []
    for a in acts:
        if a.get_actor_label() == "RELLENO_Campos":
            for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
                for k in range(c.get_instance_count()):
                    tr = c.get_instance_transform(k, True)
                    camp.append([round(tr.translation.x), round(tr.translation.y)])
    res["campos"] = camp
    leg = []
    for a in acts:
        lb = a.get_actor_label()
        if lb.startswith(("Cria_", "App3D_", "Trig_Conv_", "Trig_Hac_", "Snd_App_", "RELLENO_Animas", "RELATO_", "Narr_")):
            L = a.get_actor_location(); leg.append([lb, round(L.x), round(L.y)])
    res["legend_pts"] = leg
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
