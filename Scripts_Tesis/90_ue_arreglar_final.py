# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) ARREGLO FINAL. Recrea M_AparicionFantasma LIVIANO (time-pulse, sin fresnel/lerp que colgaron el editor):
#   emissive=BaseTex*boost (COLOR restaurado, visible de noche), opacidad pulsa lento/espaciado -> aparece ~6s y se
#   desvanece ~34s (no spam). 4 MIs con textura real + phase escalonado, reasignadas. Animacion a IDLE (fantasma que
#   acecha, no marcha en el sitio). Sube el Condenado al suelo. Respeta las posiciones que el usuario movio.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/arreglo_final.json"
res = {"steps": [], "err": []}
try:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mel = unreal.MaterialEditingLibrary
    MPATH = "/Game/JWN/Apariciones/M_AparicionFantasma"
    if unreal.EditorAssetLibrary.does_asset_exist(MPATH):
        unreal.EditorAssetLibrary.delete_asset(MPATH)
    mat = tools.create_asset("M_AparicionFantasma", "/Game/JWN/Apariciones", unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("two_sided", True)
    def ex(c, x, y): return mel.create_material_expression(mat, c, x, y)
    tex = ex(unreal.MaterialExpressionTextureSampleParameter2D, -800, -100); tex.set_editor_property("parameter_name", "BaseTex")
    boost = ex(unreal.MaterialExpressionScalarParameter, -800, 120); boost.set_editor_property("parameter_name", "EmissiveBoost"); boost.set_editor_property("default_value", 1.5)
    emul = ex(unreal.MaterialExpressionMultiply, -520, -40)
    mel.connect_material_expressions(tex, "RGB", emul, "A"); mel.connect_material_expressions(boost, "", emul, "B")
    mel.connect_material_property(emul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    tnode = ex(unreal.MaterialExpressionTime, -1100, 380)
    phase = ex(unreal.MaterialExpressionScalarParameter, -1100, 520); phase.set_editor_property("parameter_name", "PhaseOffset"); phase.set_editor_property("default_value", 0.0)
    addT = ex(unreal.MaterialExpressionAdd, -900, 400)
    mel.connect_material_expressions(tnode, "", addT, "A"); mel.connect_material_expressions(phase, "", addT, "B")
    speed = ex(unreal.MaterialExpressionScalarParameter, -1100, 640); speed.set_editor_property("parameter_name", "Speed"); speed.set_editor_property("default_value", 0.025)
    mulS = ex(unreal.MaterialExpressionMultiply, -720, 420)
    mel.connect_material_expressions(addT, "", mulS, "A"); mel.connect_material_expressions(speed, "", mulS, "B")
    sinN = ex(unreal.MaterialExpressionSine, -560, 420); sinN.set_editor_property("period", 1.0)
    mel.connect_material_expressions(mulS, "", sinN, "")
    gain = ex(unreal.MaterialExpressionScalarParameter, -720, 600); gain.set_editor_property("parameter_name", "PulseGain"); gain.set_editor_property("default_value", 2.5)
    mulG = ex(unreal.MaterialExpressionMultiply, -400, 440)
    mel.connect_material_expressions(sinN, "", mulG, "A"); mel.connect_material_expressions(gain, "", mulG, "B")
    negbias = ex(unreal.MaterialExpressionScalarParameter, -400, 600); negbias.set_editor_property("parameter_name", "PulseBiasNeg"); negbias.set_editor_property("default_value", -1.4)
    addB = ex(unreal.MaterialExpressionAdd, -220, 460)
    mel.connect_material_expressions(mulG, "", addB, "A"); mel.connect_material_expressions(negbias, "", addB, "B")
    clamp = ex(unreal.MaterialExpressionClamp, -60, 460)
    mel.connect_material_expressions(addB, "", clamp, "")
    maxop = ex(unreal.MaterialExpressionScalarParameter, -220, 640); maxop.set_editor_property("parameter_name", "MaxOpacity"); maxop.set_editor_property("default_value", 0.95)
    opmul = ex(unreal.MaterialExpressionMultiply, 120, 480)
    mel.connect_material_expressions(clamp, "", opmul, "A"); mel.connect_material_expressions(maxop, "", opmul, "B")
    mel.connect_material_property(opmul, "", unreal.MaterialProperty.MP_OPACITY)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset(MPATH)
    res["steps"].append("material OK")

    TEX = {"duende":"/Game/JWN/Apariciones/Anim/Duende/duende_full/Textures/texture_20250901.texture_20250901",
           "condenado":"/Game/JWN/Apariciones/Anim/Condenado/condenado_full/Textures/Image_1.Image_1",
           "karisiri":"/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/Textures/Image_1.Image_1"}
    IDLE = {"duende":"/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle",
            "condenado":"/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Idle.condenado_fullcondenado_Idle",
            "karisiri":"/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Idle.karisiri_fullkarisiri_Idle"}
    ACTORS = {"AppSK_Hac_Duende":("duende",0.0),"AppSK_Plz_Duende":("duende",11.0),
              "AppSK_Conv_Condenado":("condenado",22.0),"AppSK_Conv_Karisiri":("karisiri",33.0)}
    eas = unreal.EditorActorSubsystem()
    by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    for label,(char,ph) in ACTORS.items():
        try:
            a = by.get(label)
            if a is None: res["err"].append("no "+label); continue
            mip = "/Game/JWN/Apariciones/MI_Fant_"+label.replace("AppSK_","")
            if unreal.EditorAssetLibrary.does_asset_exist(mip): unreal.EditorAssetLibrary.delete_asset(mip)
            mi = tools.create_asset("MI_Fant_"+label.replace("AppSK_",""), "/Game/JWN/Apariciones", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
            mel.set_material_instance_parent(mi, mat)
            mel.set_material_instance_texture_parameter_value(mi, "BaseTex", unreal.load_asset(TEX[char]))
            mel.set_material_instance_scalar_parameter_value(mi, "PhaseOffset", ph)
            unreal.EditorAssetLibrary.save_asset(mip)
            comp = a.skeletal_mesh_component
            comp.set_material(0, mi)
            idle = unreal.load_asset(IDLE[char])
            comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            ad = comp.get_editor_property("animation_data")
            ad.set_editor_property("anim_to_play", idle); ad.set_editor_property("saved_looping", True); ad.set_editor_property("saved_playing", True)
            comp.set_editor_property("animation_data", ad); comp.play(True)
            # subir al suelo si quedo hundido (base -> ~12)
            b = a.get_actor_bounds(False); bottom = b[0].z - b[1].z
            if bottom < 5:
                l = a.get_actor_location(); a.set_actor_location(unreal.Vector(l.x, l.y, l.z + (12.0 - bottom)), False, True)
                res["steps"].append("subido "+label)
            res["steps"].append("ok "+label)
        except Exception as e:
            res["err"].append("%s: %s" % (label, e))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception as e:
    import traceback; res["err"].append(traceback.format_exc())
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ARREGLO FINAL done")
