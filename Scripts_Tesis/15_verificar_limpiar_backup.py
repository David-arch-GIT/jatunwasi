# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:10
# Que hace este script: Verifica luces, borra el mapa recover y actualiza backup.
# Por que se necesito: Cerrar la recuperacion de forma limpia.
# Resultado obtenido: 105 luces, backup actualizado.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None,'steps':[]}
try:
    EAL=unreal.EditorAssetLibrary
    LES=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # verify current working map
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
        if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    z={'Plaza':[],'Caminos':[],'Hacienda':[],'Convento':[],'Templo':[],'Otro':[]}; tot=0; sh=0; o12=0; nmd=0; mesh=0
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label()
        if nm.startswith('APL_') and len(a.get_components_by_class(unreal.PointLightComponent))==0 and len(a.get_components_by_class(unreal.StaticMeshComponent))>0: mesh+=1
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
            tot+=1
            if bool(c.get_editor_property('cast_shadows')): sh+=1
            r=c.get_editor_property('attenuation_radius')
            if r>1200: o12+=1
            md=c.get_editor_property('max_draw_distance')
            if not md or md<=0: nmd+=1
            loc=a.get_actor_location(); z[zone_of(nm)].append({'x':loc.x,'y':loc.y,'z':loc.z,'r':r})
    def worst(ls):
        if not ls: return 0
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-80,max(xs)+80;y0,y1=min(ys)-80,max(ys)+80;z0,z1=min(zs)-80,max(zs)+80
        sx=max(65,(x1-x0)/26);sy=max(65,(y1-y0)/26);sz=max(65,(z1-z0)/9);W=0
        zz=z0
        while zz<=z1:
            yy=y0
            while yy<=y1:
                xx=x0
                while xx<=x1:
                    cc=sum(1 for l in ls if (xx-l['x'])**2+(yy-l['y'])**2+(zz-l['z'])**2<=l['r']*l['r'])
                    if cc>W: W=cc
                    xx+=sx
                yy+=sy
            zz+=sz
        return W
    out['verify']={'total':tot,'shadows':sh,'radius_over_1200':o12,'no_maxdraw':nmd,'aplique_meshes':mesh,
        'counts':{k:len(v) for k,v in z.items() if k!='Otro'},'overlap':{k:worst(v) for k,v in z.items() if k!='Otro'}}
    # cleanup recover asset
    if EAL.does_asset_exist('/Game/JWN/MAP_RECOVER_141'):
        EAL.delete_asset('/Game/JWN/MAP_RECOVER_141'); out['steps'].append('deleted RECOVER asset')
    # save working map
    LES.save_current_level(); out['steps'].append('saved working map')
    # update backup
    src=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split(':')[0].split('.')[0]
    dst=src+'_BACKUP_LUCES_FINAL'
    if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
    EAL.duplicate_asset(src,dst); EAL.save_asset(dst); out['steps'].append('backup updated'); out['backup']=dst
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finalize.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-800:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finalize.json','w').write(json.dumps(out,indent=1))
