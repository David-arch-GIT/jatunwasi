# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-31
# Que hace: (UE) REVIERTE el horneado que rompio todo: luces -> MOVABLE de nuevo (adios warnings bUsedWithStaticLighting
#   y deformacion), encendidas, radio local 300, SIN sombra, cull 2500 (iluminado pero mas barato). Luna MOVABLE sin sombra.
#   Sube el SkyLight (relleno ambiente para interiores, barato). Afloja foliage cull. Guarda.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/revertir.json"
res = {"lights": 0, "moon": None, "skylight": None, "foliage": 0, "err": []}
eas = unreal.EditorActorSubsystem()
acts = eas.get_all_level_actors()
for a in acts:
    for lc in a.get_components_by_class(unreal.LightComponent):
        cls = lc.get_class().get_name()
        if cls in ("PointLightComponent", "SpotLightComponent"):
            try:
                a.root_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                lc.set_visibility(True, False)
                lc.set_editor_property("attenuation_radius", 350.0)
                lc.set_editor_property("cast_shadows", False)
                lc.set_editor_property("max_draw_distance", 2500.0)
                lc.set_editor_property("max_distance_fade_range", 500.0)
                res["lights"] += 1
            except Exception as e:
                res["err"].append("%s: %s" % (a.get_actor_label(), e))
        if cls == "DirectionalLightComponent":
            try:
                a.root_component.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
                lc.set_editor_property("cast_shadows", False)
                res["moon"] = "moon MOVABLE sin sombra"
            except Exception as e:
                res["err"].append("moon: %s" % e)
        if cls == "SkyLightComponent":
            try:
                lc.set_editor_property("intensity", 1.2)   # relleno ambiente para interiores
                res["skylight"] = "skylight intensity 1.2"
            except Exception as e:
                res["err"].append("sky: %s" % e)
# si no hay skylight, crear uno
if res["skylight"] is None:
    try:
        sky = eas.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,500), unreal.Rotator())
        sky.set_actor_label("SkyLight_Fill")
        skc = sky.get_component_by_class(unreal.SkyLightComponent)
        skc.set_editor_property("intensity", 1.2)
        skc.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE) if hasattr(skc,'set_editor_property') else None
        res["skylight"] = "skylight CREADO intensity 1.2"
    except Exception as e:
        res["err"].append("crear sky: %s" % e)

def cull(nm):
    n = nm.lower()
    if "horiz" in n: return (16000, 20000)
    if "bosque" in n or "hacfor" in n or "tree" in n or "arbol" in n: return (9000, 13000)
    if "grass" in n or "shrub" in n or "garden" in n or "cesped" in n: return (4000, 5500)
    return (6000, 8000)
for a in acts:
    for comp in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        try:
            if comp.get_instance_count() < 50: continue
            s, e = cull(a.get_actor_label())
            comp.set_editor_property("instance_start_cull_distance", int(s))
            comp.set_editor_property("instance_end_cull_distance", int(e))
            res["foliage"] += 1
        except Exception as ex:
            res["err"].append("hism: %s" % ex)

unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(OUT, "w").write(json.dumps(res, indent=1))
unreal.log("REVERTIR done lights=%d sky=%s" % (res["lights"], res["skylight"]))
