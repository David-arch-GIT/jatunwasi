import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_mats.json"
res={"faroles":0, "canastas":0, "err":[]}
at=unreal.AssetToolsHelpers.get_asset_tools()
EAL=unreal.EditorAssetLibrary
MEL=unreal.MaterialEditingLibrary
BASE="/Game/JWN/Materials"

def make_mat(name, unlit, color, mult, rough=0.8):
    p=BASE+"/"+name
    if EAL.does_asset_exist(p): EAL.delete_asset(p)
    m=at.create_asset(name, BASE, unreal.Material, unreal.MaterialFactoryNew())
    if unlit:
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        col=MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400,0)
        col.set_editor_property("constant", unreal.LinearColor(color[0],color[1],color[2],1.0))
        mul=MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -180,0)
        mul.set_editor_property("const_b", mult)
        MEL.connect_material_expressions(col,"",mul,"A")
        MEL.connect_material_property(mul,"",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        col=MEL.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400,0)
        col.set_editor_property("constant", unreal.LinearColor(color[0],color[1],color[2],1.0))
        MEL.connect_material_property(col,"",unreal.MaterialProperty.MP_BASE_COLOR)
        rr=MEL.create_material_expression(m, unreal.MaterialExpressionConstant, -400,150)
        rr.set_editor_property("r", rough)
        MEL.connect_material_property(rr,"",unreal.MaterialProperty.MP_ROUGHNESS)
    MEL.recompile_material(m)
    EAL.save_asset(p, only_if_is_dirty=False)
    return m

mFarol=make_mat("M_JW_LanternGlow", True, (1.0,0.60,0.28), 2.0)
mCanasta=make_mat("M_JW_Basket", False, (0.42,0.30,0.17), 1.0, 0.85)

eas=unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if isinstance(c, unreal.InstancedStaticMeshComponent): continue
        m=c.get_editor_property("static_mesh"); mn=m.get_name() if m else ""
        if mn=="SM_JW_WallLantern":
            try:
                for i in range(max(1,c.get_num_materials())): c.set_material(i, mFarol)
                res["faroles"]+=1
            except Exception as e: res["err"].append("farol:"+str(e)[:40])
        elif "Canasta" in mn:
            try:
                for i in range(max(1,c.get_num_materials())): c.set_material(i, mCanasta)
                res["canastas"]+=1
            except Exception as e: res["err"].append("canasta:"+str(e)[:40])
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); les.save_current_level()
open(OUT,"w").write(json.dumps(res,indent=1))
