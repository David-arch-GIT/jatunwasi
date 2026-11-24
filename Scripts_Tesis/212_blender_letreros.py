import bpy, json, math
base="C:/UnrealProjects/JatunWasiNawpakay/"
R={"signs":[]}
def wood_mat(name, rgb):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bsdf=m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value=(rgb[0],rgb[1],rgb[2],1)
    bsdf.inputs["Roughness"].default_value=0.85
    return m
def emis_mat(name, rgb, strength):
    m=bpy.data.materials.new(name); m.use_nodes=True
    bsdf=m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value=(rgb[0],rgb[1],rgb[2],1)
    bsdf.inputs["Emission Color"].default_value=(rgb[0],rgb[1],rgb[2],1)
    bsdf.inputs["Emission Strength"].default_value=strength
    return m
names=["HACIENDA","CONVENTO","TEMPLO"]
for nm in names:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    woodD=wood_mat("WoodDark",(0.10,0.06,0.03))
    woodL=wood_mat("WoodLight",(0.45,0.30,0.16))
    emis=emis_mat("TxtGlow",(1.0,0.95,0.78),60.0)
    # POSTE (viga) 0.1x0.1x2.3, base en z=0
    bpy.ops.mesh.primitive_cube_add(size=1)
    post=bpy.context.active_object; post.name="Poste"
    post.scale=(0.06,0.06,1.15); post.location=(0,0,1.15)
    post.data.materials.append(woodD)
    # TABLA 2.0(x ancho) x 0.10(y grosor) x 0.44(z alto) a z=2.0
    bpy.ops.mesh.primitive_cube_add(size=1)
    board=bpy.context.active_object; board.name="Tabla"
    board.scale=(1.0,0.05,0.22); board.location=(0,0,2.0)
    board.data.materials.append(woodL)
    # bisel ligero (chaflan) para que parezca tabla real
    bpy.ops.object.modifier_add(type='BEVEL'); board.modifiers["Bevel"].width=0.02; board.modifiers["Bevel"].segments=2
    # TEXTO en 2 caras (frente +Y y atras -Y)
    for sgn,yoff,rotz in [(1,0.055,0.0),(-1,-0.055,math.pi)]:
        bpy.ops.object.text_add()
        t=bpy.context.active_object
        t.data.body=nm; t.data.align_x='CENTER'; t.data.align_y='CENTER'
        t.data.size=0.26; t.data.extrude=0.015
        t.rotation_euler=(math.pi/2,0,rotz)   # parado, mirando Y
        t.location=(0,yoff,2.0)
        t.data.materials.append(emis)
        bpy.context.view_layer.objects.active=t
        bpy.ops.object.convert(target='MESH')
    # seleccionar todo y exportar
    for o in bpy.data.objects: o.select_set(True)
    out=base+"Saved/Models/processed/sign_%s.glb"%nm
    bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True)
    R["signs"].append(nm)
open(base+"Saved/ClaudeBackups/blender_signs.json","w").write(json.dumps(R))
print("DONE")
