# Importa la guia de controles como textura, crea material unlit, y coloca un panel en la plaza frente al spawn.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/colocar_guia.json"
res={}
AT=unreal.AssetToolsHelpers.get_asset_tools()
# 1) importar textura
task=unreal.AssetImportTask()
task.filename=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/guia_controles.png"
task.destination_path="/Game/JWN/UI"
task.destination_name="T_GuiaControles"
task.automated=True; task.replace_existing=True; task.save=True
AT.import_asset_tasks([task])
tex=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/T_GuiaControles")
res["textura"]=bool(tex)
# 2) material unlit emissive
mat=None
if not unreal.EditorAssetLibrary.does_asset_exist("/Game/JWN/UI/M_GuiaControles"):
    mat=AT.create_asset("M_GuiaControles","/Game/JWN/UI",unreal.Material,unreal.MaterialFactoryNew())
else:
    mat=unreal.EditorAssetLibrary.load_asset("/Game/JWN/UI/M_GuiaControles")
mat.set_editor_property("shading_model",unreal.MaterialShadingModel.MSM_UNLIT)
ts=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionTextureSample,-380,0)
ts.set_editor_property("texture",tex)
unreal.MaterialEditingLibrary.connect_material_property(ts,"RGB",unreal.MaterialProperty.MP_EMISSIVE_COLOR)
unreal.MaterialEditingLibrary.recompile_material(mat)
unreal.EditorAssetLibrary.save_asset("/Game/JWN/UI/M_GuiaControles")
res["material"]=True
# 3) colocar panel frente al PlayerStart
eas=unreal.EditorActorSubsystem()
ps=None
for a in eas.get_all_level_actors():
    if a.get_class().get_name()=="PlayerStart":
        ps=a; break
if ps:
    pl=ps.get_actor_location()
    fwd=ps.get_actor_forward_vector()
    panel=unreal.Vector(pl.x+fwd.x*260, pl.y+fwd.y*260, pl.z+140)
    normal=unreal.Vector(-fwd.x,-fwd.y,0)  # mira de vuelta al jugador
    n=unreal.MathLibrary.normalize(normal)
    rot=unreal.MathLibrary.make_rot_from_zy(n, unreal.Vector(0,0,-1))
    plane=unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Plane")
    act=unreal.EditorLevelLibrary.spawn_actor_from_object(plane, panel, rot)
    act.set_actor_label("GUIA_Controles")
    act.set_actor_scale3d(unreal.Vector(2.1,1.32,1.0))
    smc=act.get_component_by_class(unreal.StaticMeshComponent)
    smc.set_material(0, mat)
    smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    unreal.EditorLoadingAndSavingUtils.save_current_level()
    res["panel_loc"]=[round(panel.x),round(panel.y),round(panel.z)]
    res["colocado"]=True
else:
    res["err"]="no PlayerStart"
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
