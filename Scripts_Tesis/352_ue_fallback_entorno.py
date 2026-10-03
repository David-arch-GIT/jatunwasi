# Fallback Nanite barato a mallas de ENTORNO (rocas/cobblestone/cercas). NO edificios.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fb_entorno.json"
res={"cambiados":[], "otros_nanite":[]}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
ENTORNO=["Cobblestone","ForestRock","Rock","Cliff","Stone_Fence","Fence","Ground","Path_","Gravel","Dirt"]
EXCLUIR=["HACKIT","Wall","Arch","Column","Staircase","Dome","Drum","Building","Door","Window","Roof","Cartela","Vitrina"]
EAL=unreal.EditorAssetLibrary
assets=ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True)
hechos=0
for ad in assets:
    nm=str(ad.asset_name)
    p=str(ad.package_name)
    if not p.startswith("/Game"): continue
    es_ent=any(k in nm for k in ENTORNO)
    es_excl=any(k in nm for k in EXCLUIR)
    if not es_ent or es_excl:
        continue
    try:
        sm=EAL.load_asset(p)
        ns=sm.get_editor_property("nanite_settings")
        if not ns or not ns.get_editor_property("enabled"):
            continue
        for prop,val in [("fallback_percent_triangles",0.08),("fallback_relative_error",1.5)]:
            try: ns.set_editor_property(prop,val)
            except Exception: pass
        sm.set_editor_property("nanite_settings", ns)
        EAL.save_loaded_asset(sm)
        hechos+=1
        if len(res["cambiados"])<20: res["cambiados"].append(nm)
    except Exception as e:
        pass
res["total"]=hechos
open(OUT,"w").write(json.dumps(res,indent=1))
