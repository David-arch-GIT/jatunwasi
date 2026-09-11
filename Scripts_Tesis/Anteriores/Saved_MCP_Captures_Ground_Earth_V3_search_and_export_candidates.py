import json
import os
import unreal

roots=("/Game/Megascans","/Game/StylescapeHD","/Game/JWN")
queries=("Soil","Dirt","Earth","Dry Soil","Forest Floor","Garden Soil","Mud","Rocky Soil","Dry Grass Ground","Ground")
registry=unreal.AssetRegistryHelpers.get_asset_registry()
all_assets=[]
for root in roots:
    all_assets.extend(registry.get_assets_by_path(root,recursive=True))
query_results={}
for query in queries:
    tokens=query.lower().split()
    query_results[query]=[
        str(a.package_name) for a in all_assets
        if all(token in (str(a.asset_name)+" "+str(a.package_name)).lower() for token in tokens)
    ]

candidates={
    "00_Island_Background":{
        "base":"/Game/StylescapeHD/Misc/Background/Textures/T_Island_Background_D",
        "normal":"/Game/StylescapeHD/Misc/Background/Textures/T_Island_Background_N",
        "roughness":"PARAMETER",
    },
    "00_Sand_CliffDetail":{
        "base":"/Game/StylescapeHD/Foliage/Textures/Cliff/T_Sand_D",
        "normal":"/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_N",
        "roughness":"/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_R",
    },
    "01_Needle_Pile":{
        "base":"/Game/StylescapeHD/Foliage/Textures/Needle_Pile/T_Needle_Pile_D",
        "normal":"/Game/StylescapeHD/Foliage/Textures/Needle_Pile/T_Needle_Pile_N",
        "roughness":"/Game/StylescapeHD/Foliage/Textures/Needle_Pile/T_Needle_Pile_R_SS_AO_OM",
    },
    "02_Underbrush_Patch":{
        "base":"/Game/StylescapeHD/Foliage/Textures/Underbrush_Patch/T_Underbrush_Patch_D",
        "normal":"/Game/StylescapeHD/Foliage/Textures/Underbrush_Patch/T_Underbrush_Patch_N",
        "roughness":"/Game/StylescapeHD/Foliage/Textures/Underbrush_Patch/T_Underbrush_Patch_R_SS_AO_OM",
    },
    "03_Mossy_Grass":{
        "base":"/Game/StylescapeHD/Foliage/Textures/Mossy_Grass/T_Mossy_Grass_D",
        "normal":"/Game/StylescapeHD/Foliage/Textures/Mossy_Grass/T_Mossy_Grass_N",
        "roughness":"/Game/StylescapeHD/Foliage/Textures/Mossy_Grass/T_Mossy_Grass_R_SS_AO_OM",
    },
    "04_Canyon_Mesa_Mound":{
        "base":"/Game/StylescapeHD/Foliage/Textures/Canyon/T_Canyon_Mesa_Mound_D",
        "normal":"/Game/StylescapeHD/Foliage/Textures/Canyon/T_Canyon_Mesa_Mound_N",
        "roughness":"/Game/StylescapeHD/Foliage/Textures/Canyon/T_Canyon_Mesa_Mound_R_AO",
    },
    "05_Cliff_Earth":{
        "base":"/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_D",
        "normal":"/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_N",
        "roughness":"/Game/StylescapeHD/Foliage/Textures/Cliff/T_Cliff_R",
    },
}

export_dir=os.path.join(unreal.Paths.project_saved_dir(),"MCP_Captures","Ground_Earth_V3","Candidates")
os.makedirs(export_dir,exist_ok=True)
for name,paths in candidates.items():
    for role,path in paths.items():
        if path == "PARAMETER":
            continue
        if not unreal.EditorAssetLibrary.does_asset_exist(path):
            raise RuntimeError("Missing candidate texture: "+path)
        if role=="base":
            task=unreal.AssetExportTask()
            task.object=unreal.load_asset(path)
            task.filename=os.path.join(export_dir,name+"_Base.png")
            task.automated=True
            task.prompt=False
            task.replace_identical=True
            task.exporter=unreal.TextureExporterPNG()
            if not unreal.Exporter.run_asset_export_task(task):
                raise RuntimeError("Texture export failed: "+path)

report={"queries":query_results,"candidates":candidates}
out=os.path.join(export_dir,"candidate_report.json")
with open(out,"w",encoding="utf-8") as f:json.dump(report,f,indent=2)
unreal.log("GROUND_5B_CANDIDATES="+json.dumps(candidates))
