# Consulta NavMesh actual en los puntos exactos donde el usuario se bloqueo + tipo de pawn.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/query_nav.json"
res={"pawn":{}, "puntos":{}}
world=unreal.EditorLevelLibrary.get_editor_world()

# --- pawn / locomocion ---
ar=unreal.AssetRegistryHelpers.get_asset_registry()
def find_asset(namepart):
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Blueprint"), True):
        if namepart.lower() in str(ad.asset_name).lower():
            return str(ad.package_name)
    return None
try:
    gm_path=find_asset("XRGameMode") or find_asset("GameMode")
    res["pawn"]["gamemode_path"]=gm_path
    if gm_path:
        gmc=unreal.EditorAssetLibrary.load_blueprint_class(gm_path)
        cdo=unreal.get_default_object(gmc)
        p=cdo.get_editor_property("default_pawn_class")
        res["pawn"]["pawn_class"]=p.get_name() if p else "None"
except Exception as e:
    res["pawn"]["err"]=str(e)[:80]
try:
    pawn_path=find_asset("XRPawn") or find_asset("VRPawn")
    res["pawn"]["pawn_path"]=pawn_path
    if pawn_path:
        pc=unreal.EditorAssetLibrary.load_blueprint_class(pawn_path)
        pcdo=unreal.get_default_object(pc)
        comps=[c.get_name() for c in pcdo.get_components_by_class(unreal.ActorComponent)]
        res["pawn"]["components"]=[c for c in comps if any(k in c for k in ["Teleport","Move","Loco","Nav","Snap","Smooth","Widget","Motion"])][:20]
except Exception as e:
    res["pawn"]["err2"]=str(e)[:80]

# --- consulta de navmesh ---
PTS={
 "HAC_2P_landing":(-7588,-2478,435),
 "HAC_2P_bridge":(-7545,-2100,402),
 "HAC_ground_center":(-7000,-2500,100),
 "HAC_stair_bottom":(-6930,-2320,60),
 "HAC_entr_approach_N":(-6950,-400,90),
 "HAC_entr_approach_M":(-6950,-1200,90),
 "PATH_end_to_hac":(-6948,878,60),
 "CONV_court_center":(6290,5000,30),
 "CONV_arch_W":(5550,5000,30),
 "CONV_arch_E":(7050,5000,30),
 "CONV_arch_N":(6290,4250,30),
 "CONV_arch_S":(6290,5750,30),
}
def onnav(p):
    pt=unreal.Vector(p[0],p[1],p[2])
    ext=unreal.Vector(300,300,600)
    last=""
    for args in [ (world,pt,None,None,ext), (world,pt,None) ]:
        try:
            loc=unreal.NavigationSystemV1.project_point_to_navigation(*args)
            d=((loc.x-p[0])**2+(loc.y-p[1])**2+(loc.z-p[2])**2)**0.5
            zero = (abs(loc.x)<0.01 and abs(loc.y)<0.01 and abs(loc.z)<0.01)
            return {"navmesh": (not zero and d<800), "proj":[round(loc.x),round(loc.y),round(loc.z)], "dist":round(d)}
        except Exception as e:
            last=str(e)[:70]
    return {"err":last}
for k,p in PTS.items():
    res["puntos"][k]=onnav(p)
open(OUT,"w").write(json.dumps(res,indent=1))
