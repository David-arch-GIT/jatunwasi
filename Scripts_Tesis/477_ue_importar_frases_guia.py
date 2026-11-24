# 477_ue_importar_frases_guia.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: importar las frases de 476 a /Game/JWN/Audio/Guia con las reglas de voz del proyecto:
#   SC_Narracion (max 1), SCL_Voz (se silencian cuando Adela/Convai habla o el usuario mantiene el grip),
#   PlayWhenSilent y PRIORIDAD 0.5 (< 1 de narraciones/cartelas): nunca cortan una narracion; si hay
#   una sonando, la frase es rechazada y el componente de guia la reintenta despues.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/frases_guia.json"
res = {"err": None, "ok": {}}
NAMES = ["A_Guia_Sigueme_Templo", "A_Guia_Sigueme_Convento", "A_Guia_Sigueme_Hacienda", "A_Guia_NoTeQuedes", "A_Guia_Preguntas", "A_Guia_Preguntas_Hacienda"]
try:
    ref = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Relato_templo")
    tasks = []
    for n in NAMES:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", "C:/UnrealProjects/JatunWasiNawpakay/Saved/NarrWav/%s.wav" % n)
        t.set_editor_property("destination_path", "/Game/JWN/Audio/Guia"); t.set_editor_property("destination_name", n)
        t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for n in NAMES:
        p = "/Game/JWN/Audio/Guia/" + n
        w = unreal.load_asset(p)
        w.set_editor_property("concurrency_set", ref.get_editor_property("concurrency_set"))
        w.set_editor_property("sound_class_object", ref.get_editor_property("sound_class_object"))
        w.set_editor_property("virtualization_mode", unreal.VirtualizationMode.PLAY_WHEN_SILENT)
        w.set_editor_property("priority", 0.5)
        unreal.EditorAssetLibrary.save_asset(p, False)
        res["ok"][n] = [round(w.get_editor_property("duration"), 1), w.get_editor_property("sound_class_object").get_name()]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
