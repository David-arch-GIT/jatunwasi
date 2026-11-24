# 493_ue_separar_cartelas_retablo.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: Cartela_urkupina (0,13973,208) y Cartela_retablo (0,13997,272) estaban a 66 cm: al apuntar a
#   una se abrian LAS DOS (cono de 18 grados del BP_Cartela). Se separan sobre el retablo:
#   urkupina delante de la imagen (0,13925,150); retablo en la parte alta derecha (160,13930,320).
#   Desde cualquier punto a < 4.5 m quedan a > 25 grados -> se abre solo la que se apunta.
#   Ademas lista TODAS las parejas de cartelas a menos de 1.5 m. Respaldo del mapa. Guarda.
import unreal, json, math, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/separar_cartelas.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_separar_cartelas.umap")
    carts = [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_class().get_name() == "BP_Cartela_C"]
    by = {a.get_actor_label(): a for a in carts}
    by["Cartela_urkupina"].set_actor_location(unreal.Vector(0, 13925, 150), False, False)
    by["Cartela_retablo"].set_actor_location(unreal.Vector(160, 13930, 320), False, False)
    pares = []
    for i in range(len(carts)):
        for j in range(i + 1, len(carts)):
            A = carts[i].get_actor_location(); B = carts[j].get_actor_location()
            d = math.dist([A.x, A.y, A.z], [B.x, B.y, B.z])
            if d < 150: pares.append([carts[i].get_actor_label(), carts[j].get_actor_label(), round(d)])
    res["pares_cercanos"] = pares
    U = by["Cartela_urkupina"].get_actor_location(); R = by["Cartela_retablo"].get_actor_location()
    peor = 180.0
    for ox in range(-300, 301, 50):
        for oy in range(13450, 13901, 50):
            E = (ox, oy, 160.0)
            du = math.dist(E, (U.x, U.y, U.z)); dr = math.dist(E, (R.x, R.y, R.z))
            if du > 450 and dr > 450: continue
            vu = [(U.x - E[0]) / du, (U.y - E[1]) / du, (U.z - E[2]) / du]; vr = [(R.x - E[0]) / dr, (R.y - E[1]) / dr, (R.z - E[2]) / dr]
            ang = math.degrees(math.acos(max(-1, min(1, sum(a * b for a, b in zip(vu, vr))))))
            peor = min(peor, ang)
    res["angulo_minimo_entre_ellas_grados"] = round(peor, 1)
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
