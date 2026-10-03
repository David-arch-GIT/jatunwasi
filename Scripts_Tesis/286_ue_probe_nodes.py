import unreal, json, traceback
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/probenodes.json"
res={}
try:
    EAL=unreal.EditorAssetLibrary
    bp=EAL.load_asset("/Game/Cartelas/BP_Cartela")
    BEL=unreal.BlueprintEditorLibrary
    graph=BEL.find_event_graph(bp)
    res["graph_type"]=graph.get_class().get_name() if graph else "None"
    res["graph_methods"]=[m for m in dir(graph) if not m.startswith("_")][:60] if graph else []
    # metodos globales que contengan 'node'
    res["unreal_node_funcs"]=[m for m in dir(unreal) if " node" in m.lower() or m.lower().endswith("node")][:40]
    # ver si hay funciones utiles en unreal para spawn
    res["spawn_like"]=[m for m in dir(unreal) if "spawn" in m.lower() or "add_k2" in m.lower() or "graph" in m.lower()][:40]
except Exception as e:
    res["err"]=str(e)+" "+traceback.format_exc()[:300]
open(OUT,"w").write(json.dumps(res,indent=1))
