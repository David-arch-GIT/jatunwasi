# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-14
# Que hace: (UE) PASO 1 (reversible): las 3 criaturas con rig (AppSK_*) dejan de estar congeladas -> Idle en LOOP
#   (respiran) en vez del frame 0 de Walk. Y DESACTIVA el InterpToMovementComponent (el movimiento robotico lineal).
#   Encuentra el Idle de cada criatura por nombre. Guarda. Reversible (volver a Walk / reactivar interp).
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/criaturas_idle.json"
res = {"ok": [], "err": []}
eas = unreal.EditorActorSubsystem()
ar = unreal.AssetRegistryHelpers.get_asset_registry()
# mapa criatura -> idle sequence
idle_by = {}
for a in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine", "AnimSequence"), True):
    p = str(a.package_name); nm = p.split("/")[-1].lower()
    if "idle" not in nm: continue
    for k in ["karisiri", "condenado", "duende"]:
        if k in nm and k not in idle_by:
            idle_by[k] = p
res["idle_encontrados"] = idle_by
for a in eas.get_all_level_actors():
    lab = a.get_actor_label()
    if not lab.startswith("AppSK_"):
        continue
    creature = None
    for k in ["karisiri", "condenado", "duende"]:
        if k in lab.lower():
            creature = k
    if not creature or creature not in idle_by:
        res["err"].append("sin idle: " + lab); continue
    idle = unreal.EditorAssetLibrary.load_asset(idle_by[creature])
    # 1) idle en loop (single node)
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        try:
            c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            spd = unreal.SingleAnimationPlayData()
            spd.set_editor_property("anim_to_play", idle)
            spd.set_editor_property("saved_looping", True)
            spd.set_editor_property("saved_playing", True)
            spd.set_editor_property("saved_play_rate", 1.0)
            c.set_editor_property("animation_data", spd)
            res["ok"].append(lab + " -> Idle loop")
        except Exception as e:
            res["err"].append(lab + " idle:" + str(e)[:40])
    # 2) desactivar interp robotico
    for c in a.get_components_by_class(unreal.InterpToMovementComponent):
        try:
            c.set_active(False, True)
            c.set_editor_property("auto_activate", False)
            res["ok"].append(lab + " -> interp OFF")
        except Exception as e:
            res["err"].append(lab + " interp:" + str(e)[:40])
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
les.save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("CRIATURAS IDLE ok=%d err=%d" % (len(res["ok"]), len(res["err"])))
