# Lee las asignaciones REALES de botones (Input Mapping Contexts) para la guia de controles.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/controles_reales.json"
res={}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
imc_paths={}
for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/EnhancedInput","InputMappingContext"), True):
    imc_paths[str(ad.asset_name)]=str(ad.package_name)
res["imc_encontrados"]=list(imc_paths.keys())
def key_name(k):
    try: return str(k.get_editor_property("key_name"))
    except Exception:
        try: return str(k)
        except Exception: return "?"
for name in ["IMC_Default","IMC_Menu","IMC_Hands"]:
    p=imc_paths.get(name)
    if not p: continue
    try:
        imc=unreal.EditorAssetLibrary.load_asset(p)
        maps=imc.get_editor_property("mappings")
        out=[]
        for m in maps:
            try:
                act=m.get_editor_property("action")
                an=act.get_name() if act else "None"
                k=m.get_editor_property("key")
                out.append({"accion":an,"tecla":key_name(k)})
            except Exception as e:
                out.append({"err":str(e)[:40]})
        res[name]=out
    except Exception as e:
        res[name]="ERR:"+str(e)[:50]
open(OUT,"w").write(json.dumps(res,indent=1))
