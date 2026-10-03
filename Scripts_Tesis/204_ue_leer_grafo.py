import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/leer_grafo.json"
res = {"grafos": [], "nodos": {}, "err": []}
bp = unreal.EditorAssetLibrary.load_asset("/Game/JWN/Blueprints/BP_CriaturaViva")
BEL = unreal.BlueprintEditorLibrary
# intentar enumerar grafos y nodos
for gname in ["EventGraph", "DecidirAccion"]:
    try:
        g = BEL.find_graph(bp, gname) if gname != "EventGraph" else BEL.find_event_graph(bp)
        if g is None:
            res["grafos"].append(gname + ": no encontrado"); continue
        res["grafos"].append(gname + ": OK")
        nodes = g.get_editor_property("nodes")
        lst = []
        for n in nodes:
            try:
                title = n.get_node_title(unreal.NodeTitleType.LIST_VIEW) if hasattr(n, "get_node_title") else "?"
            except Exception:
                title = "?"
            lst.append({"clase": n.get_class().get_name(), "titulo": str(title)[:50]})
        res["nodos"][gname] = lst
    except Exception as e:
        res["err"].append(gname + ": " + str(e)[:70])
open(OUT, "w").write(json.dumps(res, indent=1))
