# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-01
# Que hace: (UE) Baja el costo GPU de la plaza (frames mas cortos = arregla el deadlock del re-don + fluidez):
#   mantiene las 6 luces LP_ (plaza) mas cercanas al centro ENCENDIDAS (donde caminas/miras de cerca),
#   APAGA las demas LP_ redundantes (los faroles YA tienen brillo emisivo propio = siguen "encendidos").
#   NO toca luces de hacienda/caminos (LH_/LC_/APL_). Sube SkyLight y Luna para que NO se vea oscuro.
#   Reversible (respaldo del nivel ya hecho). Reporta que hizo.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luces_emisivo.json"
CX, CY = 0.0, -1000.0
KEEP = 6
res = {"plaza_total": 0, "mantenidas": 0, "apagadas": 0, "sky": None, "moon": None, "apagadas_lbl": [], "err": []}
eas = unreal.EditorActorSubsystem()
plaza_lights = []  # (dist, actor, lightcomp, label)
for a in eas.get_all_level_actors():
    lbl = a.get_actor_label()
    for lc in a.get_components_by_class(unreal.LightComponent):
        if lc.get_class().get_name() in ("PointLightComponent", "SpotLightComponent"):
            if lbl.startswith("LP_"):   # SOLO luces propias de la plaza
                try:
                    loc = a.get_actor_location()
                    d = math.hypot(loc.x - CX, loc.y - CY)
                    plaza_lights.append((d, a, lc, lbl))
                except Exception as e:
                    res["err"].append("%s: %s" % (lbl, e))
plaza_lights.sort(key=lambda t: t[0])
res["plaza_total"] = len(plaza_lights)
for i, (d, a, lc, lbl) in enumerate(plaza_lights):
    try:
        if i < KEEP:
            lc.set_visibility(True, False)
            lc.set_editor_property("cast_shadows", False)
            res["mantenidas"] += 1
        else:
            lc.set_visibility(False, False)   # apagar (el farol sigue con brillo emisivo)
            res["apagadas"] += 1
            res["apagadas_lbl"].append(lbl)
    except Exception as e:
        res["err"].append("%s: %s" % (lbl, e))
# Compensar: subir SkyLight + Luna para que NO se vea oscuro
for a in eas.get_all_level_actors():
    sk = a.get_component_by_class(unreal.SkyLightComponent)
    if sk:
        try:
            sk.set_editor_property("intensity", 2.0)
            res["sky"] = "skylight 2.0"
        except Exception as e:
            res["err"].append("sky: %s" % e)
    dl = a.get_component_by_class(unreal.DirectionalLightComponent)
    if dl:
        try:
            cur = float(dl.get_editor_property("intensity"))
            dl.set_editor_property("intensity", cur * 1.4)
            dl.set_editor_property("cast_shadows", False)
            res["moon"] = "moon %.2f -> %.2f" % (cur, cur * 1.4)
        except Exception as e:
            res["err"].append("moon: %s" % e)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("LUCES EMISIVO plaza=%d keep=%d off=%d" % (res["plaza_total"], res["mantenidas"], res["apagadas"]))
