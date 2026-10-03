import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/verif_texsize.json"
res={"tex":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
targets=["T_Cliff_N","T_Maple_01_Impostor_BaseColor","T_Cobblestone_Path_D","T_Bark_D","T_Stone_Fence_N","T_Moss_D"]
assets=ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Texture2D"), search_sub_classes=True)
for ad in assets:
    nm=str(ad.asset_name)
    if nm in targets:
        t=ad.get_asset()
        if isinstance(t, unreal.Texture2D):
            mts=t.get_editor_property("max_texture_size")
            try: sx=t.blueprint_get_size_x(); sy=t.blueprint_get_size_y()
            except Exception: sx=sy=-1
            res["tex"].append({"nm":nm,"max_texture_size":mts,"import":str(ad.get_tag_value("Dimensions")),"built":[sx,sy]})
open(OUT,"w").write(json.dumps(res,indent=1))
