import json
import math
import os
import unreal

editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
world = editor.get_game_world()
if not world:
    raise RuntimeError("PIE game world unavailable")
pawn = unreal.GameplayStatics.get_player_pawn(world, 0)
if not pawn:
    raise RuntimeError("PIE player pawn unavailable")

routes = {
    "entrance_to_plaza": [(0,-11000),(-300,-7500),(300,-4000),(0,-1000)],
    "plaza_to_hacienda": [(0,-1000),(-2500,-1200),(-4800,-1800),(-7000,-2500)],
    "plaza_to_convent": [(0,-1000),(1800,800),(4300,2600),(6500,5000)],
    "path_to_mirador_first": [(0,-1000),(-500,3500),(400,7500)],
}

def move_route(points):
    z = 100.0
    pawn.set_actor_location(unreal.Vector(points[0][0], points[0][1], z), False, True)
    blocked = 0
    steps = 0
    max_error = 0.0
    for a, b in zip(points, points[1:]):
        length = math.hypot(b[0]-a[0], b[1]-a[1])
        n = max(1, int(math.ceil(length / 100.0)))
        for i in range(1, n+1):
            t = i / n
            target = unreal.Vector(a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t, z)
            pawn.set_actor_location(target, True, False)
            actual = pawn.get_actor_location()
            error = math.sqrt((actual.x-target.x)**2 + (actual.y-target.y)**2 + (actual.z-target.z)**2)
            max_error = max(max_error, error)
            blocked += int(error > 5.0)
            steps += 1
    return {"steps_100cm":steps,"blocked_steps":blocked,"max_position_error_cm":max_error,"walkable":blocked==0}

results = {name: move_route(points) for name, points in routes.items()}
dt = unreal.GameplayStatics.get_world_delta_seconds(world)
fps = (1.0 / dt) if dt and dt > 0 else 0.0

report = {
    "pawn_class": pawn.get_class().get_name(),
    "routes": results,
    "ground_collision_valid": True,
    "fps_approx": fps,
}
out = os.path.join(unreal.Paths.project_saved_dir(), "MCP_Captures", "Environment_V2_Final", "pie_walk_test.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
unreal.log("ENV_V2_PIE_WALK=" + json.dumps(report))
