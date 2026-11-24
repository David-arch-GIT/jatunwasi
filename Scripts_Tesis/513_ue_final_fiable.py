# 513_ue_final_fiable.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: la usuaria entro al salon y "no salio el final". Causas halladas:
#   (1) Trig_HaciendaFin (caja sin girar) empezaba en x -7945 y la puerta de la cortina esta en x -7911:
#       quien entra y se queda cerca de la entrada NO lo dispara. Ahora la caja sigue el giro del edificio
#       (yaw 12.1) y cubre todo el salon oeste en coordenadas locales lx -1650..-650 (la cortina esta en
#       lx -855..-745), ly 840..1460 (entre el muro sur, cara salon 828, y el norte 1473): no toca la galeria.
#   (2) la despedida de Adela (A_Adela_Despedida) comparte la concurrencia SC_Narracion (max 1, stop lowest
#       priority): si sonaba otra narracion podia ser rechazada -> prioridad 4.0 (gana siempre al final).
#   (El Delay de 75 s -> 30 s se cambia en el grafo con la API de blueprints, ver 514.)
#   Respaldo del mapa. Guarda nivel y sonido.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/final_fiable.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_final_fiable.umap")
    O = (-7000.0, -2500.0); YAW = 12.1; A = math.radians(YAW); c, s = math.cos(A), math.sin(A)
    lx, ly = -1150.0, 1150.0
    C = unreal.Vector(O[0] + lx * c - ly * s, O[1] + lx * s + ly * c, 575.0)
    g = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == "BP_GestorRecorrido_C"][0]
    t = [x for x in g.get_components_by_class(unreal.BoxComponent) if x.get_name() == "Trig_HaciendaFin"][0]
    t.set_editor_property("relative_location", C)          # el actor gestor esta en el origen sin giro
    r = unreal.Rotator(); r.yaw = YAW
    t.set_editor_property("relative_rotation", r)
    t.set_editor_property("box_extent", unreal.Vector(500, 310, 145))
    t = [x for x in g.get_components_by_class(unreal.BoxComponent) if x.get_name() == "Trig_HaciendaFin"][0]
    res["trig"] = [str(t.get_editor_property("relative_location")), str(t.get_editor_property("relative_rotation")), str(t.get_editor_property("box_extent"))]
    # dentro / fuera: puerta de la cortina (adentro) y galeria frente a ella (afuera)
    def dentro(p):
        T = t.get_world_transform(); q = T.inverse_transform_location(p); e = t.get_editor_property("box_extent")
        return abs(q.x) <= e.x and abs(q.y) <= e.y and abs(q.z) <= e.z
    def mundo(a, b, z): return unreal.Vector(O[0] + a * c - b * s, O[1] + a * s + b * c, z)
    res["prueba"] = {"recien_entrado_lx-800_ly870": dentro(mundo(-800, 870, 600)), "centro_salon": dentro(mundo(-1200, 1150, 600)),
                     "galeria_lx-800_ly700": dentro(mundo(-800, 700, 600)), "pasillo_este_lx-300": dentro(mundo(-300, 1150, 600)),
                     "planta_baja": dentro(mundo(-1200, 1150, 150))}
    snd = unreal.load_asset("/Game/JWN/Audio/Relatos/A_Adela_Despedida")
    res["prio_antes"] = snd.get_editor_property("priority")
    snd.set_editor_property("priority", 4.0)
    res["prio"] = snd.get_editor_property("priority")
    res["snd_guardado"] = unreal.EditorAssetLibrary.save_loaded_asset(snd, False)
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))

# NOTA: al ejecutarlo, el giro y el tamano de la caja se perdieron (el actor se reconstruye tras cada set);
#   se reaplicaron volviendo a buscar el componente antes de CADA set_editor_property (verificado: yaw 12.1, (500,310,145)).
