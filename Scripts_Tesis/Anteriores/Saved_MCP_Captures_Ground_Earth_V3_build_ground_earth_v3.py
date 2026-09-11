import json
import os
import unreal

MASTER_PATH="/Game/JWN/Environment/Materials/M_JW_Ground_Earth_V3"
MI_PATH="/Game/JWN/Environment/Materials/MI_JW_Ground_Earth_V3"
BASE_PATH="/Game/StylescapeHD/Foliage/Textures/Cliff/T_Sand_D"
NORMAL_PATH="/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_N"
ROUGH_PATH="/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_R"

base=unreal.load_asset(BASE_PATH); normal=unreal.load_asset(NORMAL_PATH); rough=unreal.load_asset(ROUGH_PATH)
if not all((base,normal,rough)):
    raise RuntimeError("Selected earth texture set is incomplete")

tools=unreal.AssetToolsHelpers.get_asset_tools()
if unreal.EditorAssetLibrary.does_asset_exist(MASTER_PATH):
    mat=unreal.load_asset(MASTER_PATH)
else:
    mat=tools.create_asset("M_JW_Ground_Earth_V3","/Game/JWN/Environment/Materials",unreal.Material,unreal.MaterialFactoryNew())
if not mat:
    raise RuntimeError("Could not create ground earth master")

# Rebuild only this new ground material's expression graph.
unreal.MaterialEditingLibrary.delete_all_material_expressions(mat)
def node(cls,x,y):
    return unreal.MaterialEditingLibrary.create_material_expression(mat,cls,x,y)
def scalar(name,value,x,y):
    n=node(unreal.MaterialExpressionScalarParameter,x,y)
    n.set_editor_property("parameter_name",name); n.set_editor_property("default_value",value)
    return n

uv=node(unreal.MaterialExpressionTextureCoordinate,-1200,-50)
tile_u=scalar("TileU",175.0,-1200,130)
tile_v=scalar("TileV",125.0,-1200,250)
append=node(unreal.MaterialExpressionAppendVector,-950,180)
unreal.MaterialEditingLibrary.connect_material_expressions(tile_u,"",append,"A")
unreal.MaterialEditingLibrary.connect_material_expressions(tile_v,"",append,"B")
uv_mul=node(unreal.MaterialExpressionMultiply,-700,0)
unreal.MaterialEditingLibrary.connect_material_expressions(uv,"",uv_mul,"A")
unreal.MaterialEditingLibrary.connect_material_expressions(append,"",uv_mul,"B")

base_tex=node(unreal.MaterialExpressionTextureSampleParameter2D,-450,-250)
base_tex.set_editor_property("parameter_name","BaseColorTexture")
base_tex.set_editor_property("texture",base)
unreal.MaterialEditingLibrary.connect_material_expressions(uv_mul,"",base_tex,"UVs")

tint=node(unreal.MaterialExpressionVectorParameter,-450,-70)
tint.set_editor_property("parameter_name","GroundTint")
tint.set_editor_property("default_value",unreal.LinearColor(0.42,0.30,0.20,1.0))
tint_mul=node(unreal.MaterialExpressionMultiply,-180,-210)
unreal.MaterialEditingLibrary.connect_material_expressions(base_tex,"RGB",tint_mul,"A")
unreal.MaterialEditingLibrary.connect_material_expressions(tint,"RGB",tint_mul,"B")

saturation=scalar("Saturation",0.72,-420,90)
sat_mul=node(unreal.MaterialExpressionMultiply,60,-190)
unreal.MaterialEditingLibrary.connect_material_expressions(tint_mul,"",sat_mul,"A")
unreal.MaterialEditingLibrary.connect_material_expressions(saturation,"",sat_mul,"B")
unreal.MaterialEditingLibrary.connect_material_property(sat_mul,"",unreal.MaterialProperty.MP_BASE_COLOR)

