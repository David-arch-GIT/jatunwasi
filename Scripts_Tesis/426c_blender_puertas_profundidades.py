# 426c_blender_puertas_profundidades.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (solo lectura) para cada puerta Tripo: caras VISIBLES DESDE EL FRENTE (rayo hacia -Y
#   desde cada cara sin chocar con el modelo) y la distribucion de profundidad (y) de las caras que
#   miran al frente, separando zona de hojas y zona de marco -> plano real de las hojas, del marco y
#   cuanto sobresalen los herrajes. Sirve para elegir el corte trasero (y_cut) del gate 426 v2.
import bpy, bmesh, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SRC = r"C:/Users/Mi PC/Desktop/puertas tripoia/"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/puertas/profundidades.json"
REG = {"templo": lambda c: abs(c.x) <= 24.6 and (c.z <= 65.3 or (c.x ** 2 + (c.z - 65.3) ** 2) ** 0.5 <= 24.6),
       "hacienda": lambda c: abs(c.x) <= 41.2 and c.z <= 94.9,
       "convento": lambda c: True}
rep = {}
for name, inleaf in REG.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC + "puerta " + name + ".glb")
    ob = [o for o in bpy.data.objects if o.type == 'MESH'][0]
    bm = bmesh.new(); bm.from_mesh(ob.data); bm.transform(ob.matrix_world)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    vis = 0; hist = {"leaf": {}, "frame": {}}; tot = len(bm.faces)
    for f in bm.faces:
        c = f.calc_center_median()
        hit = tree.ray_cast(c + Vector((0, -0.02, 0)), Vector((0, -1, 0)))
        if hit[0] is not None:
            continue
        vis += 1
        if f.normal.y < -0.6:
            k = "leaf" if inleaf(c) else "frame"
            b = round(c.y * 2) / 2.0
            hist[k][b] = hist[k].get(b, 0) + 1
    rep[name] = {"faces": tot, "visible_front": vis,
                 "leaf_y_hist": sorted(hist["leaf"].items()), "frame_y_hist": sorted(hist["frame"].items()),
                 "ymin": round(min(v.co.y for v in bm.verts), 2), "ymax": round(max(v.co.y for v in bm.verts), 2)}
json.dump(rep, open(OUT, "w"), indent=0)
print("PROF OK")
