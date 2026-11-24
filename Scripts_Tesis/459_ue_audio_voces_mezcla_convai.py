# 459_ue_audio_voces_mezcla_convai.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: evitar que las voces grabadas choquen con Adela (Convai) y que el microfono las capte.
#   - Crea SCL_Voz (SoundClass) y la asigna a TODAS las SoundWave del grupo SC_Narracion (relatos,
#     leyendas, cartelas, voces grabadas de Adela) + VirtualizationMode PlayWhenSilent (a volumen 0 siguen
#     corriendo en silencio en vez de detenerse -> no se pierde la narracion).
#   - Crea SMX_Conversacion (Adela habla) y SMX_Escucha (usuario mantiene el grip): SCL_Voz -> 0,
#     SCL_Ambiente -> 0.4; fundido entrada 0.25 s, salida 1.0 s.
#   El cableado Push/Pop va en los BP (460). Respaldo = commit git 8a53c9d.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/voces_mezcla.json"
res = {"err": None, "asignadas": []}
try:
    at = unreal.AssetToolsHelpers.get_asset_tools(); eal = unreal.EditorAssetLibrary
    A = "/Game/JWN/Audio"
    if eal.does_asset_exist(A + "/SCL_Voz"):
        scl = unreal.load_asset(A + "/SCL_Voz")
    else:
        scl = at.create_asset("SCL_Voz", A, unreal.SoundClass, unreal.SoundClassFactory())
    eal.save_asset(A + "/SCL_Voz", False)
    amb = unreal.load_asset("/Game/JWN/Audio/Noche/SCL_Ambiente")
    def mix(name):
        p = A + "/" + name
        m = unreal.load_asset(p) if eal.does_asset_exist(p) else at.create_asset(name, A, unreal.SoundMix, unreal.SoundMixFactory())
        effs = []
        for cls, vol in ((scl, 0.0), (amb, 0.4)):
            e = unreal.SoundClassAdjuster(); e.set_editor_property("sound_class_object", cls); e.set_editor_property("volume_adjuster", vol)
            e.set_editor_property("apply_to_children", True)
            effs.append(e)
        m.set_editor_property("sound_class_effects", effs)
        m.set_editor_property("fade_in_time", 0.25); m.set_editor_property("fade_out_time", 1.0)
        m.set_editor_property("duration", -1.0)
        eal.save_asset(p, False)
        return [[x.get_editor_property("sound_class_object").get_name(), x.get_editor_property("volume_adjuster")] for x in m.get_editor_property("sound_class_effects")]
    res["SMX_Conversacion"] = mix("SMX_Conversacion")
    res["SMX_Escucha"] = mix("SMX_Escucha")
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    for path in ("/Game/JWN/Audio", "/Game/Cartelas/Audio"):
        for ad in ar.get_assets_by_path(path, True):
            if str(ad.asset_class_path.asset_name) != "SoundWave": continue
            w = ad.get_asset()
            conc = w.get_editor_property("concurrency_set")
            if not any("SC_Narracion" in str(c) for c in conc): continue
            w.set_editor_property("sound_class_object", scl)
            w.set_editor_property("virtualization_mode", unreal.VirtualizationMode.PLAY_WHEN_SILENT)
            eal.save_asset(str(ad.package_name), False)
            res["asignadas"].append(str(ad.asset_name))
    res["n"] = len(res["asignadas"])
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, default=str))
