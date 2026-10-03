# Mueve el PlayerStart al punto VERIFICADO de la plaza (600,-950,30 yaw 180, dz=0 sobre NavMesh)
# y reubica la guia de controles frente a ese spawn. Deja la camara del editor en el ojo para capturar.
import unreal, json, math
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_ps.json"
res={}
eas=unreal.EditorActorSubsystem()
# 1) PlayerStart -> plaza
ps=None
for a in eas.get_all_level_actors():
    if a.get_class().get_name()=="PlayerStart": ps=a; break
if not ps:
    res["err"]="no PlayerStart"; open(OUT,"w").write(json.dumps(res)); raise SystemExit
newloc=unreal.Vector(600,-950,30)
newrot=unreal.Rotator(); newrot.yaw=180.0
ps.set_actor_location(newloc, False, True)
ps.set_actor_rotation(newrot, False)
l=ps.get_actor_location()
res["playerstart"]=[round(l.x),round(l.y),round(l.z)]
# verificar proyeccion dz
pr=unreal.NavigationSystemV1.project_point_to_navigation(unreal.EditorLevelLibrary.get_editor_world(), newloc, None, None, unreal.Vector(220,220,600))
res["ps_proj_z"]=round(pr.z,1) if pr else None
# 2) guia frente al spawn
mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/M_GuiaControles")
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="GUIA_Controles": eas.destroy_actor(a)
fwd=ps.get_actor_forward_vector()
DIST=300; ZUP=160
panel=unreal.Vector(l.x+fwd.x*DIST, l.y+fwd.y*DIST, l.z+ZUP)
nx=-fwd.x; ny=-fwd.y; mag=math.hypot(nx,ny) or 1.0
n=unreal.Vector(nx/mag, ny/mag, 0)
rot=unreal.MathLibrary.make_rot_from_zy(n, unreal.Vector(0,0,-1))
plane=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
act=unreal.EditorLevelLibrary.spawn_actor_from_object(plane, panel, rot)
act.set_actor_label("GUIA_Controles")
act.set_actor_scale3d(unreal.Vector(2.6,1.56,1.0))
smc=act.get_component_by_class(unreal.StaticMeshComponent)
smc.set_material(0, mat)
smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
act.set_editor_property("initial_life_span", 30.0)
res["guia"]=[round(panel.x),round(panel.y),round(panel.z)]
# 3) camara editor en el ojo
cam=unreal.Vector(l.x, l.y, l.z+60)
look=unreal.Rotator(); look.yaw=180.0
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
open(OUT,"w").write(json.dumps(res,default=str))
