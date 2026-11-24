# 422_blender_inspeccion_puertas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (BLENDER headless, solo lectura) inspeccionar los 3 GLB de puertas de Tripo
#   (templo/convento/hacienda): triangulos, caja envolvente, ejes, texturas, piezas sueltas, y
#   RENDER frontal + lateral (textura real) para ver si es una hoja o dos, si trae marco/arco,
#   y hacia donde mira. Salida: Saved/ClaudeBackups/puertas_inspect.json + puerta_<n>_{front,side}.png
import bpy, bmesh, json, math, os
from mathutils import Vector
SRC = r"C:/Users/Mi PC/Desktop/puertas tripoia/"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/"
rep = {}
for name in ("templo", "convento", "hacienda"):
    r = {}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC + "puerta " + name + ".glb")
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    tris = 0; pts = []
    for o in ms:
        o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
        pts += [o.matrix_world @ v.co for v in o.data.vertices]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    r["objects"] = len(ms); r["tris"] = tris
    r["size"] = [round(mx[i] - mn[i], 3) for i in range(3)]; r["min"] = [round(v, 3) for v in mn]; r["max"] = [round(v, 3) for v in mx]
    r["images"] = [[im.name, im.size[0], im.size[1]] for im in bpy.data.images]
    # piezas tras unir dobles
    o = ms[0]
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
    bm.verts.ensure_lookup_table(); seen = set(); parts = []
    for v in bm.verts:
        if v.index in seen: continue
        st = [v]; seen.add(v.index); n = 0; cs = []
        while st:
            x = st.pop(); n += 1; cs.append(o.matrix_world @ x.co)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen: seen.add(y.index); st.append(y)
        parts.append([n, [round(min(c[i] for c in cs), 3) for i in range(3)], [round(max(c[i] for c in cs), 3) for i in range(3)]])
    bm.free(); parts.sort(key=lambda p: -p[0])
    r["parts"] = len(parts); r["parts_top"] = parts[:6]
    # render
    ctr = (mn + mx) / 2; size = max(mx - mn)
    scn = bpy.context.scene
    scn.render.engine = 'BLENDER_WORKBENCH'
    scn.display.shading.light = 'FLAT'; scn.display.shading.color_type = 'TEXTURE'
    scn.render.resolution_x = 700; scn.render.resolution_y = 700
    scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.15, 0.15, 0.15)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = size * 1.15
    for view, loc, rot in (("front", ctr + Vector((0, -size * 3, 0)), (math.radians(90), 0, 0)),
                           ("side", ctr + Vector((size * 3, 0, 0)), (math.radians(90), 0, math.radians(90))),
                           ("top", ctr + Vector((0, 0, size * 3)), (0, 0, 0))):
        cam.location = loc; cam.rotation_euler = rot
        scn.render.filepath = OUT + "puerta_%s_%s.png" % (name, view)
        bpy.ops.render.render(write_still=True)
    rep[name] = r
json.dump(rep, open(OUT + "puertas_inspect.json", "w"), indent=1)
print("PUERTAS OK")
