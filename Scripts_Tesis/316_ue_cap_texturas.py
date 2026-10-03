import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_tex.json"
res={"capadas":0, "err":0, "detectados":0, "muestras":[], "dbg":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
EAL=unreal.EditorAssetLibrary
assets=ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Texture2D"), search_sub_classes=True)
for ad in assets:
    path=str(ad.package_name)
    if not path.startswith("/Game"): continue
    dim=ad.get_tag_value("Dimensions")
    mx=0
    if dim and "x" in str(dim):
        try:
            p=str(dim).replace("X","x").split("x"); mx=max(int(p[0]),int(p[1]))
        except Exception: pass
    if len(res["dbg"])<5: res["dbg"].append({"p":path.split("/")[-1][:20],"dim":str(dim),"mx":mx})
    if mx<=2048: continue
    res["detectados"]+=1
    try:
        t=ad.get_asset()
        if isinstance(t, unreal.Texture2D):
            cur=t.get_editor_property("max_texture_size")
            if cur and cur>0 and cur<=2048: continue  # ya capada
            t.set_editor_property("max_texture_size", 2048)
            EAL.save_loaded_asset(t)
            res["capadas"]+=1
            if len(res["muestras"])<10: res["muestras"].append(t.get_name())
    except Exception as e:
        res["err"]+=1
        if len(res.get("errs",[]))<5: res.setdefault("errs",[]).append(str(e)[:50])
open(OUT,"w").write(json.dumps(res,indent=1))
