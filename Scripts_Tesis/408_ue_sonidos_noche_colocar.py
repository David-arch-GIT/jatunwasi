# 408_ue_sonidos_noche_colocar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: importar los 5 WAV sintetizados por 406 a /Game/JWN/Audio/Noche y colocarlos:
#   - Grillos: 8 AmbientSound en los campos (RELLENO_Campos), lejos (>1200) de las 3 leyendas,
#     bucle, atenuacion ATT_Grillos (interior 700 / caida 2300), volumen bajo.
#   - Lechuza: 2 AmbientSound en bordes del bosque (variantes A y B), ATT_Lechuza (1500 / 7000).
#   - Campanas y pasos: solo import + ajustes (se cablean por Blueprint en pasos aparte).
#   - Componente de audio "Pasos" (2D, volumen 0, auto-activo) agregado a BP_XRPawn.
#   Respaldo previo: copia del .umap, BP_XRPawn y BP_GestorRecorrido en Saved/ClaudeBackups.
#   Todos los actores nuevos con label NOCHE_* y tag RELLENO (reversibles). Quest: sin
#   concurrencia de narracion (no usan SC_Narracion), virtualizacion Restart fuera de rango.
import unreal, json, math, random, shutil, traceback, os
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/sonidos_noche.json"
SRC = ROOT + r"/Saved/SynthAudio"
DST = "/Game/JWN/Audio/Noche"
res = {"err": None, "steps": []}
LEG = [(3881, 3281), (1031, 8380), (4000, 1700), (-4135, 731), (325, 7596), (-4310, -143)]
BLD = [(0, 11700, 1800), (6300, 5100, 2200), (-6500, -1300, 2600), (0, -1000, 1800)]  # templo, convento, hacienda, plaza (radio de exclusion)
try:
    bk = ROOT + "/Saved/ClaudeBackups/"
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", bk + "MAP_CLEAN_pre_sonidos_noche_20261124.umap")
    shutil.copy2(ROOT + "/Content/XRFramework/Blueprints/BP_XRPawn.uasset", bk + "BP_XRPawn_pre_pasos.uasset")
    shutil.copy2(ROOT + "/Content/JWN/Blueprints/BP_GestorRecorrido.uasset", bk + "BP_GestorRecorrido_pre_campanas.uasset")
    res["steps"].append("backup")

    # ---------- import ----------
    tasks = []
    for nm in ("SW_Grillos_Loop", "SW_Lechuza_Lejana_A", "SW_Lechuza_Lejana_B", "SW_Campanas_Templo", "SW_Pasos_Grava_Loop"):
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", SRC + "/" + nm + ".wav")
        t.set_editor_property("destination_path", DST)
        t.set_editor_property("automated", True)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("save", True)
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    W = {}
    for nm in ("SW_Grillos_Loop", "SW_Lechuza_Lejana_A", "SW_Lechuza_Lejana_B", "SW_Campanas_Templo", "SW_Pasos_Grava_Loop"):
        W[nm] = unreal.load_asset(DST + "/" + nm)
        if W[nm] is None:
            raise Exception("no importo " + nm)
    for nm in ("SW_Grillos_Loop", "SW_Lechuza_Lejana_A", "SW_Lechuza_Lejana_B", "SW_Pasos_Grava_Loop"):
        W[nm].set_editor_property("looping", True)
    for nm in ("SW_Grillos_Loop", "SW_Lechuza_Lejana_A", "SW_Lechuza_Lejana_B"):
        W[nm].set_editor_property("virtualization_mode", unreal.VirtualizationMode.RESTART)
    W["SW_Pasos_Grava_Loop"].set_editor_property("virtualization_mode", unreal.VirtualizationMode.PLAY_WHEN_SILENT)
    for nm, w in W.items():
        unreal.EditorAssetLibrary.save_loaded_asset(w, False)
    res["steps"].append("import")

    # ---------- atenuaciones ----------
    at = unreal.AssetToolsHelpers.get_asset_tools()
    def make_att(name, inner, fall):
        path = DST + "/" + name
        a = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else \
            at.create_asset(name, DST, unreal.SoundAttenuation, unreal.SoundAttenuationFactory())
        s = a.get_editor_property("attenuation")
        s.set_editor_property("attenuate", True)
        s.set_editor_property("spatialize", True)
        s.set_editor_property("attenuation_shape", unreal.AttenuationShape.SPHERE)
        s.set_editor_property("attenuation_shape_extents", unreal.Vector(inner, 0, 0))
        s.set_editor_property("falloff_distance", fall)
        a.set_editor_property("attenuation", s)
        unreal.EditorAssetLibrary.save_loaded_asset(a, False)
        return a
    A_GR = make_att("ATT_Grillos", 700.0, 2300.0)
    A_LE = make_att("ATT_Lechuza", 1500.0, 7000.0)
    A_CA = make_att("ATT_Campanas", 2500.0, 9000.0)
    res["steps"].append("att")

    # ---------- grillos: 8 puntos repartidos en los campos ----------
    inv = json.load(open(ROOT + "/Saved/ClaudeBackups/inv_sonidos.json"))
    cand = []
    for x, y, z in inv["campos_pts"]:
        if any(math.hypot(x - lx, y - ly) < 1200 for lx, ly in LEG):
            continue
        if any(math.hypot(x - bx, y - by) < r for bx, by, r in BLD):
            continue
        if not (-10500 < x < 10000 and -6000 < y < 17500):  # dentro de la zona recorrible (no en el horizonte)
            continue
        cand.append((x, y, z))
    random.seed(408)
    pick = [random.choice(cand)] if cand else []
    while len(pick) < 8 and cand:  # muestreo del punto mas lejano -> buena dispersion
        best = max(cand, key=lambda p: min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in pick))
        pick.append(best)
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("NOCHE_"):
            unreal.EditorLevelLibrary.destroy_actor(a)
    def amb(label, wave, att, loc, vol):
        s = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.AmbientSound, loc)
        s.set_actor_label(label); s.tags = [unreal.Name("RELLENO")]
        c = s.get_editor_property("audio_component")
        c.set_editor_property("sound", wave)
        c.set_editor_property("attenuation_settings", att)
        c.set_editor_property("volume_multiplier", vol)
        c.set_editor_property("auto_activate", True)
        return s
    for i, (x, y, z) in enumerate(pick):
        amb("NOCHE_Grillos_%d" % i, W["SW_Grillos_Loop"], A_GR, unreal.Vector(x, y, z + 40), 0.45)
    res["grillos"] = [[round(p[0]), round(p[1])] for p in pick]

    # ---------- lechuzas: bordes del bosque, lejos del camino ----------
    amb("NOCHE_Lechuza_A", W["SW_Lechuza_Lejana_A"], A_LE, unreal.Vector(-9500, 7500, 1400), 0.55)
    amb("NOCHE_Lechuza_B", W["SW_Lechuza_Lejana_B"], A_LE, unreal.Vector(9000, -3500, 1400), 0.55)
    res["steps"].append("ambient")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    res["steps"].append("level_saved")

    # ---------- componente Pasos en BP_XRPawn ----------
    bp = unreal.load_asset("/Game/XRFramework/Blueprints/BP_XRPawn")
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    handles = sds.k2_gather_subobject_data_for_blueprint(bp)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    exist = None
    for h in handles:
        d = lib.get_data(h)
        if str(lib.get_variable_name(d)) == "Pasos":
            exist = h
    if exist is None:
        hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=handles[0],
            new_class=unreal.AudioComponent, blueprint_context=bp))
        sds.rename_subobject(hh, unreal.Text("Pasos"))
        exist = hh
    comp = lib.get_object(lib.get_data(exist))
    comp.set_editor_property("sound", W["SW_Pasos_Grava_Loop"])
    comp.set_editor_property("auto_activate", True)
    comp.set_editor_property("volume_multiplier", 0.0)
    comp.set_editor_property("allow_spatialization", False)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    res["pasos_comp"] = comp.get_name()
    res["steps"].append("pasos_comp")
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
