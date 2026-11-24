# 402_ue_criaturas_disolver.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: las 3 criaturas de leyenda se deshacen en brasas de color al acercarse el
#   jugador y se vuelven a formar al alejarse. Todo en el material (sin logica BP):
#   distancia camara->objeto controla un umbral de disolucion (textura de ruido) con borde
#   emisivo. Masked (apto movil). Cada leyenda con su color y distancias calibradas para que
#   se vea COMPLETA desde su punto de narracion.
#   Materiales originales quedan intactos (se crean MI nuevos) -> reversible.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/criaturas_disolver.json"
res = {"err": None, "assigned": []}
MAT = "/Game/JWN/FX/M_CriaturaDisuelve"
NOISE = "/Engine/EngineMaterials/Good64x64TilingNoiseHighFreq"
CRIAS = {
    "Cria_Karisiri": ("/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/Textures/Image_1", 800.0, 1150.0, (1.0, 0.45, 0.08)),
    "Cria_Condenado": ("/Game/JWN/Apariciones/Anim/Condenado/condenado_full/Textures/Image_1", 820.0, 1000.0, (0.55, 0.75, 1.0)),
    "Cria_Duende": ("/Game/JWN/Apariciones/Anim/Duende/duende_full/Textures/texture_20250901", 720.0, 860.0, (0.6, 1.0, 0.3)),
}
def ci(name):
    c = unreal.CustomInput(); c.set_editor_property("input_name", name); return c
try:
    mel = unreal.MaterialEditingLibrary
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    if unreal.EditorAssetLibrary.does_asset_exist(MAT):
        m = unreal.load_asset(MAT); mel.delete_all_material_expressions(m)
    else:
        m = tools.create_asset("M_CriaturaDisuelve", "/Game/JWN/FX", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("opacity_mask_clip_value", 0.0)
    m.set_editor_property("used_with_skeletal_mesh", True)
    tex = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -1000, -300)
    tex.set_editor_property("parameter_name", "BaseColorTexture")
    tex.set_editor_property("texture", unreal.load_asset(CRIAS["Cria_Karisiri"][0]))
    mel.connect_material_property(tex, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    uv = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1200, 100)
    uv.set_editor_property("u_tiling", 3.0); uv.set_editor_property("v_tiling", 3.0)
    nz = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -1000, 100)
    nz.set_editor_property("texture", unreal.load_asset(NOISE))
    mel.connect_material_expressions(uv, "", nz, "UVs")
    cam = mel.create_material_expression(m, unreal.MaterialExpressionCameraPositionWS, -1200, 300)
    obj = mel.create_material_expression(m, unreal.MaterialExpressionObjectPositionWS, -1200, 400)
    dist = mel.create_material_expression(m, unreal.MaterialExpressionDistance, -1000, 350)
    mel.connect_material_expressions(cam, "", dist, "A"); mel.connect_material_expressions(obj, "", dist, "B")
    near = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1000, 500)
    near.set_editor_property("parameter_name", "Near"); near.set_editor_property("default_value", 800.0)
    far = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1000, 600)
    far.set_editor_property("parameter_name", "Far"); far.set_editor_property("default_value", 1150.0)
    mask = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 200)
    mask.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    mask.set_editor_property("code", "float th = 1.0 - saturate((D - Nr) / max(Fr - Nr, 1.0)); return N + 0.01 - th;")
    mask.set_editor_property("inputs", [ci("D"), ci("N"), ci("Nr"), ci("Fr")])
    mel.connect_material_expressions(dist, "", mask, "D"); mel.connect_material_expressions(nz, "R", mask, "N")
    mel.connect_material_expressions(near, "", mask, "Nr"); mel.connect_material_expressions(far, "", mask, "Fr")
    mel.connect_material_property(mask, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    edge = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -700, 0)
    edge.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    edge.set_editor_property("code", "float th = 1.0 - saturate((D - Nr) / max(Fr - Nr, 1.0)); float mk = N + 0.01 - th; return saturate(1.0 - mk / 0.07) * saturate(th * 12.0);")
    edge.set_editor_property("inputs", [ci("D"), ci("N"), ci("Nr"), ci("Fr")])
    mel.connect_material_expressions(dist, "", edge, "D"); mel.connect_material_expressions(nz, "R", edge, "N")
    mel.connect_material_expressions(near, "", edge, "Nr"); mel.connect_material_expressions(far, "", edge, "Fr")
    ecol = mel.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -700, -200)
    ecol.set_editor_property("parameter_name", "EdgeColor"); ecol.set_editor_property("default_value", unreal.LinearColor(1.0, 0.45, 0.08, 1.0))
    e1 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, -100)
    mel.connect_material_expressions(ecol, "", e1, "A"); mel.connect_material_expressions(edge, "", e1, "B")
    e2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -100); e2.set_editor_property("const_b", 12.0)
    mel.connect_material_expressions(e1, "", e2, "A")
    bri = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -700, -400)
    bri.set_editor_property("parameter_name", "Brillo"); bri.set_editor_property("default_value", 0.35)
    b1 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, -350)
    mel.connect_material_expressions(tex, "RGB", b1, "A"); mel.connect_material_expressions(bri, "", b1, "B")
    add = mel.create_material_expression(m, unreal.MaterialExpressionAdd, -150, -200)
    mel.connect_material_expressions(b1, "", add, "A"); mel.connect_material_expressions(e2, "", add, "B")
    mel.connect_material_property(add, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)

    mis = {}
    for name, (texp, nr, fr, col) in CRIAS.items():
        mip = "/Game/JWN/FX/MI_" + name
        if unreal.EditorAssetLibrary.does_asset_exist(mip):
            mi = unreal.load_asset(mip)
        else:
            mi = tools.create_asset("MI_" + name, "/Game/JWN/FX", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, m)
        mel.set_material_instance_texture_parameter_value(mi, "BaseColorTexture", unreal.load_asset(texp))
        mel.set_material_instance_scalar_parameter_value(mi, "Near", nr)
        mel.set_material_instance_scalar_parameter_value(mi, "Far", fr)
        mel.set_material_instance_vector_parameter_value(mi, "EdgeColor", unreal.LinearColor(col[0], col[1], col[2], 1.0))
        mel.update_material_instance(mi)
        unreal.EditorAssetLibrary.save_asset(mip, False)
        mis[name] = mi
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() in mis:
            sk = a.get_component_by_class(unreal.SkeletalMeshComponent)
            for i in range(sk.get_num_materials()):
                sk.set_material(i, mis[a.get_actor_label()])
            res["assigned"].append([a.get_actor_label(), sk.get_num_materials(), sk.get_material(0).get_name()])
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res, indent=1))
