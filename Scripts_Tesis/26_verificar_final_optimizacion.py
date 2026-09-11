# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:41
# Que hace este script: Verifica que las luces siguen intactas y hace backup.
# Por que se necesito: Confirmar que la optimizacion no toco luces.
# Resultado obtenido: 105 luces intactas, backup actualizado.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    EAL=unreal.EditorAssetLibrary; eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # verify no cull volume, count lights, overlap
    cv=sum(1 for a in eas.get_all_level_actors() if a.get_class().get_name()=='CullDistanceVolume')
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
        if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    z={'Plaza':[],'Caminos':[],'Hacienda':[],'Convento':[],'Templo':[]}; tot=0; sh=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
            tot+=1
            if bool(c.get_editor_property('cast_shadows')): sh+=1
            zz=zone_of(a.get_actor_label())
            if zz in z:
                loc=a.get_actor_location(); z[zz].append({'x':loc.x,'y':loc.y,'z':loc.z,'r':c.get_editor_property('attenuation_radius')})
    def worst(ls):
        if not ls: return 0
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-80,max(xs)+80;y0,y1=min(ys)-80,max(ys)+80;z0,z1=min(zs)-80,max(zs)+80
        sx=max(70,(x1-x0)/22);sy=max(70,(y1-y0)/22);sz=max(70,(z1-z0)/8);W=0
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
    out['cull_volumes']=cv; out['lights_total']=tot; out['shadows']=sh
    out['lights_per_zone']={k:len(v) for k,v in z.items()}
    out['overlap']={k:worst(v) for k,v in z.items()}
    # update backup
    src=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split(':')[0].split('.')[0]
    dst=src+'_BACKUP_LUCES_FINAL'
    if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
    EAL.duplicate_asset(src,dst); EAL.save_asset(dst); out['backup']='updated'
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finopt.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finopt.json','w').write(json.dumps(out,indent=1))
