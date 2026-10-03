import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bpapi.json"
res={}
def dircls(name, obj):
    try:
        res[name]=[m for m in dir(obj) if not m.startswith("_")]
    except Exception as e:
        res[name]="err:"+str(e)[:40]
dircls("BlueprintEditorLibrary", unreal.BlueprintEditorLibrary)
# KismetEditorUtilities?
for n in ["KismetEditorUtilities","K2Node","MaterialEditingLibrary"]:
    try: dircls(n, getattr(unreal, n))
    except Exception as e: res[n]="no attr"
# clases K2Node disponibles
knodes=[c for c in dir(unreal) if "K2Node" in c]
res["K2Node_classes"]=knodes[:60]
# funciones utiles en EditorAssetLibrary / subsystems para BP
res["has_add_component_helpers"]=[c for c in dir(unreal) if "SubobjectDataSubsystem" in c or "SubobjectData" in c]
open(OUT,"w").write(json.dumps(res, indent=1))
