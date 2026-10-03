import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/xrpawn.json"
res={}
EAL=unreal.EditorAssetLibrary
# todos los assets XRFramework, filtrando interfaces / interaccion
inter=[]
allx=[]
for a in EAL.list_assets("/Game/XRFramework", recursive=True):
    nm=a.split("/")[-1].split(".")[0]
    allx.append(nm)
    low=nm.lower()
    if nm.startswith("BPI_") or "interface" in low or "interact" in low or "interfaz" in low:
        inter.append(nm)
res["interfaces_interact"]=sorted(set(inter))
res["xr_total"]=len(allx)
# funciones del generated class de BP_XRPawn
def funcs_of(path):
    bp=EAL.load_asset(path)
    if not bp: return "NO"
    gc=bp.generated_class()
    try:
        cdo=unreal.get_default_object(gc)
        fns=[m for m in dir(cdo) if not m.startswith("_")]
        # filtrar los muy comunes de Actor
        common=set(dir(unreal.Pawn))
        return [f for f in fns if f not in common][:80]
    except Exception as e:
        return "err:"+str(e)[:50]
res["BP_XRPawn_funcs"]=funcs_of("/Game/XRFramework/Blueprints/BP_XRPawn")
# buscar tambien todo /Game por interfaces con 'interact'
allint=[]
for a in EAL.list_assets("/Game", recursive=True):
    nm=a.split("/")[-1].split(".")[0]
    low=nm.lower()
    if "interact" in low or nm.startswith("BPI_"):
        allint.append(nm)
res["game_interfaces"]=sorted(set(allint))
open(OUT,"w").write(json.dumps(res, indent=1))
