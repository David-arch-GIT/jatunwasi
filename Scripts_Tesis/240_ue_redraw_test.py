import unreal, math
eas = unreal.EditorActorSubsystem()
fa=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="MUS_Cuadro_03": fa=a; break
o,e=fa.get_actor_bounds(False)
yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
rx=-nx; ry=-ny
cam=unreal.Vector(o.x+rx*160, o.y+ry*160, o.z)
look=math.degrees(math.atan2(o.y-cam.y,o.x-cam.x))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,0,look))
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception as ex: pass
