# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (BLENDER) Por personaje, importa *_animado.glb (esqueleto+mesh+Walk) e *_idle.glb (Idle),
#           pasa AMBAS acciones a NLA en un solo armature y exporta *_full.glb con 2 animaciones (Idle+Walk)
#           para que UE lo importe como 1 SkeletalMesh + 2 AnimSequences.
# ------------------------------------------------------------
import bpy, os
BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
for name in ["duende", "condenado", "karisiri"]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=BASE + name + "_animado.glb")
    armA = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    walk = armA.animation_data.action; walk.name = name + "_Walk"
    # importar idle (crea 2do armature)
    bpy.ops.import_scene.gltf(filepath=BASE + name + "_idle.glb")
    armB = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != armA][0]
    idle = armB.animation_data.action; idle.name = name + "_Idle"
    # pasar ambas acciones a NLA en armA (mismos nombres de hueso -> compatible)
    armA.animation_data.action = None
    tw = armA.animation_data.nla_tracks.new(); tw.name = "Walk"; tw.strips.new("Walk", 1, walk)
    ti = armA.animation_data.nla_tracks.new(); ti.name = "Idle"; ti.strips.new("Idle", 1, idle)
    # borrar armB y sus mallas
    rem = [armB] + [c for c in bpy.data.objects if c.parent == armB]
    for o in rem:
        bpy.data.objects.remove(o, do_unlink=True)
    # seleccionar armA + su malla
    bpy.ops.object.select_all(action='DESELECT')
    armA.select_set(True)
    for c in bpy.data.objects:
        if c.parent == armA: c.select_set(True)
    bpy.context.view_layer.objects.active = armA
    out = BASE + name + "_full.glb"
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True,
                              export_animations=True, export_skins=True, export_nla_strips=True)
    print("FULL", name, os.path.exists(out), round(os.path.getsize(out)/1024/1024, 1), "MB")
