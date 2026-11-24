# 412_blender_fuente_optimizar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (BLENDER headless) GATE de la fuente de la plaza (Tripo, 975k tris, 396 piezas).
#   1) unir vertices duplicados de costuras (merge by distance 0.3 mm; las UV son por loop, no se pierden)
#   2) listar piezas sueltas que quedan (para detectar fragmentos flotantes) y borrar las que estan
#      SEPARADAS del cuerpo (>3 cm de cualquier otra pieza grande) y son pequenas
#   3) decimate COLLAPSE a 40 000 tris (conserva UV -> se reutilizan las texturas 2K originales)
#   4) escala UNIFORME: ancho mayor = 5.27 m (mismo diametro que la pileta actual), origen en la base
#   (v2 2026-11-24: se quita TODA pieza separada >3 cm del cuerpo principal, p.ej. la cinta flotante sobre el remate)
#   5) exporta FBX (metros, Z arriba) sin texturas -> material se asigna en UE
import bpy, bmesh, json, mathutils, os
SRC = r"C:/Users/Mi PC/Desktop/tripo ia generado/fuente plaza mejorado.glb"
OUTF = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/plaza/SM_Fuente_Plaza_Q.fbx"
OUTJ = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fuente_gate.json"
TARGET = 40000
WIDTH = 5.27
rep = {}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
me = obj.data; me.calc_loop_triangles(); rep["tris_in"] = len(me.loop_triangles)

bm = bmesh.new(); bm.from_mesh(me)
r = bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
bm.to_mesh(me); bm.free()
me.calc_loop_triangles(); rep["tris_after_merge"] = len(me.loop_triangles)

def parts_of(me):
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    seen = set(); parts = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]; comp = []; seen.add(v.index)
        while stack:
            x = stack.pop(); comp.append(x.index)
            for e in x.link_edges:
                y = e.other_vert(x)
                if y.index not in seen:
                    seen.add(y.index); stack.append(y)
        cs = [bm.verts[i].co for i in comp]
        a = mathutils.Vector([min(c[i] for c in cs) for i in range(3)]); b = mathutils.Vector([max(c[i] for c in cs) for i in range(3)])
        parts.append({"idx": comp, "min": a, "max": b})
    bm.free()
    return parts
parts = parts_of(me)
parts.sort(key=lambda p: -len(p["idx"]))
rep["parts_after_merge"] = len(parts)
rep["parts_bbox"] = [{"verts": len(p["idx"]), "min": [round(x, 3) for x in p["min"]], "max": [round(x, 3) for x in p["max"]]} for p in parts[:6]]
big = [p for p in parts if len(p["idx"]) > 2000]
def gap(p, q):
    d = 0.0
    for i in range(3):
        d = max(d, p["min"][i] - q["max"][i], q["min"][i] - p["max"][i])
    return d
remove = []
for p in parts:
    if p is parts[0]:
        continue
    near = gap(p, parts[0])
    # pieza sin conexion al cuerpo: si esta lejos o es pequena (<5 % del cuerpo), se quita
    # (la "cinta" de Tripo: 7k verts, z 0.64-1.0, fuera del eje, sobresale del remate)
    if near > 0.03 or len(p["idx"]) < 0.05 * len(parts[0]["idx"]):
        remove.append(p)
rep["removed_floating"] = [{"verts": len(p["idx"]), "min": [round(x, 3) for x in p["min"]], "max": [round(x, 3) for x in p["max"]]} for p in remove]
if remove:
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    kill = set(i for p in remove for i in p["idx"])
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in kill], context='VERTS')
    bm.to_mesh(me); bm.free()

m = obj.modifiers.new("dec", 'DECIMATE'); m.decimate_type = 'COLLAPSE'
me.calc_loop_triangles(); cur = len(me.loop_triangles)
m.ratio = min(1.0, TARGET / float(cur))
bpy.ops.object.modifier_apply(modifier=m.name)
me.calc_loop_triangles(); rep["tris_out"] = len(me.loop_triangles)
bpy.ops.object.shade_smooth()

cs = [v.co for v in me.vertices]
mn = mathutils.Vector([min(c[i] for c in cs) for i in range(3)]); mx = mathutils.Vector([max(c[i] for c in cs) for i in range(3)])
s = WIDTH / max(mx.x - mn.x, mx.y - mn.y)
ctr = mathutils.Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
for v in me.vertices:
    v.co = (v.co - ctr) * s
me.update()
cs = [v.co for v in me.vertices]
rep["size_m"] = [round(max(c[i] for c in cs) - min(c[i] for c in cs), 3) for i in range(3)]
rep["uniform_scale"] = round(s, 4)
obj.name = "SM_Fuente_Plaza_Q"
for mat in list(obj.data.materials):
    pass
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
bpy.ops.export_scene.fbx(filepath=OUTF, use_selection=True, global_scale=1.0, apply_unit_scale=True,
                         axis_forward='-Y', axis_up='Z', bake_space_transform=True, path_mode='STRIP',
                         mesh_smooth_type='FACE', use_tspace=True)
rep["out"] = OUTF; rep["size_mb"] = round(os.path.getsize(OUTF) / 1048576.0, 1)
json.dump(rep, open(OUTJ, "w"), indent=1)
print("GATE OK")

