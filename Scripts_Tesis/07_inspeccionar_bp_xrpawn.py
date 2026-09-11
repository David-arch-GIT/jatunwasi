# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 15:39
# Que hace este script: Localiza e inspecciona BP_XRPawn.
# Por que se necesito: Preparar las instrucciones de la caminata VR.
# Resultado obtenido: Ruta hallada; Python no lee el grafo de Blueprint.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    hits=[]
    for a in ar.get_assets_by_path('/Game',recursive=True):
        n=str(a.asset_name)
        if 'XRPawn' in n or 'XR_Pawn' in n or ('Pawn' in n and ('VR' in n or 'XR' in n)):
            hits.append(str(a.package_name))
    out['candidates']=hits
    path=None
    for h in hits:
        if h.split('/')[-1]=='BP_XRPawn': path=h; break
    if not path and hits: path=hits[0]
    out['using']=path
    if path:
        bp=unreal.EditorAssetLibrary.load_asset(path)
        gc=None
        try: gc=bp.get_editor_property('generated_class')
        except: pass
        # parent
        try:
            par=bp.get_editor_property('parent_class'); out['parent']=str(par.get_name()) if par else None
        except Exception as e: out['parent_err']=str(e)
        # components via CDO
        try:
            cdo=unreal.get_default_object(gc) if gc else None
            comps=[]
            if cdo:
                for c in cdo.get_components_by_class(unreal.ActorComponent):
                    comps.append([c.get_name(),c.get_class().get_name()])
            out['components']=comps
        except Exception as e: out['comp_err']=str(e)
        # variables
        try:
            vars=[]
            for v in unreal.BlueprintEditorLibrary.get_blueprint_variables(bp) if hasattr(unreal.BlueprintEditorLibrary,'get_blueprint_variables') else []:
                vars.append(str(v))
            out['vars']=vars
        except Exception as e: out['vars_err']=str(e)[:120]
        # try to open editor
        try:
            unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp]); out['opened']=True
        except Exception as e: out['open_err']=str(e)[:120]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bpx.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-600:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bpx.json','w').write(json.dumps(out,indent=1))
