import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/test_plano.json"
res = {}
eas = unreal.EditorActorSubsystem()
EAL = unreal.EditorAssetLibrary
plane_mesh = EAL.load_asset("/Engine/BasicShapes/Plane")
mi = EAL.load_asset("/Game/FotosAntano/Planos/MI_P_memorias_del_ayer")
# datos COR_Cuadro_07
fa = None
for a in eas.get_all_level_actors():
    if a.get_actor_label() == "COR_Cuadro_07": fa = a; break
o, e = fa.get_actor_bounds(False)
yaw = math.radians(fa.get_actor_rotation().yaw)
nx = -math.sin(yaw); ny = math.cos(yaw)           # normal local
rx = -nx; ry = -ny                                  # room dir = -normal
room = unreal.Vector(rx, ry, 0.0)
up = unreal.Vector(0,0,1)
rot = unreal.MathLibrary.make_rot_from_zy(room, unreal.Vector(0,0,-1))  # 180 sobre normal para orientar bien
pos = unreal.Vector(o.x + rx*4.0, o.y + ry*4.0, o.z)
# borrar plano previo si existe
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label() == "FotoPlano_COR_Cuadro_07":
        eas.destroy_actor(a)
pl = eas.spawn_actor_from_object(plane_mesh, pos, rot)
pl.set_actor_label("FotoPlano_COR_Cuadro_07")
pl.set_actor_scale3d(unreal.Vector(0.62, 0.77, 1.0))   # X=ancho62 Y=alto77
smc = pl.get_component_by_class(unreal.StaticMeshComponent)
smc.set_material(0, mi)
smc.set_cast_shadow(False)
res["plano"] = [round(pos.x,1), round(pos.y,1), round(pos.z,1)]
res["rot"] = [round(rot.roll,1), round(rot.pitch,1), round(rot.yaw,1)]
# camara de frente (lado sala)
cam = unreal.Vector(o.x + rx*150.0, o.y + ry*150.0, o.z)
look = math.degrees(math.atan2(o.y - cam.y, o.x - cam.x))
eas.set_selected_level_actors([])
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, unreal.Rotator(0,0,look))
res["cam"] = [round(cam.x,1), round(cam.y,1), round(cam.z,1), round(look,1)]
open(OUT,"w").write(json.dumps(res, indent=1))
