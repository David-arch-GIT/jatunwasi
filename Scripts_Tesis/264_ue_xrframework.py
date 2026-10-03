import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/xrfw.json"
res={"interact_assets":[], "interfaces":[], "widget_interaction_classes":[]}
EAL=unreal.EditorAssetLibrary
for a in EAL.list_assets("/Game/XRFramework", recursive=True):
    nm=a.split("/")[-1].split(".")[0]
    low=nm.lower()
    if any(k in low for k in ["interact","grab","point","laser","widget","use","select","hover","menu","button"]):
        res["interact_assets"].append(nm)
res["interact_assets"]=sorted(set(res["interact_assets"]))
# tambien buscar interfaces BPI en todo el proyecto
for a in EAL.list_assets("/Game", recursive=True):
    nm=a.split("/")[-1].split(".")[0]
    if nm.startswith("BPI_") or "interface" in nm.lower():
        res["interfaces"].append(nm)
res["interfaces"]=sorted(set(res["interfaces"]))[:40]
open(OUT,"w").write(json.dumps(res,indent=1))
