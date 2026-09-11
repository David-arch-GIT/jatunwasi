# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Adelgaza la CANTIDAD de instancias pesadas en la plaza (frame mucho mas ligero = deja de colgar + fluido):
#   bosque impostores -> deja 40% (quita 60%), jardin -> deja 55%, pasto -> deja 60%. Solo en el area de la plaza.
#   Usa remove_instances (lote) por eficiencia. Respaldo del nivel ya hecho. Guarda. Reporta conteos.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/adelgazar_plaza.json"
CX, CY, R = 0.0, -1000.0, 6500.0
res = {"comps": 0, "quitadas": 0, "antes": 0, "despues": 0, "detalle": [], "err": []}
eas = unreal.EditorActorSubsystem()
def keep_ratio(nm):
    n = nm.lower()
    if "hacfor" in n or "bosque" in n or "tree" in n or "arbol" in n or "forest" in n or "impostor" in n:
        return 0.40
    if "grass" in n or "pasto" in n or "cesped" in n:
        return 0.60
    if "garden" in n or "jardin" in n or "boxwood" in n or "seto" in n or "flower" in n or "fern" in n or "helecho" in n:
        return 0.55
    return 1.0  # no tocar lo demas
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x - CX, loc.y - CY) > R:
        continue
    lbl = a.get_actor_label()
    kr = keep_ratio(lbl)
    if kr >= 1.0:
        continue
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            n = comp.get_instance_count()
            if n < 60:
                continue
            res["antes"] += n
            # indices a quitar: mantener 1 de cada round(1/(1-kr))... mas simple: quitar si (i % 100) >= kr*100
            thr = int(kr * 100)
            to_remove = [i for i in range(n) if (i % 100) >= thr]
            if to_remove:
                comp.remove_instances(to_remove)
            res["comps"] += 1
            res["quitadas"] += len(to_remove)
            res["despues"] += comp.get_instance_count()
        except Exception as ex:
            res["err"].append("%s: %s" % (lbl, str(ex)[:80]))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("ADELGAZAR PLAZA comps=%d quitadas=%d antes=%d despues=%d" % (res["comps"], res["quitadas"], res["antes"], res["despues"]))
