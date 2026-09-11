# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Configura el idle en bucle en los AppSK_* (API correcta), inspecciona SingleAnimationPlayData, reporta altura de cada mesh y Z actual para ajustar suelo.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_anim.json"
res = {"props": [], "actors": []}

# introspeccion de SingleAnimationPlayData
try:
    sd = unreal.SingleAnimationPlayData()
    res["props"] = [p for p in dir(sd) if not p.startswith("__")][:60]
except Exception as e:
    res["props"] = ["ERR %s" % e]

IDLE = {
 "AppSK_Conv_Karisiri":  "/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Idle.karisiri_fullkarisiri_Idle",
 "AppSK_Conv_Condenado": "/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Idle.condenado_fullcondenado_Idle",
 "AppSK_Hac_Duende":     "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle",
 "AppSK_Plz_Duende":     "/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle",
}
eas = unreal.EditorActorSubsystem()
by_label = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for label, idle_path in IDLE.items():
    a = by_label.get(label)
    if a is None:
        res["actors"].append({"label": label, "err": "no existe"}); continue
    comp = a.skeletal_mesh_component
    idle = unreal.load_asset(idle_path)
    comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    info = {"label": label}
    try:
        ad = comp.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", idle)
        for pk in ["b_saved_looping", "saved_looping", "looping", "b_looping"]:
            try: ad.set_editor_property(pk, True); info["loop_prop"] = pk; break
            except Exception: pass
        for pk in ["b_saved_playing", "saved_playing", "playing", "b_playing"]:
            try: ad.set_editor_property(pk, True); info["play_prop"] = pk; break
            except Exception: pass
        comp.set_editor_property("animation_data", ad)
    except Exception as e:
        info["ad_err"] = str(e)
    try:
        comp.play(True)
    except Exception as e:
        info["play_err"] = str(e)
    # altura del mesh y bounds para ajustar suelo
    try:
        b = a.get_actor_bounds(False)  # (origin, extent)
        info["z"] = round(a.get_actor_location().z)
        info["ext_z"] = round(b[1].z, 1)
        info["origin_z"] = round(b[0].z, 1)
    except Exception as e:
        info["bounds_err"] = str(e)
    res["actors"].append(info)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("FIX ANIM done")
