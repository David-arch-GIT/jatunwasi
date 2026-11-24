# 426d_blender_verificar_fbx_puertas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: verificacion (solo lectura) de los FBX exportados por 426: importa cada pieza y la
#   renderiza DE FRENTE (camara en -Y mirando +Y) para confirmar que no quedaron en espejo
#   (bisagras del convento a la izquierda como en el original) y que las piezas encajan.
import bpy, math, os
from mathutils import Vector
D = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/puertas/"
GROUPS = {"templo": [("SM_PuertaTemplo_Marco", 0), ("SM_PuertaTemplo_HojaIzq", -1.308), ("SM_PuertaTemplo_HojaDer", 1.308)],
          "hacienda": [("SM_PuertaHacienda_Marco", 0), ("SM_PuertaHacienda_HojaIzq", -1.1546), ("SM_PuertaHacienda_HojaDer", 1.1546)],
          "convento": [("SM_PuertaConvento_Montante", 0), ("SM_PuertaConvento_HojaIzq", -0.59)],
          "convento_der": [("SM_PuertaConvento_Montante", 0), ("SM_PuertaConvento_HojaDer", 0.59)]}
PIV = {"templo": -0.01, "hacienda": 0.2091, "convento": 0.1787, "convento_der": 0.1787}
for g, parts in GROUPS.items():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for nm, hx in parts:
        bpy.ops.import_scene.fbx(filepath=D + nm + ".fbx")
        ob = bpy.context.selected_objects[0]
        if hx != 0:
            ob.location = (hx, PIV[g], 0)
    scn = bpy.context.scene
    allv = [o.matrix_world @ v.co for o in scn.objects if o.type == 'MESH' for v in o.data.vertices]
    mn = Vector([min(v[i] for v in allv) for i in range(3)]); mx = Vector([max(v[i] for v in allv) for i in range(3)])
    c = (mn + mx) / 2
    scn.render.engine = 'BLENDER_WORKBENCH'; scn.display.shading.light = 'STUDIO'; scn.display.shading.color_type = 'TEXTURE'
    scn.render.resolution_x = 600; scn.render.resolution_y = 600
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = max(mx - mn) * 1.1; cam.location = c + Vector((0, -30, 0)); cam.rotation_euler = (math.radians(90), 0, 0)
    scn.render.filepath = D + "front_%s.png" % g; bpy.ops.render.render(write_still=True)
print("VERIF OK")
