# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER headless) Optimiza los 3 modelos de aparicion para Quest:
#   - condenado y karisiri (2M tris, 8K): decimate collapse a ~15k (conserva UVs de fotogrametria) + baja texturas a 2K.
#   - duende (20k, sin material): le asigna un material de color (verde-tierra oscuro, eerie) y decimate ligero.
#   Pone origen en la base (para que se apoye en el piso) y exporta GLB optimizado.
# Por que se necesito: Apariciones (relatos) para el Convento; el duende venia sin color; todo debe ser ligero para Quest 2.
# Resultado obtenido: (pendiente) 3 GLB en Saved/Models/processed listos para importar.
# ------------------------------------------------------------
import bpy, json, os

BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/incoming/"
OUTDIR = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
OUTJSON = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/blender_process.json"
os.makedirs(OUTDIR, exist_ok=True)

report = {}

def mesh_objs():
    return [o for o in bpy.data.objects if o.type == 'MESH']

def total_tris():
    t = 0
    for o in mesh_objs():
        o.data.calc_loop_triangles()
        t += len(o.data.loop_triangles)
    return t

def join_all():
    ms = mesh_objs()
    if not ms:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms:
        o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1:
        bpy.ops.object.join()
    return bpy.context.view_layer.objects.active

def origin_to_base(obj):
    # centro X/Y, base Z (minimo del bounding box en mundo)
    import mathutils
    coords = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    minx = min(c.x for c in coords); maxx = max(c.x for c in coords)
    miny = min(c.y for c in coords); maxy = max(c.y for c in coords)
    minz = min(c.z for c in coords)
    cur = bpy.context.scene.cursor.location.copy()
    bpy.context.scene.cursor.location = ((minx+maxx)/2.0, (miny+maxy)/2.0, minz)
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.context.scene.cursor.location = cur

def decimate_to(obj, target):
    obj.data.calc_loop_triangles()
    cur = len(obj.data.loop_triangles)
    if cur <= target:
        return cur
    m = obj.modifiers.new("dec", 'DECIMATE')
    m.decimate_type = 'COLLAPSE'
    m.ratio = max(0.001, float(target)/float(cur))
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)

def downscale_images(maxpx):
    changed = []
    for img in bpy.data.images:
        try:
            w, h = img.size[0], img.size[1]
            if w > maxpx or h > maxpx:
                img.scale(min(w, maxpx), min(h, maxpx))
                changed.append("%s->%dx%d" % (img.name, img.size[0], img.size[1]))
        except Exception:
            pass
    return changed

def export_glb(obj, path):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True,
                              export_apply=True, export_yup=True)

def process_photogram(name, infile, target_tris, tex_px):
    r = {}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=BASE + infile)
    r["tris_in"] = total_tris()
    obj = join_all()
    r["tris_after_join"] = total_tris()
    r["tris_out"] = decimate_to(obj, target_tris)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    r["tex"] = downscale_images(tex_px)
    origin_to_base(obj)
    out = OUTDIR + name + "_opt.glb"
    export_glb(obj, out)
    r["out"] = out
    r["size_mb"] = round(os.path.getsize(out)/1048576.0, 1)
    return r

def process_duende(infile, target_tris):
    r = {}
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=BASE + infile)
    r["tris_in"] = total_tris()
    obj = join_all()
    # material de color (verde-tierra oscuro, eerie)
    mat = bpy.data.materials.new("M_Duende")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.20, 0.27, 0.18, 1.0)
        try:
            bsdf.inputs["Roughness"].default_value = 0.82
        except Exception:
            pass
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    r["tris_out"] = decimate_to(obj, target_tris)
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    origin_to_base(obj)
    out = OUTDIR + "duende_color.glb"
    export_glb(obj, out)
    r["out"] = out
    r["size_mb"] = round(os.path.getsize(out)/1048576.0, 1)
    return r

try:
    report["condenado"] = process_photogram("condenado", "condenado alma.glb", 15000, 2048)
except Exception as e:
    report["condenado"] = {"error": str(e)}
try:
    report["karisiri"] = process_photogram("karisiri", "karisiri.glb", 15000, 2048)
except Exception as e:
    report["karisiri"] = {"error": str(e)}
try:
    report["duende"] = process_duende("duende pero sin texturas blanco .glb", 12000)
except Exception as e:
    report["duende"] = {"error": str(e)}

with open(OUTJSON, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
print("PROCESS OK")
