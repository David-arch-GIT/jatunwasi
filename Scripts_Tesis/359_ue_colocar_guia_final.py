# Coloca la guia de controles como panel frente al PlayerStart y deja la camara del editor
# en el ojo del jugador para verificar por captura. Emisivo unlit, sin colision.
import unreal, json, math
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colocar_guia.json"
res={}
AT=unreal.AssetToolsHelpers.get_asset_tools()
# 1) importar/actualizar textura
task=unreal.AssetImportTask()
task.filename=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/guia_controles.png"
task.destination_path="/Game/JWN/UI"
task.destination_name="T_GuiaControles"
task.automated=True; task.replace_existing=True; task.save=True
AT.import_asset_tasks([task])
tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/T_GuiaControles")
res["textura"]=bool(tex)
# 2) material unlit emissive
if not unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/UI/M_GuiaControles"):
    mat=AT.create_asset("M_GuiaControles","/Game/JWN/UI",unreal.Material,unreal.MaterialFactoryNew())
    mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
    ts=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-380,0)
    ts.set_editor_property("texture",tex)
    unreal.MaterialEditingLibrary.connect_material_property(ts,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_asset("/Game/JWN/UI/M_GuiaControles")
else:
    mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/M_GuiaControles")
res["material"]=True
# 3) localizar PlayerStart
eas=unreal.EditorActorSubsystem()
ps=None
for a in eas.get_all_level_actors():
    if a.get_class().get_name()=="PlayerStart": ps=a; break
if not ps:
    res["err"]="no PlayerStart"; open(OUT,"w").write(json.dumps(res,default=str)); raise SystemExit
# quitar guia previa si existiera
for a in eas.get_all_level_actors():
    if a.get_actor_label()=="GUIA_Controles": unreal.EditorActorSubsystem().destroy_actor(a)
pl=ps.get_actor_location(); fwd=ps.get_actor_forward_vector()
DIST=300; ZUP=55
panel=unreal.Vector(pl.x+fwd.x*DIST, pl.y+fwd.y*DIST, pl.z+ZUP)
# normal del panel apunta de vuelta al jugador
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
res["panel_loc"]=[round(panel.x),round(panel.y),round(panel.z)]
# 4) camara editor en el ojo del jugador mirando al frente
cam=unreal.Vector(pl.x, pl.y, pl.z+60)
look=unreal.Rotator(); look.yaw=unreal.MathLibrary.make_rot_from_x(fwd).yaw
unreal.EditorLevelLibrary.set_level_viewport_camera_info(cam, look)
res["colocado"]=True
open(OUT,"w").write(json.dumps(res,default=str))
