# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Rehace M_AparicionFantasma: opacidad controlada por parametro escalar "Appear" (0=invisible reposo, 1=visible),
#           emissive=BaseTex*boost + rim Fresnel (etereo). Quita el pulso por Time. Las MIs existentes se actualizan solas.
#           Deja Appear=0 por defecto. Verifica forzando Appear=1 en el condenado.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/material_appear.json"
res = {"ok": False, "err": None}
try:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    MPATH = "/Game/JWN/Apariciones/M_AparicionFantasma"
    # recrear master (las MIs hijas conservan su parent por ruta/nombre)
    if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
        unreal.EditorAssetLibrary.delete_asset(MPATH)
    mat = tools.create_asset("M_AparicionFantasma", "/Game/JWN/Apariciones", unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("two_sided", True)
    def ex(c, x, y): return mel.create_material_expression(mat, c, x, y)
    tex = ex(unreal.MaterialExpressionTextureSampleParameter2D, -820, -120); tex.set_editor_property("parameter_name", "BaseTex")
    boost = ex(unreal.MaterialExpressionScalarParameter, -820, 120); boost.set_editor_property("parameter_name", "EmissiveBoost"); boost.set_editor_property("default_value", 1.4)
    emul = ex(unreal.MaterialExpressionMultiply, -540, -60)
    mel.connect_material_expressions(tex, "RGB", emul, "A")
    mel.connect_material_expressions(boost, "", emul, "B")
    # rim fresnel etereo -> suma al emissive
    fres = ex(unreal.MaterialExpressionFresnel, -820, 300); fres.set_editor_property("exponent", 3.5)
    rimc = ex(unreal.MaterialExpressionConstant3Vector, -820, 420); rimc.set_editor_property("constant", unreal.LinearColor(0.35, 0.45, 0.6, 1.0))
    rim = ex(unreal.MaterialExpressionMultiply, -560, 320)
    mel.connect_material_expressions(fres, "", rim, "A")
    mel.connect_material_expressions(rimc, "", rim, "B")
    emadd = ex(unreal.MaterialExpressionAdd, -320, 40)
    mel.connect_material_expressions(emul, "", emadd, "A")
    mel.connect_material_expressions(rim, "", emadd, "B")
    mel.connect_material_property(emadd, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    # opacidad = Appear * (0.55 + 0.45*Fresnel) * MaxOpacity   (bordes aparecen primero = etereo)
    appear = ex(unreal.MaterialExpressionScalarParameter, -820, 560); appear.set_editor_property("parameter_name", "Appear"); appear.set_editor_property("default_value", 0.0)
    fbias = ex(unreal.MaterialExpressionLinearInterpolate, -560, 520)
    ca = ex(unreal.MaterialExpressionConstant, -720, 640); ca.set_editor_property("r", 0.55)
    cb = ex(unreal.MaterialExpressionConstant, -720, 700); cb.set_editor_property("r", 1.0)
    mel.connect_material_expressions(ca, "", fbias, "A")
    mel.connect_material_expressions(cb, "", fbias, "B")
    mel.connect_material_expressions(fres, "", fbias, "Alpha")
    op1 = ex(unreal.MaterialExpressionMultiply, -360, 560)
    mel.connect_material_expressions(appear, "", op1, "A")
    mel.connect_material_expressions(fbias, "", op1, "B")
    maxop = ex(unreal.MaterialExpressionScalarParameter, -360, 700); maxop.set_editor_property("parameter_name", "MaxOpacity"); maxop.set_editor_property("default_value", 0.95)
    op2 = ex(unreal.MaterialExpressionMultiply, -140, 580)
    mel.connect_material_expressions(op1, "", op2, "A")
    mel.connect_material_expressions(maxop, "", op2, "B")
    mel.connect_material_property(op2, "", unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(MPATH)
    # re-parentear las 4 MIs por si acaso, y dejar Appear=0
    for n in ["MI_Fant_Hac_Duende","MI_Fant_Plz_Duende","MI_Fant_Conv_Condenado","MI_Fant_Conv_Karisiri"]:
        p = "/Game/JWN/Apariciones/" + n
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            mi = unreal.load_asset(p)
            mel.set_material_instance_parent(mi, mat)
            mel.set_material_instance_scalar_parameter_value(mi, "Appear", 0.0)
            unreal.EditorAssetLibrary.save_asset(p)
    # verificacion: forzar condenado Appear=1
    mic = unreal.load_asset("/Game/JWN/Apariciones/MI_Fant_Conv_Condenado")
    mel.set_material_instance_scalar_parameter_value(mic, "Appear", 1.0)
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Apariciones/MI_Fant_Conv_Condenado")
    res["ok"] = True
except Exception as e:
    import traceback; res["err"] = traceback.format_exc()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MATERIAL APPEAR done ok=%s" % res["ok"])
