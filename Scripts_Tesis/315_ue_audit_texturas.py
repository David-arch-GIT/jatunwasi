import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_tex.json"
res={"grandes":[], "por_tamano":{}, "total":0}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
assets=ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Texture2D"), search_sub_classes=True)
res["total"]=len(assets)
for ad in assets:
    path=str(ad.package_name)
    if not path.startswith("/Game"): continue
    dim=None
    try:
        t=ad.get_tag_value("Dimensions")
        if t: dim=str(t)
    except Exception: pass
    # tamano max
    mx=0
    if dim and "x" in dim:
        try:
            parts=dim.replace("X","x").split("x"); mx=max(int(parts[0]), int(parts[1]))
        except Exception: pass
    bucket = "4096+" if mx>=4096 else ("2049-4095" if mx>2048 else ("2048" if mx==2048 else "<=1024" if mx<=1024 else "1025-2047"))
    res["por_tamano"][bucket]=res["por_tamano"].get(bucket,0)+1
    if mx>2048:
        res["grandes"].append({"asset":path.split("/")[-1][:34],"dim":dim})
res["grandes"]=res["grandes"][:40]
res["n_grandes"]=len(res["grandes"])
open(OUT,"w").write(json.dumps(res,indent=1))
