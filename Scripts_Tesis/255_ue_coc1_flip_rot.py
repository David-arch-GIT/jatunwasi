import unreal, math
eas=unreal.EditorActorSubsystem()
fa=None; pl=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="MUS_Cuadro_coc1": fa=a
    if a.get_actor_label()=="FotoPlano_MUS_Cuadro_coc1": pl=a
o,e=fa.get_actor_bounds(False)
yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
# rotacion con +Z = -normal (invertida), posicion en +normal (sala)
rot=unreal.MathLibrary.make_rot_from_zy(unreal.Vector(-nx,-ny,0), unreal.Vector(0,0,-1))
pos=unreal.Vector(o.x+nx*8.0, o.y+ny*8.0, o.z)
pl.set_actor_location_and_rotation(pos, rot, False, False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
# camara en +normal mirando el plano
cam=unreal.Vector(o.x+nx*115, o.y+ny*115, o.z+6)
look=unreal.MathLibrary.find_look_at_rotation(cam, pos)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
