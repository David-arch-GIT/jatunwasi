import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cam_calib.json"
res = {}
eas = unreal.EditorActorSubsystem()
fa = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COR_Cuadro_07": fa = a; break
loc = fa.get_actor_location(); rot = fa.get_actor_rotation()
yaw = math.radians(rot.yaw); nx = -math.sin(yaw); ny = math.cos(yaw)
dist = 110.0
# lado -normal
cam = unreal.Vector(loc.x - nx*dist, loc.y - ny*dist, loc.z)
look = math.degrees(math.atan2(loc.y - cam.y, loc.x - cam.x))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,0,look))
res["cam"] = [round(cam.x), round(cam.y), round(cam.z), round(look,1)]
res["frameloc"] = [round(loc.x), round(loc.y), round(loc.z)]
open(OUT,"w").write(json.dumps(res))
