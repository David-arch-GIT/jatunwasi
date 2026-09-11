# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Abre BP_XRPawn e intenta leer su estado de compilacion (status) y tipo.
# Por que se necesito: Verificar si la caminata con joystick esta terminada, sin poder leer el grafo.
# Resultado obtenido: (ver salida) - status del blueprint y apertura en el editor.
import unreal, json, traceback
out={'err':None}
try:
    bp=unreal.EditorAssetLibrary.load_asset('/Game/XRFramework/Blueprints/BP_XRPawn')
    out['loaded']=bp is not None
    for prop in ['status','blueprint_type']:
        try: out[prop]=str(bp.get_editor_property(prop))
        except Exception as e: out[prop+'_err']=str(e)[:80]
    # try list graphs / functions names via BlueprintEditorLibrary
    try:
        gnames=[]
        for g in unreal.BlueprintEditorLibrary.get_all_graphs(bp) if hasattr(unreal.BlueprintEditorLibrary,'get_all_graphs') else []:
            gnames.append(str(g.get_name()))
        out['graphs']=gnames
    except Exception as e: out['graphs_err']=str(e)[:80]
    try:
        unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp]); out['opened']=True
    except Exception as e: out['open_err']=str(e)[:80]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/loco.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/loco.json','w').write(json.dumps(out,indent=1))