normal_tex=node(unreal.MaterialExpressionTextureSampleParameter2D,-420,330)
normal_tex.set_editor_property("parameter_name","NormalTexture")
normal_tex.set_editor_property("texture",normal)
try: normal_tex.set_editor_property("sampler_type",unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
except Exception: pass
unreal.MaterialEditingLibrary.connect_material_expressions(uv_mul,"",normal_tex,"UVs")
normal_strength=scalar("NormalStrength",0.38,-170,470)
flat=node(unreal.MaterialExpressionConstant3Vector,-170,320)
flat.set_editor_property("constant",unreal.LinearColor(0.0,0.0,1.0,1.0))
normal_lerp=node(unreal.MaterialExpressionLinearInterpolate,70,350)
unreal.MaterialEditingLibrary.connect_material_expressions(flat,"",normal_lerp,"A")
unreal.MaterialEditingLibrary.connect_material_expressions(normal_tex,"RGB",normal_lerp,"B")
unreal.MaterialEditingLibrary.connect_material_expressions(normal_strength,"",normal_lerp,"Alpha")
unreal.MaterialEditingLibrary.connect_material_property(normal_lerp,"",unreal.MaterialProperty.MP_NORMAL)

rough_tex=node(unreal.MaterialExpressionTextureSampleParameter2D,-420,690)
rough_tex.set_editor_property("parameter_name","RoughnessTexture")
rough_tex.set_editor_property("texture",rough)
try: rough_tex.set_editor_property("sampler_type",unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
except Exception: pass
unreal.MaterialEditingLibrary.connect_material_expressions(uv_mul,"",rough_tex,"UVs")
rough_strength=scalar("RoughnessStrength",1.12,-170,850)
rough_mul=node(unreal.MaterialExpressionMultiply,70,720)
unreal.MaterialEditingLibrary.connect_material_expressions(rough_tex,"R",rough_mul,"A")
unreal.MaterialEditingLibrary.connect_material_expressions(rough_strength,"",rough_mul,"B")
unreal.MaterialEditingLibrary.connect_material_property(rough_mul,"",unreal.MaterialProperty.MP_ROUGHNESS)

mat.set_editor_property("two_sided",False)
unreal.MaterialEditingLibrary.recompile_material(mat)

if unreal.EditorAssetLibrary.does_asset_exist(MI_PATH):
    mi=unreal.load_asset(MI_PATH)
else:
    factory=unreal.MaterialInstanceConstantFactoryNew()
    mi=tools.create_asset("MI_JW_Ground_Earth_V3","/Game/JWN/Environment/Materials",unreal.MaterialInstanceConstant,factory)
if not mi:
    raise RuntimeError("Could not create ground earth material instance")
mi.set_editor_property("parent",mat)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"TileU",175.0)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"TileV",125.0)
unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi,"GroundTint",unreal.LinearColor(0.46,0.34,0.23,1.0))
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"Saturation",0.68)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"NormalStrength",0.34)
unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi,"RoughnessStrength",1.15)
unreal.MaterialEditingLibrary.update_material_instance(mi)

subsystem=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
ground=next((a for a in subsystem.get_all_level_actors() if a.get_actor_label()=="Ground_Cochabamba"),None)
if not ground: raise RuntimeError("Ground_Cochabamba missing")
gcomp=ground.get_components_by_class(unreal.StaticMeshComponent)[0]
before={"location":str(ground.get_actor_location()),"scale":str(ground.get_actor_scale3d()),"bounds":str(ground.get_actor_bounds(False)),"old":gcomp.get_material(0).get_path_name()}
gcomp.set_material(0,mi)
after={"location":str(ground.get_actor_location()),"scale":str(ground.get_actor_scale3d()),"bounds":str(ground.get_actor_bounds(False)),"new":gcomp.get_material(0).get_path_name()}
if before["location"]!=after["location"] or before["scale"]!=after["scale"] or before["bounds"]!=after["bounds"]:
    raise RuntimeError("Ground transform or bounds changed")

report={"old_material":before["old"],"master":mat.get_path_name(),"instance":mi.get_path_name(),"textures":{"base":BASE_PATH,"normal":NORMAL_PATH,"roughness":ROUGH_PATH},"tile_u":175.0,"tile_v":125.0,"target_tile_cm":[400.0,400.0],"ground_transform_unchanged":True}
out=os.path.join(unreal.Paths.project_saved_dir(),"MCP_Captures","Ground_Earth_V3","material_build.json")
with open(out,"w",encoding="utf-8") as f:json.dump(report,f,indent=2)
unreal.log("GROUND_5B_MATERIAL_READY="+json.dumps(report))
