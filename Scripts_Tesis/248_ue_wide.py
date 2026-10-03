import unreal, math
TARGET="__LBL__"
eas=unreal.EditorActorSubsystem()
fa=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()==TARGET: fa=a; break
o,e=fa.get_actor_bounds(False)
yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
# camara elevada y atras, en diagonal
cam=unreal.Vector(o.x+nx*260 - ny*120, o.y+ny*260 + nx*120, o.z+140)
look_pitch = -18.0
look_yaw=math.degrees(math.atan2(o.y-cam.y,o.x-cam.x))
eas.set_selected_level_actors([fa])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,look_pitch,look_yaw))
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
