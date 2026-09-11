import bpy
from pathlib import Path

out=Path(__file__).resolve().parent/'EXP_Foundation_Floors_OriginalRestore.fbx'
bpy.ops.object.select_all(action='DESELECT')
obj=bpy.data.objects['EXP_Foundation_Floors']
obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,object_types={'MESH'},
    axis_forward='-Y',axis_up='Z',apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=True,
    mesh_smooth_type='FACE',use_triangles=True,add_leaf_bones=False,path_mode='AUTO')
