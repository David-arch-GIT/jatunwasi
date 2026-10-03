import unreal, math
TARGET = "__LBL__"
eas = unreal.EditorActorSubsystem()
fa=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()==TARGET: fa=a; break
o,e = fa.get_actor_bounds(False)
yaw = math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
dist=160.0
cam = unreal.Vector(o.x+nx*dist, o.y+ny*dist, o.z)
look = math.degrees(math.atan2(o.y-cam.y, o.x-cam.x))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,0,look))
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
