import unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
mat = EAL.load_asset("/Game/FotosAntano/M_FotoPlane")
# subir el multiplicador emissive
for ex in MEL.get_material_expressions(mat) if hasattr(MEL,"get_material_expressions") else []:
    if ex.get_class().get_name() == "MaterialExpressionMultiply":
        ex.set_editor_property("const_b", 2.5)
MEL.recompile_material(mat)
EAL.save_asset("/Game/FotosAntano/M_FotoPlane", only_if_is_dirty=False)
