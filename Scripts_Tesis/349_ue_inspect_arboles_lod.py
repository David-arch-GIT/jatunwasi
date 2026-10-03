# Inspecciona LODs/Nanite/impostor de las mallas de arboles (nivel de asset, no necesita el nivel).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/arboles_lod.json"
res={"arboles":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
NAMES=["SM_TropicalTree_01","SM_TropicalTree_02","SM_Dead_Tree","SM_Maple_01","SM_Maple_03","SM_Oak_01","SM_Oak_03","SM_Palm_01","SM_ForestBush_01","SM_GrassForest_01"]
assets=ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True)
byname={}
for ad in assets:
    byname[str(ad.asset_name)]=str(ad.package_name)
for nm in NAMES:
    p=byname.get(nm)
    if not p:
        res["arboles"].append({"mesh":nm,"nota":"no encontrado"}); continue
    try:
        sm=unreal.EditorAssetLibrary.load_asset(p)
        info={"mesh":nm,"path":p}
        # Nanite
        try:
            ns=sm.get_editor_property("nanite_settings")
            info["nanite"]=bool(ns.get_editor_property("enabled")) if ns else False
        except Exception: info["nanite"]="?"
        # LODs
        try:
            nlods=unreal.EditorStaticMeshLibrary.get_lod_count(sm)
        except Exception:
            try: nlods=sm.get_num_lods()
            except Exception: nlods=-1
        info["num_lods"]=nlods
        # tris por lod
        tris=[]
        for i in range(max(nlods,0)):
            try: tris.append(unreal.EditorStaticMeshLibrary.get_number_of_triangles(sm,i))
            except Exception: tris.append("?")
        info["tris_por_lod"]=tris
        # min lod
        try: info["min_lod"]=str(sm.get_editor_property("min_lod"))
        except Exception: pass
        res["arboles"].append(info)
    except Exception as e:
        res["arboles"].append({"mesh":nm,"err":str(e)[:60]})
open(OUT,"w").write(json.dumps(res,indent=1))
