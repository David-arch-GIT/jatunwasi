# 435_ue_audio_pozo_canto_moneda.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: preparar assets de las interacciones nuevas:
#   - importa SW_Pozo_Moneda, SW_Susurro_Leyenda, SW_Canto_Convento_Loop (/Game/JWN/Audio/Convento) y
#     A_Adela_Pozo (/Game/JWN/Audio/Relatos) copiando concurrencia/prioridad/clase de A_Relato_convento
#   - atenuaciones ATT_Susurro (1200/2500) y ATT_Canto (500/1400)
#   - M_Moneda: material dorado unlit (brilla de noche sin luces)
#   - CVT_Pozo: tag "PozoDeseos" + colision solo consulta (para el rayo del control)
#   - AmbientSound NOCHE_CantoConvento en la capilla (clase SCL_Ambiente -> se apaga con el boton A)
import unreal, json, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/audio_pozo.json"
res = {"err": None}
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    def imp(src, dst):
        t = unreal.AssetImportTask(); t.set_editor_property("filename", src); t.set_editor_property("destination_path", dst)
        t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
        at.import_asset_tasks([t])
    for n in ("SW_Pozo_Moneda", "SW_Susurro_Leyenda", "SW_Canto_Convento_Loop"):
        imp(ROOT + "/Saved/SynthAudio/" + n + ".wav", "/Game/JWN/Audio/Convento")
    imp(ROOT + "/Saved/NarrWav/A_Adela_Pozo.wav", "/Game/JWN/Audio/Relatos")
    ref = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Relato_convento")
    voz = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Adela_Pozo")
    for p in ("concurrency_set", "priority", "sound_class_object", "attenuation_settings", "virtualization_mode"):
        try:
            voz.set_editor_property(p, ref.get_editor_property(p))
        except Exception as e:
            res.setdefault("copy_warn", []).append(p)
    unreal.EditorAssetLibrary.save_loaded_asset(voz, False)
    res["voz_conc"] = [c.get_name() for c in voz.get_editor_property("concurrency_set")]
    canto = unreal.load_asset("/Game/JWN/Audio/Convento/SW_Canto_Convento_Loop")
    canto.set_editor_property("looping", True); canto.set_editor_property("virtualization_mode", unreal.VirtualizationMode.RESTART)
    canto.set_editor_property("sound_class_object", unreal.load_asset("/Game/JWN/Audio/Noche/SCL_Ambiente"))
    unreal.EditorAssetLibrary.save_loaded_asset(canto, False)
    def att(name, inner, fall):
        p = "/Game/JWN/Audio/Convento/" + name
        a = unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset(name, "/Game/JWN/Audio/Convento", unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
        s = a.get_editor_property("attenuation"); s.set_editor_property("attenuation_shape_extents", unreal.Vector(inner, 0, 0))
        s.set_editor_property("falloff_distance", fall); s.set_editor_property("spatialize", True); a.set_editor_property("attenuation", s)
        unreal.EditorAssetLibrary.save_loaded_asset(a, False); return a
    att("ATT_Susurro", 1200.0, 2500.0); a_canto = att("ATT_Canto", 500.0, 1400.0); att("ATT_Pozo", 400.0, 1600.0)
    # material moneda
    mp = "/Game/JWN/FX/M_Moneda"
    mel = unreal.MaterialEditingLibrary
    m = unreal.load_asset(mp) if unreal.EditorAssetLibrary.does_asset_exist(mp) else at.create_asset("M_Moneda", "/Game/JWN/FX", unreal.Material, unreal.MaterialFactoryNew())
    mel.delete_all_material_expressions(m)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    c = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -400, 0)
    c.set_editor_property("constant", unreal.LinearColor(1.0, 0.72, 0.25, 1.0))
    fr = mel.create_material_expression(m, unreal.MaterialExpressionFresnel, -400, 200)
    ad = mel.create_material_expression(m, unreal.MaterialExpressionAdd, -200, 100); ad.set_editor_property("const_b", 0.6)
    mel.connect_material_expressions(fr, "", ad, "A")
    mu = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -50, 0)
    mel.connect_material_expressions(c, "", mu, "A"); mel.connect_material_expressions(ad, "", mu, "B")
    mel.connect_material_property(mu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m); unreal.EditorAssetLibrary.save_asset(mp, False)
    # pozo
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "CVT_Pozo":
            tags = list(a.tags)
            if unreal.Name("PozoDeseos") not in tags: tags.append(unreal.Name("PozoDeseos"))
            a.tags = tags
            sm = a.get_component_by_class(unreal.StaticMeshComponent)
            res["pozo_coll_prev"] = str(sm.get_collision_enabled())
            sm.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
            sm.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_BLOCK)
            o, e = a.get_actor_bounds(False); res["pozo_bounds"] = [round(o.x), round(o.y), round(o.z), round(e.x), round(e.y), round(e.z)]
        if a.get_actor_label() == "NOCHE_CantoConvento":
            unreal.EditorLevelLibrary.destroy_actor(a)
    s = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.AmbientSound, unreal.Vector(8400, 4750, 320))
    s.set_actor_label("NOCHE_CantoConvento"); s.tags = [unreal.Name("RELLENO")]
    ac = s.get_editor_property("audio_component")
    ac.set_editor_property("sound", canto); ac.set_editor_property("attenuation_settings", a_canto)
    ac.set_editor_property("volume_multiplier", 0.35); ac.set_editor_property("auto_activate", True)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
