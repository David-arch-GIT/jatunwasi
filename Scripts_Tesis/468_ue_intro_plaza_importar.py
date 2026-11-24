# 468_ue_intro_plaza_importar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: importar A_Adela_IntroPlaza (de 467) con las mismas reglas que las voces (SC_Narracion,
#   SCL_Voz, PlayWhenSilent, prioridad 4 como la intro), asignarla a Adela_Intro_Audio y dejar SIN sonido el
#   Narration de RELATO_plaza (su contenido ya va dentro de la intro; evita el corte por concurrencia).
#   Guarda nivel y asset.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/intro_plaza.json"
res = {"err": None}
try:
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", r"C:/UnrealProjects/JatunWasiNawpakay/Saved/NarrWav/A_Adela_IntroPlaza.wav")
    t.set_editor_property("destination_path", "/Game/JWN/Audio/Relatos"); t.set_editor_property("destination_name", "A_Adela_IntroPlaza")
    t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    w = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Adela_IntroPlaza")
    ref = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Adela_IntroPaced")
    w.set_editor_property("concurrency_set", ref.get_editor_property("concurrency_set"))
    w.set_editor_property("sound_class_object", ref.get_editor_property("sound_class_object"))
    w.set_editor_property("virtualization_mode", unreal.VirtualizationMode.PLAY_WHEN_SILENT)
    w.set_editor_property("priority", ref.get_editor_property("priority"))
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/Audio/Relatos/A_Adela_IntroPlaza", False)
    res["dur"] = round(w.get_editor_property("duration"), 1); res["prio"] = w.get_editor_property("priority")
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        lb = a.get_actor_label()
        if lb == "Adela_Intro_Audio":
            c = a.get_component_by_class(unreal.AudioComponent); c.set_editor_property("sound", w)
            res["intro_sound"] = c.get_editor_property("sound").get_name()
        if lb == "RELATO_plaza":
            for c in a.get_components_by_class(unreal.AudioComponent):
                if c.get_name().startswith("Narration"):
                    c.set_editor_property("sound", None)
                    res["relato_plaza_sound"] = str(c.get_editor_property("sound"))
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, default=str))
