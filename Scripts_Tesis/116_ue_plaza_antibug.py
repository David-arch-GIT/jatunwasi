# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Hace la PLAZA tan ligera como las otras zonas para que quitar/poner el visor NO se cuelgue ahi.
#   La plaza es abierta = se dibuja todo. Recorta MUY corto el bosque-impostor de fondo (lo mas caro de dibujar) y
#   el horizonte; adelgaza un poco el jardin/pasto. Mantiene lo cercano para que no se vea vacio. Guarda.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/plaza_antibug.json"
CX, CY, R = 0.0, -1000.0, 7000.0
res = {"forest_cull": 0, "horiz_cull": 0, "garden_thin": 0, "grass_thin": 0, "quitadas": 0, "err": []}
eas = unreal.EditorActorSubsystem()
for a in eas.get_all_level_actors():
    try:
        loc = a.get_actor_location()
    except Exception:
        continue
    if math.hypot(loc.x - CX, loc.y - CY) > R:
        continue
    lbl = a.get_actor_label(); n = lbl.lower()
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            c = comp.get_instance_count()
            if c < 20:
                continue
            if "hacfor" in n or "bosque" in n or "tree" in n or "arbol" in n or "forest" in n or "impostor" in n:
                # bosque de fondo: cull MUY corto (lo mas caro en la plaza abierta)
                comp.set_editor_property("instance_start_cull_distance", 1800)
                comp.set_editor_property("instance_end_cull_distance", 2800)
                res["forest_cull"] += 1
            elif "horiz" in n:
                comp.set_editor_property("instance_start_cull_distance", 8000)
                comp.set_editor_property("instance_end_cull_distance", 11000)
                res["horiz_cull"] += 1
            elif "garden" in n or "jardin" in n or "flower" in n or "fern" in n or "helecho" in n or "boxwood" in n or "seto" in n:
                comp.set_editor_property("instance_start_cull_distance", 2200)
                comp.set_editor_property("instance_end_cull_distance", 3200)
                # adelgazar 30% mas (mantener 70%)
                rem = [i for i in range(c) if (i % 100) >= 70]
                if rem:
                    comp.remove_instances(rem); res["quitadas"] += len(rem)
                res["garden_thin"] += 1
            elif "grass" in n or "pasto" in n or "cesped" in n:
                comp.set_editor_property("instance_start_cull_distance", 1200)
                comp.set_editor_property("instance_end_cull_distance", 2200)
                rem = [i for i in range(c) if (i % 100) >= 60]
                if rem:
                    comp.remove_instances(rem); res["quitadas"] += len(rem)
                res["grass_thin"] += 1
        except Exception as ex:
            res["err"].append("%s: %s" % (lbl, str(ex)[:50]))
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("PLAZA ANTIBUG forest=%d horiz=%d garden=%d grass=%d quit=%d" % (res["forest_cull"], res["horiz_cull"], res["garden_thin"], res["grass_thin"], res["quitadas"]))
