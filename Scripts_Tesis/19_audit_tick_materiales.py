# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:18
# Que hace este script: Audita el tick real y los blend modes de materiales.
# Por que se necesito: Afinar el reporte de rendimiento.
# Resultado obtenido: 0 tick real; 7 masked, 12 translucidos.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # real tick: b_can_ever_tick
    canever=0; canlist=[]
    for a in eas.get_all_level_actors():
        try:
            pt=a.get_editor_property('primary_actor_tick')
            if pt and pt.get_editor_property('can_ever_tick'):
                canever+=1
                if len(canlist)<40: canlist.append([a.get_actor_label(),a.get_class().get_name()])
        except: pass
    out['can_ever_tick']=canever; out['can_ever_tick_list']=canlist
    # blend modes on Material assets
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    EAL=unreal.EditorAssetLibrary
    masked=[]; transl=[]; opaque=0; total=0
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','Material'),True):
        pn=str(ad.package_name)
        if not pn.startswith('/Game'): continue
        total+=1
        m=EAL.load_asset(pn)
        if not m: continue
        try:
            bm=str(m.get_editor_property('blend_mode'))
        except: bm=''
        if 'MASKED' in bm.upper(): masked.append(pn.split('/')[-1])
        elif 'TRANSLUCENT' in bm.upper(): transl.append(pn.split('/')[-1])
        else: opaque+=1
    out['materials_total']=total; out['masked']=len(masked); out['translucent']=len(transl)
    out['masked_sample']=masked[:25]; out['transl_sample']=transl[:25]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit3.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit3.json','w').write(json.dumps(out,indent=1))
