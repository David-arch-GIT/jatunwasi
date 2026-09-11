# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:59
# Que hace este script: Reporta radio e intensidad final por sala y hace backup.
# Por que se necesito: Cerrar el re-alumbrado de la Hacienda.
# Resultado obtenido: Valores finales por sala; otras zonas sin tocar.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem); EAL=unreal.EditorAssetLibrary
    def room(nm):
        if 'Folk' in nm: return 'Folklore'
        if 'Salon' in nm: return 'Salon'
        if 'Comedor' in nm: return 'Comedor'
        if 'Zaguan' in nm or 'Portal' in nm: return 'Zaguan/Corredor'
        if 'Cocina' in nm: return 'Cocina'
        if 'Dormitorio' in nm: return 'Dormitorio'
        if 'Pasillo2' in nm or 'GAL_Farol' in nm or 'Hab2' in nm: return 'Pasillo2/Galeria'
        if 'Patio' in nm: return 'Patio'
        return 'Otro'
    def is_hac(l):
        return l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_') or (l.startswith('APL_') and not any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']))
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if is_hac(l): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv') or (l.startswith('APL_') and any(k in l for k in ['Refect','Celdas','ClaustG','Capilla'])): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    rooms={}; zcount={}; hac=[]
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label()
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
            z=zone_of(nm); zcount[z]=zcount.get(z,0)+1
            if z=='Hacienda':
                loc=a.get_actor_location()
                rooms.setdefault(room(nm),[]).append([nm,c.get_editor_property('attenuation_radius'),round(c.get_editor_property('intensity'),1)])
                hac.append({'x':loc.x,'y':loc.y,'z':loc.z,'r':c.get_editor_property('attenuation_radius')})
    def worst(ls):
        if not ls: return 0
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-90,max(xs)+90;y0,y1=min(ys)-90,max(ys)+90;z0,z1=min(zs)-90,max(zs)+90
        sx=max(70,(x1-x0)/28);sy=max(70,(y1-y0)/28);sz=max(70,(z1-z0)/10);W=0
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
    out['rooms']=rooms; out['zone_counts']=zcount; out['hac_overlap']=worst(hac)
    src=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split(':')[0].split('.')[0]
    dst=src+'_BACKUP_LUCES_FINAL'
    if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
    EAL.duplicate_asset(src,dst); EAL.save_asset(dst); out['backup']='updated'
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finalhac.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/finalhac.json','w').write(json.dumps(out,indent=1))
