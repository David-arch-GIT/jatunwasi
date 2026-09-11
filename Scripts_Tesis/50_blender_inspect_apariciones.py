# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER headless) Inspecciona los 3 modelos nuevos (condenado, karisiri, duende): triangulos, materiales, si tienen textura, y dimensiones reales.
# Por que se necesito: Planear la optimizacion Quest de cada uno y ver cual necesita color/textura.
# Resultado obtenido: (pendiente) JSON con el estado de cada modelo.
# ------------------------------------------------------------
import bpy, json

BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/incoming/"
MODELS = {
    "condenado": BASE + "condenado alma.glb",
    "karisiri":  BASE + "karisiri.glb",
    "duende":    BASE + "duende pero sin texturas blanco .glb",
}
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/blender_inspect.json"

res = {}
for name, path in MODELS.items():
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=path)
    except Exception as e:
        res[name] = {"error_import": str(e)}
        continue
    tris = 0
    mats = set()
    imgs = set()
    verts = 0
    dx = dy = dz = 0.0
    n_mesh = 0
    for o in bpy.data.objects:
        if o.type == 'MESH':
            n_mesh += 1
            me = o.data
            me.calc_loop_triangles()
            tris += len(me.loop_triangles)
            verts += len(me.vertices)
            d = o.dimensions
            dx = max(dx, d.x); dy = max(dy, d.y); dz = max(dz, d.z)
            for ms in o.material_slots:
                if ms.material:
                    mats.add(ms.material.name)
                    if ms.material.use_nodes:
                        for nd in ms.material.node_tree.nodes:
                            if nd.type == 'TEX_IMAGE' and nd.image:
                                imgs.add(nd.image.name + " " + str(tuple(nd.image.size)))
    res[name] = {
        "meshes": n_mesh, "tris": tris, "verts": verts,
        "materials": list(mats), "texturas": list(imgs), "tiene_textura": len(imgs) > 0,
        "dims_m": [round(dx, 3), round(dy, 3), round(dz, 3)],
    }

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print("INSPECT OK")
