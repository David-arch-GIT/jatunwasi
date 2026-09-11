# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Crea M_AparicionFantasma (Unlit + Translucido + two-sided; Emissive=BaseTex*boost; Opacidad PULSA con Time -> aparece/camina/desvanece en bucle SOLO). Crea 4 MIs (textura + PhaseOffset por actor), las asigna a los AppSK_* y cambia su animacion a WALK.
# Por que: Evento automatico "se desvanece en el sitio" sin cableado BP (eleccion del usuario).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/material_fantasma.json"
res = {"steps": [], "err": []}
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
MPATH = "/Game/JWN/Apariciones/M_AparicionFantasma"

# ---- master material ----
if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
    unreal.EditorAssetLibrary.delete_asset(MPATH)
mat = tools.create_asset("M_AparicionFantasma", "/Game/JWN/Apariciones", unreal.Material, unreal.MaterialFactoryNew())
mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
mat.set_editor_property("two_sided", True)
def ex(c, x, y): return mel.create_material_expression(mat, c, x, y)
# emissive = BaseTex * boost
tex = ex(unreal.MaterialExpressionTextureSampleParameter2D, -800, -100); tex.set_editor_property("parameter_name", "BaseTex")
boost = ex(unreal.MaterialExpressionScalarParameter, -800, 120); boost.set_editor_property("parameter_name", "EmissiveBoost"); boost.set_editor_property("default_value", 1.35)
emul = ex(unreal.MaterialExpressionMultiply, -520, -40)
mel.connect_material_expressions(tex, "RGB", emul, "A")
mel.connect_material_expressions(boost, "", emul, "B")
mel.connect_material_property(emul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
# opacidad = clamp( sin( (Time+phase)*speed ) * gain - bias ) * maxop
tnode = ex(unreal.MaterialExpressionTime, -1100, 380)
phase = ex(unreal.MaterialExpressionScalarParameter, -1100, 520); phase.set_editor_property("parameter_name", "PhaseOffset"); phase.set_editor_property("default_value", 0.0)
addT = ex(unreal.MaterialExpressionAdd, -900, 400)
mel.connect_material_expressions(tnode, "", addT, "A")
mel.connect_material_expressions(phase, "", addT, "B")
speed = ex(unreal.MaterialExpressionScalarParameter, -1100, 640); speed.set_editor_property("parameter_name", "Speed"); speed.set_editor_property("default_value", 0.075)
mulS = ex(unreal.MaterialExpressionMultiply, -720, 420)
mel.connect_material_expressions(addT, "", mulS, "A")
mel.connect_material_expressions(speed, "", mulS, "B")
sinN = ex(unreal.MaterialExpressionSine, -560, 420); sinN.set_editor_property("period", 1.0)
mel.connect_material_expressions(mulS, "", sinN, "")
gain = ex(unreal.MaterialExpressionScalarParameter, -720, 600); gain.set_editor_property("parameter_name", "PulseGain"); gain.set_editor_property("default_value", 2.2)
mulG = ex(unreal.MaterialExpressionMultiply, -400, 440)
mel.connect_material_expressions(sinN, "", mulG, "A")
mel.connect_material_expressions(gain, "", mulG, "B")
negbias = ex(unreal.MaterialExpressionScalarParameter, -400, 600); negbias.set_editor_property("parameter_name", "PulseBiasNeg"); negbias.set_editor_property("default_value", -0.7)
addB = ex(unreal.MaterialExpressionAdd, -220, 460)
mel.connect_material_expressions(mulG, "", addB, "A")
mel.connect_material_expressions(negbias, "", addB, "B")
clamp = ex(unreal.MaterialExpressionClamp, -60, 460)
mel.connect_material_expressions(addB, "", clamp, "")
maxop = ex(unreal.MaterialExpressionScalarParameter, -220, 640); maxop.set_editor_property("parameter_name", "MaxOpacity"); maxop.set_editor_property("default_value", 0.92)
opmul = ex(unreal.MaterialExpressionMultiply, 120, 480)
mel.connect_material_expressions(clamp, "", opmul, "A")
mel.connect_material_expressions(maxop, "", opmul, "B")
mel.connect_material_property(opmul, "", unreal.MaterialProperty.MP_OPACITY)
mel.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset(MPATH)
res["steps"].append("material creado")

# ---- MIs por actor (textura + phase) + asignar + anim WALK ----
TEX = {
 "duende":    "/Game/JWN/Apariciones/Anim/Duende/duende_full/Textures/texture_20250901.texture_20250901",
 "condenado": "/Game/JWN/Apariciones/Anim/Condenado/condenado_full/Textures/Image_1.Image_1",
 "karisiri":  "/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/Textures/Image_1.Image_1",
}
WALK = {
 "duende":    "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Walk.duende_fullduende_Walk",
 "condenado": "/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Walk.condenado_fullcondenado_Walk",
 "karisiri":  "/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Walk.karisiri_fullkarisiri_Walk",
}
# actor -> (char, phase)
ACTORS = {
 "AppSK_Hac_Duende":     ("duende", 0.0),
 "AppSK_Plz_Duende":     ("duende", 5.0),
 "AppSK_Conv_Condenado": ("condenado", 9.0),
 "AppSK_Conv_Karisiri":  ("karisiri", 13.0),
}
eas = unreal.EditorActorSubsystem()
by_label = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for label, (char, ph) in ACTORS.items():
    try:
        a = by_label.get(label)
        if a is None: res["err"].append("no actor " + label); continue
        mi_name = "MI_Fant_" + label.replace("AppSK_", "")
        mip = "/Game/JWN/Apariciones/" + mi_name
        if unreal.EditorAssetLibrary.does_asset_exist(mip): unreal.EditorAssetLibrary.delete_asset(mip)
        mi = tools.create_asset(mi_name, "/Game/JWN/Apariciones", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, mat)
        tex_asset = unreal.load_asset(TEX[char])
        mel.set_material_instance_texture_parameter_value(mi, "BaseTex", tex_asset)
        mel.set_material_instance_scalar_parameter_value(mi, "PhaseOffset", ph)
        unreal.EditorAssetLibrary.save_asset(mip)
        comp = a.skeletal_mesh_component
        comp.set_material(0, mi)
        # cambiar anim a WALK (se mueve mientras aparece)
        walk = unreal.load_asset(WALK[char])
        comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = comp.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", walk)
        ad.set_editor_property("saved_looping", True)
        ad.set_editor_property("saved_playing", True)
        comp.set_editor_property("animation_data", ad)
        comp.play(True)
        res["steps"].append("ok " + label)
    except Exception as e:
        res["err"].append("%s: %s" % (label, e))

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("MATERIAL FANTASMA done")
