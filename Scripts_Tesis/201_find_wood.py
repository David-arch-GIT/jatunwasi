import unreal, json
R={"mats":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
assets=ar.get_all_assets(False)
for a in assets:
    try:
        cls=str(a.asset_class_path.asset_name)
        if cls not in ("Material","MaterialInstanceConstant"): continue
        nm=str(a.asset_name).lower()
        if any(k in nm for k in ["wood","madera","timber","plank","viga","roble","nogal","oak","bark","fence","tabla"]):
            R["mats"].append(str(a.package_name))
    except Exception: pass
R["mats"]=sorted(set(R["mats"]))[:30]
open("C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/wood.json","w").write(json.dumps(R))
