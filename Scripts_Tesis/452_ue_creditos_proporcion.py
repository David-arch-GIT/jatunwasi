# 452_ue_creditos_proporcion.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: corregir el plano CreditosFinal de BP_XRPawn: la textura es 16:9 (2048x1152) pero el plano
#   era vertical 90x160 cm (texto aplastado y fuera del campo visual comodo). Nueva escala (1.4, 0.7875, 1)
#   = 140x79 cm a 1.2 m (~61x36 grados). Respaldo previo del BP; compila y guarda.
import unreal, json, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_proporcion.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/Blueprints/BP_XRPawn.uasset", ROOT + "/Saved/ClaudeBackups/BP_XRPawn_pre_creditos_escala.uasset") if False else None
    bp = unreal.load_asset("/Game/VRTemplate/Blueprints/BP_XRPawn") if unreal.EditorAssetLibrary.does_asset_exist("/Game/VRTemplate/Blueprints/BP_XRPawn") else None
    if bp is None:
        for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "Blueprint")):
            if str(a.asset_name) == "BP_XRPawn":
                bp = a.get_asset(); break
    res["bp"] = bp.get_path_name()
    fp = unreal.SystemLibrary.convert_to_absolute_path(unreal.Paths.project_content_dir()) + bp.get_path_name().split(".")[0].replace("/Game/", "") + ".uasset"
    shutil.copy2(fp, ROOT + "/Saved/ClaudeBackups/BP_XRPawn_pre_creditos_escala.uasset"); res["backup"] = fp
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    hs = sds.k2_gather_subobject_data_for_blueprint(bp)
    done = False
    for h in hs:
        d = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if o and o.get_name().startswith("CreditosFinal"):
            o.set_editor_property("relative_scale3d", unreal.Vector(1.4, 0.7875, 1.0))
            res["nuevo"] = str(o.get_editor_property("relative_scale3d")); res["rot"] = str(o.get_editor_property("relative_rotation")); done = True
    res["done"] = done
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    res["saved"] = unreal.EditorAssetLibrary.save_asset(bp.get_path_name().split(".")[0], False)
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
