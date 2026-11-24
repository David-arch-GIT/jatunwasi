# 484_ue_adela_guia_configurar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: agregar UJWGuiaComponent ("GuiaJW", plugin JWGuia) a BP_GuiaInteractiva y configurarlo en la
#   instancia Adela_Convai con las rutas validadas (rutas_finales.json de 482/483):
#   tramo 0 Plaza->Templo, tramo 1 Templo->Convento (termina 7 m antes de las puertas), tramo 2 Convento->
#   Hacienda; frases de 476/477; animaciones idle / walk_sitio / talk; AudioIntro = Adela_Intro_Audio.
#   Respaldos previos del BP y del mapa. Compila, guarda BP y nivel.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/adela_guia_config.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/Blueprints/BP_GuiaInteractiva.uasset", ROOT + "/Saved/ClaudeBackups/BP_GuiaInteractiva_pre_guiajw.uasset")
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_guiajw.umap")
    R = json.loads(open(ROOT + "/Saved/ClaudeBackups/rutas_finales.json").read())
    V = lambda p: unreal.Vector(float(p[0]), float(p[1]), float(p[2]))
    bp = unreal.load_asset("/Game/JWN/Blueprints/BP_GuiaInteractiva")
    cls = unreal.load_class(None, "/Script/JWGuia.JWGuiaComponent")
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    hs = sds.k2_gather_subobject_data_for_blueprint(bp)
    ya = False
    for h in hs:
        o = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
        if o and o.get_class() == cls: ya = True
    if not ya:
        params = unreal.AddNewSubobjectParams(parent_handle=hs[0], new_class=cls, blueprint_context=bp)
        nh, fail = sds.add_new_subobject(params)
        res["add_fail"] = str(fail)
        sds.rename_subobject(nh, unreal.Text("GuiaJW"))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    res["bp_guardado"] = unreal.EditorAssetLibrary.save_asset("/Game/JWN/Blueprints/BP_GuiaInteractiva", False)

    acts = {a.get_actor_label(): a for a in unreal.EditorLevelLibrary.get_all_level_actors()}
    adela = acts["Adela_Convai"]
    A0 = adela.get_actor_location()
    est = R["estaciones"]
    # tramo 0: posicion actual de Adela -> camino Plaza->Templo -> estacion Templo
    t0 = [A0] + [V(p) for p in R["rutas"]["plaza_templo"][1:]] + [V(est["templo"]["pos"])]
    # tramo 1: estacion Templo -> camino Templo->Convento recortado en el punto 7 m antes de las puertas -> estacion Convento
    tc = [V(p) for p in R["rutas"]["templo_convento"]]
    corte = V(est["convento"]["camino"])
    t1 = [V(est["templo"]["pos"])]
    for i in range(len(tc)):
        t1.append(tc[i])
        if i + 1 < len(tc):
            ax, ay, bx, by = tc[i].x, tc[i].y, tc[i + 1].x, tc[i + 1].y
            L2 = (bx - ax) ** 2 + (by - ay) ** 2
            if L2 > 0:
                t = max(0.0, min(1.0, ((corte.x - ax) * (bx - ax) + (corte.y - ay) * (by - ay)) / L2))
                cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
                if math.hypot(cx - corte.x, cy - corte.y) < 30:
                    t1.append(corte); break
    t1.append(V(est["convento"]["pos"]))
    # tramo 2: estacion Convento -> camino exterior Convento->Hacienda -> estacion Hacienda
    t2 = [V(est["convento"]["pos"])] + [V(p) for p in R["rutas"]["convento_hacienda_ext"]] + [V(est["hacienda"]["pos"])]
    G = "/Game/JWN/Audio/Guia/"
    snd = lambda n: unreal.load_asset(G + n)
    tramos = []
    for pts, ini, preg in ((t0, "A_Guia_Sigueme_Templo", "A_Guia_Preguntas"), (t1, "A_Guia_Sigueme_Convento", "A_Guia_Preguntas"), (t2, "A_Guia_Sigueme_Hacienda", "A_Guia_Preguntas_Hacienda")):
        tr = unreal.JWGuiaTramo()
        tr.set_editor_property("puntos", pts); tr.set_editor_property("frase_inicio", snd(ini)); tr.set_editor_property("frase_preguntas", snd(preg))
        tramos.append(tr)
    def comp():
        return [c for c in adela.get_components_by_class(cls)][0]
    c = comp(); c.set_editor_property("tramos", tramos)
    c = comp(); c.set_editor_property("frase_no_te_quedes", snd("A_Guia_NoTeQuedes"))
    D = "/Game/JWN/Characters/AdelaFinal/"
    c = comp(); c.set_editor_property("anim_idle", unreal.load_asset(D + "A_Adela_idle"))
    c = comp(); c.set_editor_property("anim_walk", unreal.load_asset(D + "A_Adela_walk_sitio"))
    c = comp(); c.set_editor_property("anim_talk", unreal.load_asset(D + "A_Adela_talk"))
    c = comp(); c.set_editor_property("audio_intro", acts["Adela_Intro_Audio"])
    c = comp()
    res["verif"] = {"tramos": [len(t.get_editor_property("puntos")) for t in c.get_editor_property("tramos")],
                    "frases": [[t.get_editor_property("frase_inicio").get_name(), t.get_editor_property("frase_preguntas").get_name()] for t in c.get_editor_property("tramos")],
                    "no_te_quedes": c.get_editor_property("frase_no_te_quedes").get_name(),
                    "anims": [c.get_editor_property(k).get_name() for k in ("anim_idle", "anim_walk", "anim_talk")],
                    "audio_intro": c.get_editor_property("audio_intro").get_actor_label(),
                    "salon": str(c.get_editor_property("salon_pos"))}
    res["largos_m"] = [round(sum(math.hypot(p[i].x - p[i - 1].x, p[i].y - p[i - 1].y) for i in range(1, len(p))) / 100, 1) for p in (t0, t1, t2)]
    res["nivel_guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, default=str))
