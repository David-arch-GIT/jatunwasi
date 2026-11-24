# 441_ue_revertir_mobiliario_convento.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: REVERTIR el amoblado del convento (439) a pedido de la usuaria ("no me gusta"):
#   - borra SOLO el actor CONV_MOBILIARIO (creado por 439; los objetos previos del convento no se tocan)
#   - quita la colision simple que 439/mob_colision agrego a mallas que antes NO tenian (0 formas):
#     bancas/mesa/arcon Megascans, cocina de barro, batan, aparador, tinaja, Kit_Cirio, lena
#     (estas mallas tambien se usan en Templo/Hacienda -> vuelven a su estado anterior)
#   - verifica que los actores previos del convento siguen (conteo) y guarda.
import unreal, json, traceback
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/revertir_convento.json"
MESHES = ["/Game/Megascans/3D_Assets/Old_Wooden_Bench_ucvpfirfa/S_Old_Wooden_Bench_ucvpfirfa_lod3",
          "/Game/Megascans/3D_Assets/Wooden_Table_veigfjmaw/S_Wooden_Table_veigfjmaw_lod3_Var1",
          "/Game/Megascans/3D_Assets/Wooden_Chest_vignaajva/S_Wooden_Chest_vignaajva_lod3_Var1",
          "/Game/JWN/TripoClean2/cocina_de_barro_hacienda/StaticMeshes/cocina_de_barro_hacienda",
          "/Game/JWN/TripoClean2/batan_de_piedra_hacienda/StaticMeshes/batan_de_piedra_hacienda",
          "/Game/JWN/Props/Furniture/G_Aparador/FN_Aparador/StaticMeshes/FN_Aparador",
          "/Game/JWN/Props/Vessels/G_V_Tinaja/V_Tinaja/StaticMeshes/V_Tinaja",
          "/Game/JWN/Templo/Kit_Cirio",
          "/Game/JWN/Props/Furniture/G_Lena/FN_Lena/StaticMeshes/FN_Lena"]
res = {"err": None}
try:
    n = 0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "CONV_MOBILIARIO":
            unreal.EditorLevelLibrary.destroy_actor(a); n += 1
    res["borrados"] = n
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    col = []
    for p in MESHES:
        sm = unreal.load_asset(p)
        before = sms.get_simple_collision_count(sm)
        if before > 0:
            sms.remove_collisions(sm)
            unreal.EditorAssetLibrary.save_loaded_asset(sm, False)
        col.append([p.split("/")[-1], before, sms.get_simple_collision_count(sm)])
    res["colision"] = col
    left = [a.get_actor_label() for a in unreal.EditorLevelLibrary.get_all_level_actors()
            if 3300 <= a.get_actor_location().x <= 8800 and 3200 <= a.get_actor_location().y <= 7000]
    res["actores_convento"] = len(left)
    res["previos_presentes"] = all(any(l == k for l in left) for k in ("CVT_Pozo", "CVT_Mesa", "CVT_Atril", "CVT_Cruz", "CVT_SanSeverino", "CVT_Catre_0", "VIT_Habito_Vitrina", "CONV_Altar", "PUERTA_Convento_A"))
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1200]
open(OUT, "w").write(json.dumps(res))
