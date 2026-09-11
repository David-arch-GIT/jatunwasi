# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) FINALIZACION LIGERA (sin crear/borrar/recompilar el master -> no cuelga).
#   Ajusta params de pulso en las 4 MIs (aparicion espaciada ~5s cada ~40s, escalonadas), pone animacion IDLE
#   (fantasma que acecha sutil, no marcha en el sitio), sube el Condenado al suelo. NO guarda el nivel (eso lo hace otro paso).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finalizar.json"
res = {"steps": [], "err": []}
mel = unreal.MaterialEditingLibrary
# params de pulso por MI (PhaseOffset escalonado)
PH = {"Hac_Duende": 0.0, "Plz_Duende": 11.0, "Conv_Condenado": 22.0, "Conv_Karisiri": 33.0}
for n, ph in PH.items():
    p = "/Game/JWN/Apariciones/MI_Fant_" + n
    try:
        mi = unreal.load_asset(p)
        mel.set_material_instance_scalar_parameter_value(mi, "Speed", 0.025)
        mel.set_material_instance_scalar_parameter_value(mi, "PulseGain", 2.5)
        mel.set_material_instance_scalar_parameter_value(mi, "PulseBiasNeg", -1.4)
        mel.set_material_instance_scalar_parameter_value(mi, "MaxOpacity", 0.95)
        mel.set_material_instance_scalar_parameter_value(mi, "EmissiveBoost", 1.6)
        mel.set_material_instance_scalar_parameter_value(mi, "PhaseOffset", ph)
        unreal.EditorAssetLibrary.save_asset(p)
        res["steps"].append("MI " + n)
    except Exception as e:
        res["err"].append("MI %s: %s" % (n, e))
# animacion IDLE + condenado al suelo
IDLE = {"AppSK_Hac_Duende":"/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle",
        "AppSK_Plz_Duende":"/Game/JWN/Apariciones/Anim/Duende/duende_full/SkeletalMeshes/duende_fullduende_Idle.duende_fullduende_Idle",
        "AppSK_Conv_Condenado":"/Game/JWN/Apariciones/Anim/Condenado/condenado_full/SkeletalMeshes/condenado_fullcondenado_Idle.condenado_fullcondenado_Idle",
        "AppSK_Conv_Karisiri":"/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Idle.karisiri_fullkarisiri_Idle"}
eas = unreal.EditorActorSubsystem()
by = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
for label, idlep in IDLE.items():
    try:
        a = by.get(label)
        if a is None: res["err"].append("no " + label); continue
        comp = a.skeletal_mesh_component
        idle = unreal.load_asset(idlep)
        comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = comp.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", idle)
        ad.set_editor_property("saved_looping", True); ad.set_editor_property("saved_playing", True)
        comp.set_editor_property("animation_data", ad); comp.play(True)
        if label == "AppSK_Conv_Condenado":
            b = a.get_actor_bounds(False); bottom = b[0].z - b[1].z
            l = a.get_actor_location(); a.set_actor_location(unreal.Vector(l.x, l.y, l.z + (12.0 - bottom)), False, True)
            res["steps"].append("condenado subido bottom_antes=%d" % round(bottom))
        res["steps"].append("anim " + label)
    except Exception as e:
        res["err"].append("anim %s: %s" % (label, e))
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("FINALIZAR done")
