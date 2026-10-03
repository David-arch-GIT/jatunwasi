import unreal
EAL=unreal.EditorAssetLibrary; MEL=unreal.MaterialEditingLibrary
mat=EAL.load_asset("/Game/FotosAntano/M_FotoPlane")
exprs = MEL.get_material_expressions(mat)
done=False
for ex in exprs:
    if ex.get_class().get_name()=="MaterialExpressionMultiply":
        ex.set_editor_property("const_b", 8.0); done=True
MEL.recompile_material(mat)
EAL.save_asset("/Game/FotosAntano/M_FotoPlane", only_if_is_dirty=False)
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/b8.txt","w").write("done="+str(done)+" n="+str(len(exprs)))
