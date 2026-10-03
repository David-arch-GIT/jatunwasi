# Hace la malla de respaldo de Nanite (la que usa Quest) MUCHO mas barata en el follaje = efecto "impostor".
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nanite_fb.json"
res={"cambiados":[], "props_probadas":None}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
FOLLAJE=["Maple","Oak","Tropical","Palm","Dead_Tree","ForestBush","GrassForest","Fern","ForestPlant","Flower","Mossy","Boxwood"]
assets=ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True)
EAL=unreal.EditorAssetLibrary
hechos=0
for ad in assets:
    nm=str(ad.asset_name)
    if not any(k in nm for k in FOLLAJE): continue
    p=str(ad.package_name)
    if not p.startswith("/Game"): continue
    try:
        sm=EAL.load_asset(p)
        ns=sm.get_editor_property("nanite_settings")
        if not ns: continue
        # intentar poner fallback barato (nombres varian por version)
        done=[]
        for prop,val in [("fallback_percent_triangles",0.05),("fallback_relative_error",2.0)]:
            try:
                ns.set_editor_property(prop,val); done.append(prop)
            except Exception: pass
        sm.set_editor_property("nanite_settings", ns)
        EAL.save_loaded_asset(sm)
        hechos+=1
        if len(res["cambiados"])<12:
            res["cambiados"].append({"mesh":nm,"props":done})
        if res["props_probadas"] is None: res["props_probadas"]=done
    except Exception as e:
        if len(res["cambiados"])<12: res["cambiados"].append({"mesh":nm,"err":str(e)[:40]})
res["total_mallas"]=hechos
open(OUT,"w").write(json.dumps(res,indent=1))
