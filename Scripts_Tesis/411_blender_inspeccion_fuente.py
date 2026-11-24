# 411_blender_inspeccion_fuente.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (BLENDER headless, solo lectura) inspeccionar el GLB original de Tripo de la fuente
#   ("fuente plaza mejorado.glb") y el FBX limpio previo: triangulos, dimensiones, materiales/texturas
#   y PIEZAS SUELTAS (loose parts) con su tamano y posicion -> detectar fragmentos flotantes.
# Uso: blender --background --python 411_blender_inspeccion_fuente.py
import bpy, bmesh, json, mathutils
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fuente_blender_inspect.json"
SRC = {"glb": r"C:/Users/Mi PC/Desktop/tripo ia generado/fuente plaza mejorado.glb",
       "fbx_limpia": r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/plaza/fuente_limpia.fbx"}
rep = {}
for key, path in SRC.items():
    r = {}
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if path.endswith(".glb"):
            bpy.ops.import_scene.gltf(filepath=path)
        else:
            bpy.ops.import_scene.fbx(filepath=path)
        ms = [o for o in bpy.data.objects if o.type == 'MESH']
        r["objects"] = len(ms)
        tris = 0; allc = []
        for o in ms:
            o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
            allc += [o.matrix_world @ v.co for v in o.data.vertices]
        r["tris"] = tris
        mn = [min(c[i] for c in allc) for i in range(3)]; mx = [max(c[i] for c in allc) for i in range(3)]
        r["bbox_min"] = [round(x, 3) for x in mn]; r["bbox_max"] = [round(x, 3) for x in mx]
        r["images"] = [[im.name, im.size[0], im.size[1]] for im in bpy.data.images]
        r["materials"] = [m.name for m in bpy.data.materials]
        parts = []
        for o in ms:
            bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
            seen = set()
            for v in bm.verts:
                if v.index in seen:
                    continue
                stack = [v]; comp = []
                seen.add(v.index)
                while stack:
                    x = stack.pop(); comp.append(x)
                    for e in x.link_edges:
                        y = e.other_vert(x)
                        if y.index not in seen:
                            seen.add(y.index); stack.append(y)
                cs = [o.matrix_world @ c.co for c in comp]
                a = [min(c[i] for c in cs) for i in range(3)]; b = [max(c[i] for c in cs) for i in range(3)]
                parts.append({"verts": len(comp), "min": [round(t, 3) for t in a], "max": [round(t, 3) for t in b]})
            bm.free()
        parts.sort(key=lambda p: -p["verts"])
        r["n_parts"] = len(parts)
        r["parts_top"] = parts[:25]
    except Exception as e:
        r["error"] = str(e)
    rep[key] = r
json.dump(rep, open(OUT, "w"), indent=1)
print("INSPECT OK")
