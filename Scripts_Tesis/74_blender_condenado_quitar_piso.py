# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace: (BLENDER) Importa el Condenado, BORRA el disco/piso de fotogrametria (verts del fondo con radio XY grande), limpia, escala a ~1.75m, origen a la base. Renderiza para validar antes de riguear.
# Por que: El usuario pidio quitar el piso por defecto del modelo.
# ------------------------------------------------------------
import bpy, bmesh, math, mathutils, os
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/condenado_opt.glb"
OUTD = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
co = [v.co for v in obj.data.vertices]
minz = min(c.z for c in co); maxz = max(c.z for c in co)
xs = [c.x for c in co]; ys = [c.y for c in co]
cx = (min(xs)+max(xs))/2; cy = (min(ys)+max(ys))/2
H = maxz - minz
# borrar disco: verts del fondo (banda baja) con radio XY grande
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.verts.ensure_lookup_table()
todel = []
for v in bm.verts:
    if (v.co.z - minz) < 0.09*H:
        rad = math.hypot(v.co.x-cx, v.co.y-cy)
        if rad > 0.20:
            todel.append(v)
print("VERTS_BORRAR", len(todel), "de", len(bm.verts))
bmesh.ops.delete(bm, geom=todel, context='VERTS')
bmesh.update_edit_mesh(obj.data)
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0008)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.shade_smooth()
# recomputar base y centrar/escala
co = [v.co for v in obj.data.vertices]
minz = min(c.z for c in co); maxz = max(c.z for c in co)
xs = [c.x for c in co]; ys = [c.y for c in co]
cx = (min(xs)+max(xs))/2; cy = (min(ys)+max(ys))/2
obj.location = (-cx, -cy, -minz)
bpy.ops.object.transform_apply(location=True)
Hn = obj.dimensions.z
f = 1.75 / Hn if Hn > 0.01 else 1.0
obj.scale = (f, f, f); bpy.ops.object.transform_apply(scale=True)
print("NUEVA_H", round(obj.dimensions.z,2), "dims", round(obj.dimensions.x,2), round(obj.dimensions.y,2))
# render front + side
if bpy.context.scene.world is None: bpy.context.scene.world = bpy.data.worlds.new("W")
sc = bpy.context.scene; sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.05,0.05,0.06,1)
cam = bpy.data.objects.new("C", bpy.data.cameras.new("C")); sc.collection.objects.link(cam); sc.camera = cam
sun = bpy.data.objects.new("S", bpy.data.lights.new("S",'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 4; sun.rotation_euler=(math.radians(55),0,math.radians(30))
try: sc.render.engine='BLENDER_EEVEE_NEXT'
except: pass
sc.render.resolution_x=420; sc.render.resolution_y=560
Hh = obj.dimensions.z; cz = Hh/2; dist = Hh*1.6
for tag, loc in [("clean_front",(0,-dist,cz)), ("clean_side",(dist,0,cz))]:
    cam.location = loc
    dv = mathutils.Vector((0,0,cz)) - cam.location
    cam.rotation_euler = dv.to_track_quat('-Z','Y').to_euler()
    sc.render.filepath = OUTD + "condenado_" + tag + ".png"
    bpy.ops.render.render(write_still=True)
# guardar limpio para el siguiente paso
os.makedirs(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed", exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/condenado_sinpiso.glb", export_format='GLB')
print("CLEAN OK")
