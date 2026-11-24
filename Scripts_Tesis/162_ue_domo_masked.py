# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Que hace: pasa el material del domo del cielo (M_Mountains) de
#   TRANSLUCENT a MASKED para eliminar el overdraw de pantalla completa (mas margen GPU
#   para transmitir, sin tocar lo que se ve de cerca). Reconecta Alpha->OpacityMask.
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={}
try:
    mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Env/M_Mountains")
    tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Env/T_Mountains")
    mel=unreal.MaterialEditingLibrary
    ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-500,250)
    ts.set_editor_property("texture",tex)
    mel.connect_material_property(ts,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY_MASK)
    mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_MASKED)
    mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided",True)
    mat.set_editor_property("opacity_mask_clip_value",0.33)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Env/M_Mountains")
    R["ok"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/domo_masked.json","w").write(json.dumps(R)); print("DOMO_MASKED", json.dumps(R))
