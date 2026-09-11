# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:07
# Que hace este script: Traspasa el mapa reparado al mapa de trabajo.
# Por que se necesito: El guardar-como fallo; transferir de forma segura.
# Resultado obtenido: Mapa de trabajo con 105 luces.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None,'steps':[]}
try:
    EAL=unreal.EditorAssetLibrary
    LES=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ELSU=unreal.EditorLoadingAndSavingUtils
    REC='/Game/JWN/MAP_RECOVER_141'
    TGT='/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN'
    # 1. persist repaired current level (RECOVER) to disk
    LES.save_current_level(); out['steps'].append('saved RECOVER (105 lights)')
    # 2. replace working map asset with the repaired content
    if EAL.does_asset_exist(TGT): EAL.delete_asset(TGT); out['steps'].append('deleted old working map')
    ok=EAL.duplicate_asset(REC,TGT); out['steps'].append('duplicated RECOVER->working: %s'%bool(ok))
    EAL.save_asset(TGT)
    # 3. open working map
    ELSU.load_map(TGT); out['steps'].append('loaded working map')
    # 4. cleanup recover asset
    if EAL.does_asset_exist(REC): EAL.delete_asset(REC); out['steps'].append('deleted RECOVER')
    # 5. verify on working map
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
        if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    z={'Plaza':[],'Caminos':[],'Hacienda':[],'Convento':[],'Templo':[],'Otro':[]}; tot=0; sh=0; over1200=0; nomd=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
            tot+=1
            if bool(c.get_editor_property('cast_shadows')): sh+=1
            r=c.get_editor_property('attenuation_radius')
            if r>1200: over1200+=1
            if not c.get_editor_property('max_draw_distance') or c.get_editor_property('max_draw_distance')<=0: nomd+=1
            loc=a.get_actor_location(); z[zone_of(a.get_actor_label())].append({'x':loc.x,'y':loc.y,'z':loc.z,'r':r})
    def worst(ls):
        if not ls: return 0
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-80,max(xs)+80;y0,y1=min(ys)-80,max(ys)+80;z0,z1=min(zs)-80,max(zs)+80
        sx=max(70,(x1-x0)/24);sy=max(70,(y1-y0)/24);sz=max(70,(z1-z0)/8);W=0
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
    out['verify']={'total':tot,'shadows':sh,'radius_over_1200':over1200,'no_maxdraw':nomd,
        'counts':{k:len(v) for k,v in z.items()},'overlap':{k:worst(v) for k,v in z.items() if k!='Otro'}}
    LES.save_current_level()
    # backup
    src=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split(':')[0].split('.')[0]
    dst=src+'_BACKUP_LUCES_FINAL'
    if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
    EAL.duplicate_asset(src,dst); EAL.save_asset(dst)
    out['backup']=dst
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/save2.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-900:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/save2.json','w').write(json.dumps(out,indent=1))
