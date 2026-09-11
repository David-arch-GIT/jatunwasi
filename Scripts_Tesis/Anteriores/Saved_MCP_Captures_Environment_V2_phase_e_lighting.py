import json
import os
import unreal

subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = {a.get_actor_label(): a for a in subsystem.get_all_level_actors()}
report = {}

directional = actors.get("DirectionalLight")
if directional:
    comps = directional.get_components_by_class(unreal.DirectionalLightComponent)
    if comps:
        c = comps[0]
        c.set_editor_property("intensity", 3.1)
        c.set_editor_property("light_color", unreal.Color(255, 238, 220, 255))
        c.set_editor_property("use_temperature", True)
        c.set_editor_property("temperature", 5850.0)
        report["directional"] = {"intensity": 3.1, "color": [255,238,220], "temperature": 5850}

skylight = actors.get("SkyLight")
if skylight:
    comps = skylight.get_components_by_class(unreal.SkyLightComponent)
    if comps:
        c = comps[0]
        c.set_editor_property("intensity", 0.9)
        c.set_editor_property("light_color", unreal.Color(218, 229, 255, 255))
        c.set_editor_property("real_time_capture", True)
        try:
            c.recapture_sky()
        except Exception:
            pass
        report["skylight"] = {"intensity": 0.9, "color": [218,229,255]}

fog = actors.get("ExponentialHeightFog")
if fog:
    comps = fog.get_components_by_class(unreal.ExponentialHeightFogComponent)
    if comps:
        c = comps[0]
        c.set_editor_property("fog_density", 0.0045)
        c.set_editor_property("fog_height_falloff", 0.22)
        try:
            c.set_editor_property("fog_inscattering_color", unreal.LinearColor(0.68, 0.72, 0.76, 1.0))
        except Exception:
            pass
        report["fog"] = {"density": 0.0045, "height_falloff": 0.22, "color": [0.68,0.72,0.76]}

ground_mi = unreal.load_asset("/Game/JWN/Environment/Materials/MI_JW_Ground_PBR_V2")
if not ground_mi:
    raise RuntimeError("Ground PBR instance unavailable during lighting phase")
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    ground_mi, "Albedo Tint", unreal.LinearColor(0.46, 0.43, 0.37, 1.0))
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
    ground_mi, "Tiling/Offset", unreal.LinearColor(240.0, 240.0, 0.0, 0.0))
unreal.MaterialEditingLibrary.update_material_instance(ground_mi)
report["ground_tint"] = [0.46,0.43,0.37]
report["ground_tiling"] = 240.0

point_lights = [a.get_actor_label() for a in subsystem.get_all_level_actors() if isinstance(a, unreal.PointLight)]
report["point_lights_added"] = 0
report["existing_point_lights"] = point_lights

out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2", "phase_e_lighting.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
unreal.log("ENV_V2_PHASE_E_READY=" + json.dumps(report))
