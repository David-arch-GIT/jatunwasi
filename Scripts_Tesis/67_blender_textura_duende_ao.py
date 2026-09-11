# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER Cycles headless) Al duende (sin textura) le hace Smart UV + hornea Oclusion Ambiental (AO) a 1K para darle profundidad/forma, y exporta la textura AO. Asi en UE se ve con relieve (diseno), no plano.
# Por que se necesito: El duende no tenia texturas; el usuario quiere que su diseno se vea texturizado, no plano.
# Resultado obtenido: (pendiente) Duende_AO.png para modular el color en UE.
# ------------------------------------------------------------
import bpy, os
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/duende_color.glb"
OUTDIR = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
AO_PATH = OUTDIR + "Duende_AO.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Smart UV
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

# imagen AO
img = bpy.data.images.new("Duende_AO", 1024, 1024)
# material con nodo de imagen activo para el bake
mat = obj.data.materials[0] if obj.data.materials else bpy.data.materials.new("M_DuendeBake")
if not obj.data.materials:
    obj.data.materials.append(mat)
mat.use_nodes = True
nt = mat.node_tree
texn = nt.nodes.new("ShaderNodeTexImage")
texn.image = img
nt.nodes.active = texn

# Cycles + bake AO
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
try:
    scene.cycles.samples = 32
    scene.cycles.device = 'CPU'
except Exception:
    pass
scene.render.bake.margin = 6
bpy.ops.object.bake(type='AO')
img.filepath_raw = AO_PATH
img.file_format = 'PNG'
img.save()

# exportar la malla CON las nuevas UVs para que el AO mapee bien en UE
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.export_scene.gltf(filepath=OUTDIR + "duende_uv.glb", export_format='GLB', use_selection=True, export_apply=True)
print("DUENDE AO OK", os.path.getsize(AO_PATH), "MESH", os.path.getsize(OUTDIR + "duende_uv.glb"))
