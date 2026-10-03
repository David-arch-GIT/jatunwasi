# Intenta leer del CDO del pawn el modo de locomocion (teleport vs smooth).
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/locomocion.json"
res={"encontradas":{}, "probadas":[]}
pc=unreal.EditorAssetLibrary.load_blueprint_class("/Game/XRFramework/Blueprints/BP_XRPawn")
cdo=unreal.get_default_object(pc)
CANDIDATOS=["LocomotionType","MovementType","LocomotionMode","MovementMode","bUseTeleport","bTeleport",
 "bSmoothLocomotion","bSmooth","SmoothLocomotion","TeleportEnabled","bTeleportEnabled","DefaultLocomotion",
 "MovementStyle","LocomotionStyle","bAllowTeleport","bAllowSmooth","bContinuousMovement","bSnapTurn",
 "MoveType","NavigationType","bUseNavMesh","RequireNavMesh","bTeleportRequiresNavMesh"]
for n in CANDIDATOS:
    res["probadas"].append(n)
    try:
        v=cdo.get_editor_property(n)
        res["encontradas"][n]=str(v)
    except Exception:
        pass
# tambien listar nombres de todas las propiedades que contengan palabras clave (via iterate)
try:
    for prop in unreal.get_type_from_class(pc).__dir__() if False else []:
        pass
except Exception: pass
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
