import bpy, json
R={"creatures":{}}
files={
 "karisiri":"Saved/Models/processed/karisiri_full.glb",
 "condenado":"Saved/Models/processed/condenado_full.glb",
 "duende":"Saved/Models/processed/duende_full.glb",
}
base="C:/UnrealProjects/JatunWasiNawpakay/"
for name,fp in files.items():
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=base+fp)
        sc=bpy.context.scene
        sc.frame_set(sc.frame_start)
        # borrar Icospheres (esferas basura)
        for o in list(bpy.data.objects):
            if o.type=='MESH' and 'icosphere' in o.name.lower():
                bpy.data.objects.remove(o, do_unlink=True)
        meshes=[o for o in bpy.data.objects if o.type=='MESH']
        # criatura = mesh con mas vertices
        creature=max(meshes, key=lambda m: len(m.data.vertices)) if meshes else None
        dg=bpy.context.evaluated_depsgraph_get()
        def lowz(objs):
            mn=1e9
            for m in objs:
                ev=m.evaluated_get(dg); me=ev.to_mesh(); mw=ev.matrix_world
                for v in me.vertices:
                    z=(mw@v.co).z
                    if z<mn: mn=z
                ev.to_mesh_clear()
            return mn
        feet=lowz([creature]) if creature else 0.0
        # mover todos los objetos raiz por -feet (pies -> 0)
        for o in bpy.data.objects:
            if o.parent is None:
                o.location.z -= feet
        bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get()
        newfeet=lowz([creature]) if creature else 0.0
        # exportar
        for o in bpy.data.objects: o.select_set(True)
        outp=base+"Saved/Models/processed/%s_grounded.glb"%name
        bpy.ops.export_scene.gltf(filepath=outp, export_format='GLB', export_animations=True, use_selection=False)
        R["creatures"][name]={"feet_antes":round(feet,3),"feet_despues":round(newfeet,3),
            "creature_mesh":creature.name if creature else None,"meshes_restantes":[m.name for m in meshes]}
    except Exception as e:
        import traceback
        R["creatures"][name]={"err":str(e)[:150],"tb":traceback.format_exc()[-200:]}
open(base+"Saved/ClaudeBackups/blender_ground.json","w").write(json.dumps(R,indent=0))
print("DONE")
