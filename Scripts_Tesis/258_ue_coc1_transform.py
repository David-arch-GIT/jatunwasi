import unreal, json, math
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/coc1_tr.json"
eas=unreal.EditorActorSubsystem()
EAL=unreal.EditorAssetLibrary
pl=None
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="FotoPlano_MUS_Cuadro_coc1": pl=a
# restaurar material estadio
est = EAL.load_asset("/Game/FotosAntano/Planos/MI_P_foto_de_estadio_felix_capr")
smc=pl.get_component_by_class(unreal.StaticMeshComponent)
smc.set_material(0, est)
loc=pl.get_actor_location(); rot=pl.get_actor_rotation(); sc=pl.get_actor_scale3d()
# normal del plano = +Z local en mundo
zdir=unreal.MathLibrary.quat_rotate_vector(rot.quaternion(), unreal.Vector(0,0,1))
res={"loc":[round(loc.x,1),round(loc.y,1),round(loc.z,1)],
     "rot":[round(rot.roll,1),round(rot.pitch,1),round(rot.yaw,1)],
     "scale":[round(sc.x,2),round(sc.y,2),round(sc.z,2)],
     "zdir":[round(zdir.x,2),round(zdir.y,2),round(zdir.z,2)]}
# camara a lo largo de +zdir a 130, elevada, con leve lateral para no clavarse
lateral=unreal.MathLibrary.quat_rotate_vector(rot.quaternion(), unreal.Vector(1,0,0))
cam=unreal.Vector(loc.x+zdir.x*130+lateral.x*40, loc.y+zdir.y*130+lateral.y*40, loc.z+zdir.z*130+35)
look=unreal.MathLibrary.find_look_at_rotation(cam, loc)
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
try: unreal.EditorLevelLibrary.editor_invalidate_viewports()
except Exception: pass
res["cam"]=[round(cam.x,1),round(cam.y,1),round(cam.z,1)]
open(OUT,"w").write(json.dumps(res,indent=1))
