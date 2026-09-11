# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER headless) Convierte los modelos de las leyendas (GLB) a FBX con texturas embebidas, para subirlos a Mixamo (auto-rig + animaciones). Mixamo no acepta GLB.
# Por que se necesito: Los modelos escaneados no tienen esqueleto; Mixamo los riguea y anima, pero pide FBX/OBJ.
# Resultado obtenido: (pendiente) FBX en Saved/Models/para_mixamo listos para Mixamo.
# ------------------------------------------------------------
import bpy, os
BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/para_mixamo/"
os.makedirs(OUT, exist_ok=True)

JOBS = {
    "Karisiri":  "karisiri_opt.glb",
    "Condenado": "condenado_opt.glb",
    "Duende":    "duende_uv.glb",
}

res = {}
for name, glb in JOBS.items():
    src = BASE + glb
    if not os.path.exists(src):
        res[name] = "FALTA glb"
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=src)
    # seleccionar todo
    bpy.ops.object.select_all(action='SELECT')
    out = OUT + name + "_paraMixamo.fbx"
    bpy.ops.export_scene.fbx(
        filepath=out,
        use_selection=False,
        path_mode='COPY',
        embed_textures=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_space_transform=True,
    )
    res[name] = round(os.path.getsize(out) / 1024.0, 0)

print("FBX RESULT", res)
