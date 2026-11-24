# 507_ue_cartela_san_severino.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: crear la cartela de San Severino (pedido de la usuaria) junto al relicario CVT_SanSeverino.
#   1) importa Tex/san_severino.png y Audio/san_severino.wav copiando los ajustes de altar_convento
#      (textura: compresion/mips/grupo/streaming; sonido: SCL_Voz + SC_Narracion + atenuacion).
#   2) MI_Cart_san_severino = copia de MI_Cart_altar_convento con la textura nueva.
#   3) duplica el actor Cartela_altar_convento -> Cartela_san_severino, con material y audio propios,
#      ubicado entre el punto caminable mas cercano y el relicario (alcanzable: < 4.5 m de la mano).
#   Respaldo del mapa antes. Guarda nivel y assets.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cartela_sansev_507.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None, "pasos": []}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_sansev.umap")
    at = unreal.AssetToolsHelpers.get_asset_tools()
    def importar(src, dest):
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", src); t.set_editor_property("destination_path", dest)
        t.set_editor_property("replace_existing", True); t.set_editor_property("automated", True); t.set_editor_property("save", False)
        at.import_asset_tasks([t])
        return t.get_editor_property("imported_object_paths")
    res["tex_imp"] = list(importar(ROOT + "/Content/Cartelas/Tex/san_severino.png", "/Game/Cartelas/Tex"))
    res["snd_imp"] = list(importar(ROOT + "/Content/Cartelas/Audio/san_severino.wav", "/Game/Cartelas/Audio"))
    tex = unreal.load_asset("/Game/Cartelas/Tex/san_severino"); tref = unreal.load_asset("/Game/Cartelas/Tex/altar_convento")
    for p in ("compression_settings", "mip_gen_settings", "lod_group", "never_stream", "srgb", "max_texture_size", "filter", "address_x", "address_y", "compression_quality"):
        try:
            tex.set_editor_property(p, tref.get_editor_property(p))
        except Exception as e:
            res["pasos"].append("tex %s: %s" % (p, str(e)[:60]))
    snd = unreal.load_asset("/Game/Cartelas/Audio/san_severino"); sref = unreal.load_asset("/Game/Cartelas/Audio/altar_convento")
    for p in ("sound_class_object", "concurrency_set", "attenuation_settings", "volume", "pitch", "virtualization_mode", "loading_behavior", "priority"):
        try:
            snd.set_editor_property(p, sref.get_editor_property(p))
        except Exception as e:
            res["pasos"].append("snd %s: %s" % (p, str(e)[:60]))
    res["snd_sc"] = snd.get_editor_property("sound_class_object").get_name(); res["snd_conc"] = [c.get_name() for c in snd.get_editor_property("concurrency_set")]
    res["dur"] = round(snd.get_editor_property("duration"), 1)
    mi_path = "/Game/Cartelas/Tex/MI_Cart_san_severino"
    if not unreal.EditorAssetLibrary.does_asset_exist(mi_path):
        unreal.EditorAssetLibrary.duplicate_asset("/Game/Cartelas/Tex/MI_Cart_altar_convento", mi_path)
    mi = unreal.load_asset(mi_path)
    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi, "Cartela", tex)
    for pth in ("/Game/Cartelas/Tex/san_severino", "/Game/Cartelas/Audio/san_severino", mi_path):
        unreal.EditorAssetLibrary.save_asset(pth, False)
    # ---- actor
    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    if "Cartela_san_severino" in acts:
        nuevo = acts["Cartela_san_severino"]
    else:
        unreal.EditorLevelLibrary.set_selected_level_actors([acts["Cartela_altar_convento"]])
        nuevo = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).duplicate_actor(acts["Cartela_altar_convento"], unreal.EditorLevelLibrary.get_editor_world(), unreal.Vector(0, 0, 0))
        nuevo.set_actor_label("Cartela_san_severino")
    w = unreal.EditorLevelLibrary.get_editor_world()
    S = acts["CVT_SanSeverino"].get_actor_location(); res["santo"] = [round(S.x), round(S.y), round(S.z)]
    # punto caminable mas cercano al santo
    best = None
    for k in range(24):
        ang = k * math.pi / 12
        for dd in (100, 150, 200, 250, 300, 350, 400, 500, 600):
            r = unreal.NavigationSystemV1.project_point_to_navigation(w, unreal.Vector(S.x + dd * math.cos(ang), S.y + dd * math.sin(ang), 60), None, None, unreal.Vector(10, 10, 150))
            p = r[0] if isinstance(r, tuple) else r
            if p is None or (p.x == 0 and p.y == 0): continue
            d = math.hypot(p.x - S.x, p.y - S.y)
            if best is None or d < best[1]: best = (p, d)
    P = best[0]; res["caminable"] = [round(P.x), round(P.y), round(P.z)]; res["dist_caminable_santo"] = round(best[1])
    # cartela sobre el rayo caminable->santo, a ~2.0 m del caminable (sin pasar el santo menos 60 cm)
    dx, dy = S.x - P.x, S.y - P.y; L = math.hypot(dx, dy)
    d = min(200.0, max(60.0, L - 60.0))
    C = unreal.Vector(P.x + dx / L * d, P.y + dy / L * d, 150)
    nuevo.set_actor_location(C, False, False)
    for c in nuevo.get_components_by_class(unreal.StaticMeshComponent):
        if c.get_name().startswith("Panel"):
            c.set_material(0, mi)
            c.set_editor_property("relative_location", unreal.Vector(0, 0, 0))
    nuevo = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == "Cartela_san_severino"][0]
    for c in nuevo.get_components_by_class(unreal.AudioComponent):
        c.set_editor_property("sound", snd)
    L2 = nuevo.get_actor_location(); res["cartela"] = [round(L2.x), round(L2.y), round(L2.z)]
    res["dist_mano"] = round(math.dist([P.x, P.y, P.z + 120], [L2.x, L2.y, L2.z]))
    res["dist_otras"] = sorted([(round(math.dist([L2.x, L2.y], [a.get_actor_location().x, a.get_actor_location().y])), a.get_actor_label()) for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == "BP_Cartela_C" and a != nuevo])[:3]
    chk = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == "Cartela_san_severino"][0]
    res["chk_mat"] = [c.get_materials()[0].get_name() for c in chk.get_components_by_class(unreal.StaticMeshComponent) if c.get_name().startswith("Panel")]
    res["chk_snd"] = [c.sound.get_name() if c.sound else None for c in chk.get_components_by_class(unreal.AudioComponent)]
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))

