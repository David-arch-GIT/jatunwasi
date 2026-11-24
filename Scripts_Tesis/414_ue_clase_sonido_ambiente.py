# 414_ue_clase_sonido_ambiente.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: preparar el interruptor de SONIDO AMBIENTE para el visitante.
#   - SoundClass SCL_Ambiente (hija de la clase que ya usen los sonidos, o sin padre) asignada a los
#     beds AMB_* (plaza/convento/templo/hacienda/sala baile) y a la noche (grillos/lechuzas).
#     NO se tocan narraciones, relatos, cartelas, voz de Adela/Convai, apariciones, campanas ni pasos.
#   - SoundMix SMX_SinAmbiente: ajusta SCL_Ambiente a volumen 0 (fundido 0.6 s).
#   El Blueprint hace Push/Pop de este mix al pulsar el boton A (script/cableado aparte).
#   Antes: guarda el nivel (fuente nueva ya verificada por capturas).
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/clase_ambiente.json"
DST = "/Game/JWN/Audio/Noche"
WAVES = ["/Game/JWN/Audio/Ambient/SW_Amb_Plaza", "/Game/JWN/Audio/Ambient/SW_Amb_Convento", "/Game/JWN/Audio/Ambient/SW_Amb_Templo",
         "/Game/JWN/Audio/Ambient/SW_Amb_Hacienda", "/Game/JWN/Audio/Ambient/SW_Amb_SalaBaile",
         "/Game/JWN/Audio/Noche/SW_Grillos_Loop", "/Game/JWN/Audio/Noche/SW_Lechuza_Lejana_A", "/Game/JWN/Audio/Noche/SW_Lechuza_Lejana_B"]
res = {"err": None}
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    at = unreal.AssetToolsHelpers.get_asset_tools()
    prev = {}
    for w in WAVES:
        s = unreal.load_asset(w)
        c = s.get_editor_property("sound_class_object")
        prev[w] = c.get_path_name() if c else None
    res["prev_classes"] = prev
    parent = None
    others = set(v for v in prev.values() if v)
    if len(others) == 1:
        parent = unreal.load_asset(list(others)[0])
    p = DST + "/SCL_Ambiente"
    scl = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset("SCL_Ambiente", DST, unreal.SoundClass, unreal.SoundClassFactory())
    if parent and parent != scl:
        scl.set_editor_property("parent_class", parent)
    unreal.EditorAssetLibrary.save_loaded_asset(scl, False)
    for w in WAVES:
        s = unreal.load_asset(w)
        s.set_editor_property("sound_class_object", scl)
        unreal.EditorAssetLibrary.save_loaded_asset(s, False)
    p = DST + "/SMX_SinAmbiente"
    mix = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset("SMX_SinAmbiente", DST, unreal.SoundMix, unreal.SoundMixFactory())
    adj = unreal.SoundClassAdjuster()
    adj.set_editor_property("sound_class_object", scl)
    adj.set_editor_property("volume_adjuster", 0.0)
    adj.set_editor_property("pitch_adjuster", 1.0)
    mix.set_editor_property("sound_class_effects", [adj])
    mix.set_editor_property("fade_in_time", 0.6)
    mix.set_editor_property("fade_out_time", 0.6)
    unreal.EditorAssetLibrary.save_loaded_asset(mix, False)
    res["mix_effects"] = len(mix.get_editor_property("sound_class_effects"))
    res["assigned"] = [unreal.load_asset(w).get_editor_property("sound_class_object").get_name() for w in WAVES]
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res, indent=1))
