# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-28
# Que hace: (UE) Borra el AppSK_Conv_Karisiri DUPLICADO flotante (Z alto), reaplica material+walk al que queda,
#           y oculta EN EL JUEGO los billboards viejos App_* (BP_Apparition_C) para que no se superpongan.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/limpiar.json"
res = {"borrados": [], "ocultos": [], "reaplicado": None, "err": []}
eas = unreal.EditorActorSubsystem()
acts = eas.get_all_level_actors()

# 1) duplicados de Karisiri: quedarse con el de menor Z, borrar los demas
kar = [a for a in acts if a.get_actor_label() == "AppSK_Conv_Karisiri"]
kar.sort(key=lambda a: a.get_actor_location().z)
survivor = kar[0] if kar else None
for a in kar[1:]:
    z = round(a.get_actor_location().z)
    eas.destroy_actor(a); res["borrados"].append("AppSK_Conv_Karisiri Z=%d" % z)

# 2) reaplicar material + walk al Karisiri superviviente
if survivor is not None:
    try:
        mi = unreal.load_asset("/Game/JWN/Apariciones/MI_Fant_Conv_Karisiri")
        walk = unreal.load_asset("/Game/JWN/Apariciones/Anim/Karisiri/karisiri_full/SkeletalMeshes/karisiri_fullkarisiri_Walk.karisiri_fullkarisiri_Walk")
        comp = survivor.skeletal_mesh_component
        comp.set_material(0, mi)
        comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = comp.get_editor_property("animation_data")
        ad.set_editor_property("anim_to_play", walk)
        ad.set_editor_property("saved_looping", True); ad.set_editor_property("saved_playing", True)
        comp.set_editor_property("animation_data", ad); comp.play(True)
        res["reaplicado"] = "AppSK_Conv_Karisiri Z=%d" % round(survivor.get_actor_location().z)
    except Exception as e:
        res["err"].append("reaplicar: %s" % e)

# 3) ocultar EN JUEGO los billboards viejos BP_Apparition (y editor)
for a in acts:
    try:
        if a.get_class().get_name() == "BP_Apparition_C":
            a.set_actor_hidden_in_game(True)
            try: a.set_is_temporarily_hidden_in_editor(True)
            except Exception: pass
            res["ocultos"].append(a.get_actor_label())
    except Exception as e:
        res["err"].append("ocultar: %s" % e)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("LIMPIAR done borrados=%d ocultos=%d" % (len(res["borrados"]), len(res["ocultos"])))
