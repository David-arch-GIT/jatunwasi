# 454_ue_reimportar_creditos.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: reimportar T_CreditosFinales desde creditos_finales.png (v2 de 453, lineas legibles) y
#   activar mipmaps (SimpleAverage) para que el texto no parpadee al verse reducido en el Quest.
#   Mantiene BGRA sin compresion (TC_EDITOR_ICON), sRGB, never_stream.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/reimport_creditos.json"
res = {"err": None}
try:
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/creditos_finales.png")
    t.set_editor_property("destination_path", "/Game/JWN/UI"); t.set_editor_property("destination_name", "T_CreditosFinales")
    t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    tex = unreal.load_asset("/Game/JWN/UI/T_CreditosFinales")
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_SIMPLE_AVERAGE)
    tex.set_editor_property("never_stream", True); tex.set_editor_property("srgb", True)
    res["saved"] = unreal.EditorAssetLibrary.save_loaded_asset(tex, False)
    res["size"] = [tex.blueprint_get_size_x(), tex.blueprint_get_size_y()]
    res["mips"] = str(tex.get_editor_property("mip_gen_settings"))
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
