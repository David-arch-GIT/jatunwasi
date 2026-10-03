import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/imc.json"
res={"imc":[], "ia_trigger":[]}
EAL=unreal.EditorAssetLibrary
# listar Input Actions y Mapping Contexts
for a in EAL.list_assets("/Game", recursive=True):
    nm=a.split("/")[-1].split(".")[0]
    if nm.startswith("IMC_") or nm.startswith("IA_"):
        res["imc"].append(nm)
res["imc"]=sorted(set(res["imc"]))
# intentar leer mapeos del IMC principal
for imcname in ["/Game/XRFramework/Input/IMC_Default","/Game/VRTemplate/Input/IMC_Default","/Game/XRFramework/Input/IMC_Hands"]:
    if EAL.does_asset_exist(imcname):
        imc=EAL.load_asset(imcname)
        try:
            maps=imc.get_editor_property("mappings")
            for m in maps:
                ia=m.get_editor_property("action")
                key=m.get_editor_property("key")
                res["ia_trigger"].append((imcname.split("/")[-1], ia.get_name() if ia else "?", str(key)))
        except Exception as e:
            res["ia_trigger"].append("err "+imcname+":"+str(e)[:40])
open(OUT,"w").write(json.dumps(res,indent=1))
