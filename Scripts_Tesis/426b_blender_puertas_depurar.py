# 426b_blender_puertas_depurar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: DEPURAR el gate 426 (salio con picos y piezas incompletas). Con la puerta del templo:
#   etapa A capa frontal, B escalada+aplanada, C decimada, D solidificada. Render frontal de cada
#   etapa + bbox/tris/caras degeneradas para ubicar el paso que rompe.
import bpy, bmesh, json, math, os, sys
from mathutils import Vector
sys.argv = sys.argv[:1]
exec(open(r"C:/UnrealProjects/JatunWasiNawpakay/Scripts_Tesis/426_blender_puertas_procesar.py", encoding="utf-8").read().split("# ---------------- TEMPLO")[0])
OUTD2 = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/puertas/debug/"
os.makedirs(OUTD2, exist_ok=True)
rep = {}
def stats(me):
    me.calc_loop_triangles(); vs = [v.co for v in me.vertices]
    return {"tris": len(me.loop_triangles), "min": [round(min(v[i] for v in vs), 3) for i in range(3)], "max": [round(max(v[i] for v in vs), 3) for i in range(3)]}
def snap(ob, tag):
    scn = bpy.context.scene
    scn.render.engine = 'BLENDER_WORKBENCH'; scn.display.shading.light = 'STUDIO'; scn.display.shading.color_type = 'TEXTURE'
    scn.render.resolution_x = 500; scn.render.resolution_y = 500
    if not scn.camera:
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    cam = scn.camera; cam.data.type = 'ORTHO'
    vs = [ob.matrix_world @ v.co for v in ob.data.vertices]
    mn = Vector([min(v[i] for v in vs) for i in range(3)]); mx = Vector([max(v[i] for v in vs) for i in range(3)])
    c = (mn + mx) / 2; sz = max(mx.x - mn.x, mx.z - mn.z)
    cam.data.ortho_scale = sz * 1.1; cam.location = c + Vector((0, -50, 0)); cam.rotation_euler = (math.radians(90), 0, 0)
    cam.data.clip_end = 200
    scn.render.filepath = OUTD2 + tag + ".png"; bpy.ops.render.render(write_still=True)
ob, mat = load("templo")
bm = front_shell(ob, 3.5)
me = bpy.data.meshes.new("A"); bm.to_mesh(me); oA = bpy.data.objects.new("A", me); bpy.context.collection.objects.link(oA); me.materials.append(mat)
ob.hide_render = True
rep["A_front"] = stats(me); snap(oA, "A_front")
scale_flatten(bm, 4.78 / 89.9, 0.07)
me2 = bpy.data.meshes.new("B"); bm.to_mesh(me2); oA.data = me2; me2.materials.append(mat)
rep["B_scaled"] = stats(me2); snap(oA, "B_scaled")
bpy.context.view_layer.objects.active = oA; bpy.ops.object.select_all(action='DESELECT'); oA.select_set(True)
m = oA.modifiers.new("dec", 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = 0.25
bpy.ops.object.modifier_apply(modifier="dec")
rep["C_dec"] = stats(oA.data); snap(oA, "C_dec")
sd = oA.modifiers.new("sol", 'SOLIDIFY'); sd.thickness = 0.06; sd.offset = -1.0; sd.use_rim = True; sd.use_even_offset = False
bpy.ops.object.modifier_apply(modifier="sol")
rep["D_sol"] = stats(oA.data); snap(oA, "D_sol")
json.dump(rep, open(OUTD2 + "debug.json", "w"), indent=1)
print("DEBUG OK")
