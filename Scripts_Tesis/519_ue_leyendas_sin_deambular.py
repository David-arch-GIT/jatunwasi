# 519_ue_leyendas_sin_deambular.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-25
# Proposito: complemento de 518 en las 3 instancias Cria_* (BP_CriaturaViva):
#   VelMin = VelMax = 0 (el BP ya no les da velocidad de deambular), use_controller_rotation_yaw = False
#   (la IA no las hace girar sin rumbo), IdleAnim/WalkAnim de cada criatura y animacion inicial = REPOSO
#   (antes "caminaban en el sitio"). Respaldo del mapa. Guarda.
import unreal, json, traceback, shutil
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/leyendas_519.json"
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
BASE = "/Game/JWN/Apariciones/Anim/"
ANIMS = {"Cria_Karisiri": ("Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_", ),
         "Cria_Condenado": ("Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_", ),
         "Cria_Duende": ("Duende/duende_full/SkeletalMeshes/duende_fullduende_", )}
res = {"err": None}
try:
    shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_leyendas_reposo.umap")
    def cria(lb): return [a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label() == lb][0]
    for lb, (pref,) in ANIMS.items():
        idle = unreal.load_asset(BASE + pref + "Idle"); walk = unreal.load_asset(BASE + pref + "Walk")
        d = {"antes_idle": str(cria(lb).get_editor_property("IdleAnim")), "antes_walk": str(cria(lb).get_editor_property("WalkAnim"))}
        cria(lb).set_editor_property("VelMin", 0.0)
        cria(lb).set_editor_property("VelMax", 0.0)
        cria(lb).set_editor_property("use_controller_rotation_yaw", False)
        cria(lb).set_editor_property("IdleAnim", idle)
        cria(lb).set_editor_property("WalkAnim", walk)
        m = cria(lb).get_component_by_class(unreal.SkeletalMeshComponent)
        ad = m.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", idle); ad.set_editor_property("saved_looping", True); ad.set_editor_property("saved_playing", True)
        m.set_editor_property("animation_data", ad)
        a = cria(lb); m = a.get_component_by_class(unreal.SkeletalMeshComponent)
        d.update({"VelMin": a.get_editor_property("VelMin"), "VelMax": a.get_editor_property("VelMax"), "ctrl_yaw": a.get_editor_property("use_controller_rotation_yaw"),
                  "IdleAnim": a.get_editor_property("IdleAnim").get_name() if a.get_editor_property("IdleAnim") else None,
                  "WalkAnim": a.get_editor_property("WalkAnim").get_name() if a.get_editor_property("WalkAnim") else None,
                  "anim_inicial": m.get_editor_property("animation_data").get_editor_property("anim_to_play").get_name()})
        res[lb] = d
    res["guardado"] = unreal.EditorLoadingAndSavingUtils.save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res, indent=1))
