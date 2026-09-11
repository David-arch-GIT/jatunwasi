# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Adelgaza el BOSQUE global (PCG_BosqueVol = 28040 inst = 62% de todo) al 55%, horizonte al 60%,
#   arbustos/pasto al 60%. Es la mayor ganancia de fluidez para TODAS las zonas. Ademas pone el PCG en GENERATE_ON_DEMAND
#   para que NO regenere y deshaga el adelgazamiento. Guarda. Reversible (respaldo hecho). Reporta conteos.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/adelgazar_bosque.json"
res = {"antes": 0, "despues": 0, "quitadas": 0, "comps": 0, "pcg_ondemand": 0, "err": []}
eas = unreal.EditorActorSubsystem()
def keep_for(lbl):
    n = lbl.lower()
    if "bosquevol" in n or "bosque" in n:
        return 0.55
    if "horiz" in n:
        return 0.60
    if "grass" in n or "pasto" in n or "shrub" in n or "arbust" in n:
        return 0.60
    return 1.0
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    kr = keep_for(lbl)
    if kr < 1.0:
        for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                n = comp.get_instance_count()
                if n < 40:
                    continue
                res["antes"] += n
                thr = int(kr * 100)
                to_remove = [i for i in range(n) if (i % 100) >= thr]
                if to_remove:
                    comp.remove_instances(to_remove)
                res["comps"] += 1
                res["quitadas"] += len(to_remove)
                res["despues"] += comp.get_instance_count()
            except Exception as ex:
                res["err"].append("%s: %s" % (lbl, str(ex)[:60]))
    # PCG: que no regenere en runtime/load
    for pcgc in a.get_components_by_class(unreal.PCGComponent):
        try:
            pcgc.set_editor_property("generation_trigger", unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND)
            pcgc.set_editor_property("regenerate_in_editor", False)
            res["pcg_ondemand"] += 1
        except Exception as ex:
            res["err"].append("pcg %s: %s" % (lbl, str(ex)[:60]))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ADELGAZAR BOSQUE antes=%d despues=%d quitadas=%d pcg=%d" % (res["antes"], res["despues"], res["quitadas"], res["pcg_ondemand"]))
