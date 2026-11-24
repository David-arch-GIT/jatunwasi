# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Que hace: revierte el domo del cielo al look APROBADO:
#   reimporta la textura original (airglow suave) y pone M_Mountains de nuevo en
#   TRANSLUCENT con Alpha->Opacity. (El ahorro de masked no vale el riesgo visual.)
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"; R={}
try:
    t=unreal.AssetImportTask()
    t.filename="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/backdrop_real.png"
    t.destination_path="/Game/JWN/Env"; t.destination_name="T_Mountains"
    t.replace_existing=True; t.automated=True; t.save=True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Env/T_Mountains")
    mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Env/M_Mountains")
    tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/Env/T_Mountains")
    mel=unreal.MaterialEditingLibrary
    ts=mel.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-520,-250)
    ts.set_editor_property("texture",tex)
    mel.connect_material_property(ts,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(ts,"A",unreal.MaterialProperty.MP_OPACITY)
    mat.set_editor_property("blend_mode",unreal.BlendMode.BLEND_TRANSLUCENT)
    mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    mat.set_editor_property("two_sided",True)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Env/M_Mountains")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"]=True
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-400:]
open(out+"/domo_revert.json","w").write(json.dumps(R)); print("REVERT", json.dumps(R))
