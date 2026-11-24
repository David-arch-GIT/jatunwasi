# 401b_ue_luciernaga_material_suave.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: reconstruir M_Luciernaga EN EL MISMO ASSET (no rompe referencias) con brillo suave:
#   centro brillante y bordes difuminados (1 - Fresnel), para que no se vea la forma de la malla.
#   Mismo movimiento vivo (WPO por instancia) y destellos irregulares.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luc_mat2.json"
res = {"err": None}
MAT = "/Game/JWN/FX/M_Luciernaga"
def ci(name):
    c = unreal.CustomInput(); c.set_editor_property("input_name", name); return c
try:
    mel = unreal.MaterialEditingLibrary
    m = unreal.load_asset(MAT)
    mel.delete_all_material_expressions(m)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 0)
    r = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -900, 200)
    wpo = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 300)
    wpo.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    wpo.set_editor_property("code",
        "float s = 0.65 + R * 0.7; float tt = T * s; float a = R * 61.7; float b = R * 23.3;"
        "return float3(sin(tt*0.37+a)*55.0 + sin(tt*0.91+b)*22.0,"
        " cos(tt*0.29+b)*55.0 + sin(tt*0.73+a)*22.0,"
        " sin(tt*0.53+a*0.5)*30.0 + sin(tt*1.31+b)*10.0);")
    wpo.set_editor_property("inputs", [ci("T"), ci("R")])
    mel.connect_material_expressions(t, "", wpo, "T"); mel.connect_material_expressions(r, "", wpo, "R")
    mel.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    br = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, -150)
    br.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    br.set_editor_property("code",
        "float t = T * (0.8 + R * 0.7) + R * 97.0;"
        "float p = pow(saturate(sin(t)), 10.0);"
        "float q = pow(saturate(sin(t * 0.37 + R * 13.0) * 0.5 + 0.6), 2.0);"
        "return 0.10 + p * q * 1.4;")
    br.set_editor_property("inputs", [ci("T"), ci("R")])
    mel.connect_material_expressions(t, "", br, "T"); mel.connect_material_expressions(r, "", br, "R")
    fr = mel.create_material_expression(m, unreal.MaterialExpressionFresnel, -500, -450)
    fr.set_editor_property("exponent", 1.5)
    om = mel.create_material_expression(m, unreal.MaterialExpressionOneMinus, -300, -450)
    mel.connect_material_expressions(fr, "", om, "")
    col = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -500, -650)
    col.set_editor_property("constant", unreal.LinearColor(0.65, 1.0, 0.2, 1.0))
    m1 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, -250)
    mel.connect_material_expressions(col, "", m1, "A"); mel.connect_material_expressions(br, "", m1, "B")
    m2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -100, -300)
    mel.connect_material_expressions(m1, "", m2, "A"); mel.connect_material_expressions(om, "", m2, "B")
    m3 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, 50, -300)
    m3.set_editor_property("const_b", 18.0)
    mel.connect_material_expressions(m2, "", m3, "A")
    mel.connect_material_property(m3, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)
    res["ok"] = True
    res["num_expr"] = mel.get_num_material_expressions(m)
except Exception:
    res["err"] = traceback.format_exc()[:700]
open(OUT, "w").write(json.dumps(res))
