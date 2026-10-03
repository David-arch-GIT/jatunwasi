import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_cuadro.json"
res = {}
TARGET = "MUS_Cuadro_00"
eas = unreal.EditorActorSubsystem()
fa = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == TARGET: fa = a; break
if not fa:
    res["err"] = "no frame"
else:
    loc = fa.get_actor_location(); rot = fa.get_actor_rotation()
    yaw = math.radians(rot.yaw)
    nx = -math.sin(yaw); ny = math.cos(yaw)
    dist = 95.0
    zc = loc.z + 40.0  # apuntar un poco mas arriba (centro del lienzo)
    cam = unreal.Vector(loc.x - nx*dist, loc.y - ny*dist, zc)
    tgt = unreal.Vector(loc.x, loc.y, zc)
    look_yaw = math.degrees(math.atan2(tgt.y - cam.y, tgt.x - cam.x))
    crot = unreal.Rotator(0.0, 0.0, look_yaw)
    eas.set_selected_level_actors([])
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, crot)
    res["cam"] = [cam.x, cam.y, cam.z, look_yaw]
open(OUT,"w").write(json.dumps(res, indent=1))
