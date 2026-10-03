# Inspecciona BP_Cartela y BP_XRPawn: componentes reales + variables + input, para instrucciones exactas.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inspect_bps.json"
res={}
ar=unreal.AssetRegistryHelpers.get_asset_registry()
def find_bp(namepart):
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Blueprint"), True):
        if namepart.lower() in str(ad.asset_name).lower():
            return str(ad.package_name)
    return None
def comps_of(bp_path):
    out=[]
    try:
        bp=unreal.EditorAssetLibrary.load_asset(bp_path)
        sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        handles=sds.k2_gather_subobject_data_for_blueprint(bp)
        for h in handles:
            try:
                data=sds.k2_find_subobject_data_from_handle(h)
                obj=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
                if obj:
                    nm=obj.get_name().replace("_GEN_VARIABLE","")
                    out.append(nm+" ["+obj.get_class().get_name()+"]")
            except Exception: pass
    except Exception as e:
        out.append("ERR:"+str(e)[:50])
    # dedup manteniendo orden
    seen=set(); uniq=[]
    for x in out:
        if x not in seen: seen.add(x); uniq.append(x)
    return uniq

# BP_Cartela
cart_path=find_bp("BP_Cartela") or find_bp("Cartela")
res["BP_Cartela_path"]=cart_path
if cart_path:
    res["BP_Cartela_componentes"]=comps_of(cart_path)
    # variables via CDO probando nombres tipicos
    try:
        cls=unreal.EditorAssetLibrary.load_blueprint_class(cart_path)
        cdo=unreal.get_default_object(cls)
        vars_found={}
        for n in ["Panel","PanelVisible","bVisible","Abierto","bAbierto","Audio","AudioComp","Texto","Sonido","bMostrando","Cartela"]:
            try: vars_found[n]=str(cdo.get_editor_property(n))[:40]
            except Exception: pass
        res["BP_Cartela_vars_encontradas"]=vars_found
    except Exception as e:
        res["BP_Cartela_vars_err"]=str(e)[:50]

# BP_XRPawn
pawn_path=find_bp("XRPawn") or find_bp("VRPawn")
res["BP_XRPawn_path"]=pawn_path
if pawn_path:
    res["BP_XRPawn_componentes"]=comps_of(pawn_path)

# Input Mapping Contexts y Input Actions del proyecto
ims=[]
ias=[]
for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/EnhancedInput","InputMappingContext"), True):
    ims.append(str(ad.asset_name))
for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/EnhancedInput","InputAction"), True):
    ias.append(str(ad.asset_name))
res["InputMappingContexts"]=ims[:20]
res["InputActions"]=ias[:30]
open(OUT,"w").write(json.dumps(res,indent=1))
