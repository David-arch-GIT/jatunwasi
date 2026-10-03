# Diagnostico de navegacion: tipo de pawn/locomocion, cobertura NavMeshBoundsVolume, NavModifier (exclusiones).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_nav.json"
res={"pawn_class":"", "pawn_vars_teleport":[], "navvols":[], "navmods":[], "navlinks":0}
eas=unreal.EditorActorSubsystem()
def bounds(a):
    o,e=a.get_actor_bounds(False)
    return {"centro":[round(o.x),round(o.y),round(o.z)],"ext":[round(e.x),round(e.y),round(e.z)],
            "x":[round(o.x-e.x),round(o.x+e.x)],"y":[round(o.y-e.y),round(o.y+e.y)],"z":[round(o.z-e.z),round(o.z+e.z)]}
for a in eas.get_all_level_actors():
    cn=a.get_class().get_name()
    if cn=="NavMeshBoundsVolume":
        res["navvols"].append(bounds(a))
    elif "NavModifier" in cn:
        b=bounds(a); b["label"]=a.get_actor_label()[:30]; res["navmods"].append(b)
    elif "NavLink" in cn:
        res["navlinks"]+=1
# pawn default
try:
    world=unreal.EditorLevelLibrary.get_editor_world()
    gm_path="/Game/VRTemplate/Blueprints/BP_XRGameMode"
    gmc=unreal.EditorAssetLibrary.load_blueprint_class(gm_path) if unreal.EditorAssetLibrary.does_asset_exist(gm_path) else None
    if gmc:
        cdo=unreal.get_default_object(gmc)
        pawn=cdo.get_editor_property("default_pawn_class")
        res["pawn_class"]=pawn.get_name() if pawn else "None"
except Exception as e:
    res["pawn_err"]=str(e)[:60]
# buscar variables tipo teleport en el pawn CDO
try:
    for pth in ["/Game/VRTemplate/Blueprints/BP_XRPawn","/Game/VRTemplate/Blueprints/VRPawn","/Game/JWN/Blueprints/BP_XRPawn"]:
        if unreal.EditorAssetLibrary.does_asset_exist(pth):
            pc=unreal.EditorAssetLibrary.load_blueprint_class(pth)
            res["pawn_bp_found"]=pth
            break
except Exception as e:
    res["pawn2_err"]=str(e)[:60]
res["n_navvols"]=len(res["navvols"]); res["n_navmods"]=len(res["navmods"])
open(OUT,"w").write(json.dumps(res,indent=1))
