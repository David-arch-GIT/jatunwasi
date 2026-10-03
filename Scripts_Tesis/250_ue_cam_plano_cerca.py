import unreal, math
TARGET = "FotoPlano___LBL__"
eas = unreal.EditorActorSubsystem()
pl=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()==TARGET: pl=a; break
loc = pl.get_actor_location()
rot = pl.get_actor_rotation()
# forward = +Z del plano (normal). obtener vector Z de la rotacion
fz = unreal.MathLibrary.get_forward_vector(rot)  # +X local... necesitamos +Z
# usar get_up_vector? El normal del plano es su +Z local
q = rot.quaternion() if hasattr(rot,"quaternion") else None
zx = unreal.MathLibrary.quat_rotate_vector(rot.quaternion(), unreal.Vector(0,0,1)) if hasattr(rot,"quaternion") else None
d = zx
cam = unreal.Vector(loc.x + d.x*105, loc.y + d.y*105, loc.z + d.z*105 + 8)
look = unreal.MathLibrary.find_look_at_rotation(cam, loc)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
