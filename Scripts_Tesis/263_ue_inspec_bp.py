import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inspec_bp.json"
res={}
EAL=unreal.EditorAssetLibrary
def comps_of(bppath):
    out=[]
    bp=EAL.load_asset(bppath)
    if not bp: return ["NO_ASSET"]
    gc=bp.generated_class() if hasattr(bp,"generated_class") else None
    try:
        cdo=unreal.get_default_object(gc) if gc else None
    except Exception:
        cdo=None
    # via SCS
    try:
        scs=bp.get_editor_property("simple_construction_script")
    except Exception:
        scs=None
    # intentar leer nodos SCS
    try:
        for node in bp.get_editor_property("simple_construction_script").get_editor_property("all_nodes"):
            ct=node.get_editor_property("component_class")
            vn=node.get_editor_property("variable_name")
            out.append(str(vn)+":"+ (ct.get_name() if ct else "?"))
    except Exception as e:
        out.append("scs_err:"+str(e)[:40])
    return out
for path,key in [("/Game/VRTemplate/Blueprints/BP_XRPawn","BP_XRPawn"),
                 ("/Game/JWN/Blueprints/BP_NarrationPoint","BP_NarrationPoint")]:
    if not EAL.does_asset_exist(path):
        # buscar
        found=None
        for a in EAL.list_assets("/Game", recursive=True):
            if a.split("/")[-1].split(".")[0]==key:
                found=a.split(".")[0]; break
        path=found
    res[key]={"path":path,"comps":comps_of(path) if path else "NOT_FOUND"}
open(OUT,"w").write(json.dumps(res,indent=1))
