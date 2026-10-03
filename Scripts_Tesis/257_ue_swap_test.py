import unreal, math
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
good = EAL.load_asset("/Game/FotosAntano/Planos/MI_P_calle_comercio_antaño")
pl=None; fa=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="FotoPlano_MUS_Cuadro_coc1": pl=a
    if a.get_actor_label()=="MUS_Cuadro_coc1": fa=a
smc=pl.get_component_by_class(unreal.StaticMeshComponent)
smc.set_material(0, good)
# camara de frente +normal
o,e=fa.get_actor_bounds(False)
yaw=math.radians(fa.get_actor_rotation().yaw); nx=-math.sin(yaw); ny=math.cos(yaw)
cam=unreal.Vector(o.x+nx*120, o.y+ny*120, o.z+5)
look=unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(o.x,o.y,o.z))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
