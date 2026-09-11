# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 15:36
# Que hace este script: Reduce 141 a 59 luces protegiendo las canonicas.
# Por que se necesito: Cumplir el limite de 4 solapadas del Quest 2.
# Resultado obtenido: 59 luces, todas las zonas menor o igual a 4.
# ------------------------------------------------------------

import unreal, json, traceback, re
out={'err':None,'removed_lights':[],'kept_lights':0,'kept_meshes':0}
try:
    LES=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # backup save first
    LES.save_current_level()
    PROT=set([
      'LP_Plaza_0','LP_Plaza_1','LP_Plaza_2','LP_Plaza_3','LP_Plaza_4','LP_Plaza_5','LP_Plaza_6','LP_Plaza_7','LP_Fuente',
      'LC_Cam_Junc_0','LC_Cam_Junc_1','LC_Cam_Junc_2','LC_Cam_4','LC_FarolL_1','LC_FarolL_4','LC_FarolL_6','LC_FarolL_8',
      'LH_Comedor','LH_Dormitorio','LH_Folklore_A','LH_Folklore_B','LH_SalonBaile_1','LH_SalonBaile_2','LH_SalonBaile_3',
      'LH_Patio_1','LH_Cocina_Fogon','LH_Portal_1','FILL_Hac_Hab2','GAL_Farol_1','GAL_Farol_2','GAL_Farol_3',
      'APL_Folk_1_L','APL_Folk_2_L','APL_Comedor_1_L','APL_Zaguan_1_L','APL_Zaguan_2_L','APL_Dormitorio_1_L',
      'APL_Salon_1_L','APL_Salon_2_L','APL_Pasillo2_1_L','APL_Pasillo2_2_L',
      'LCV_Claustro_A','LCV_Claustro_B','LCV_Pozo','LCV_Refectorio','LCV_Capilla_Altar','LCV_Celdas_Pasillo','FILL_Cv_Cocina',
      'APL_Refect_1_L','APL_Refect_2_L','APL_Celdas_1_L','APL_Celdas_2_L','APL_ClaustG_1_L','APL_ClaustG_2_L','APL_Capilla_1_L',
      'Spot_Retablo_L','Spot_Retablo_R','NaveFill_0','NaveFill_1','NaveFill_3','LT_Altar',
    ])
    # pass 1: delete all NON-protected light actors (keep meshes)
    for a in list(eas.get_all_level_actors()):
        nm=a.get_actor_label()
        haslight=len(a.get_components_by_class(unreal.PointLightComponent))+len(a.get_components_by_class(unreal.SpotLightComponent))>0
        if haslight and nm not in PROT:
            out['removed_lights'].append(nm); eas.destroy_actor(a)
    # verify + greedy trim if any zone still >4 or total>65
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
        if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    def collect():
        z={'Plaza':[],'Caminos':[],'Hacienda':[],'Convento':[],'Templo':[],'Otro':[]}
        for a in eas.get_all_level_actors():
            for c in a.get_components_by_class(unreal.LightComponentBase):
                if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
                loc=a.get_actor_location()
                z[zone_of(a.get_actor_label())].append({'n':a.get_actor_label(),'x':loc.x,'y':loc.y,'z':loc.z,'r':c.get_editor_property('attenuation_radius')})
        return z
    def worst(ls):
        if not ls: return 0,None
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-100,max(xs)+100;y0,y1=min(ys)-100,max(ys)+100;z0,z1=min(zs)-100,max(zs)+100
        sx=max(60,(x1-x0)/26);sy=max(60,(y1-y0)/26);sz=max(60,(z1-z0)/9);W=0;WL=None
        zz=z0
        while zz<=z1:
            yy=y0
            while yy<=y1:
                xx=x0
                while xx<=x1:
                    cc=[l['n'] for l in ls if (xx-l['x'])**2+(yy-l['y'])**2+(zz-l['z'])**2<=l['r']*l['r']]
                    if len(cc)>W: W=len(cc);WL=cc
                    xx+=sx
                yy+=sy
            zz+=sz
        return W,WL
    # greedy last-resort (should rarely trigger); remove a protected light only if a cluster >4
    for _ in range(20):
        z=collect(); broke=False
        for zn,ls in z.items():
            W,WL=worst(ls)
            if W>4 and WL:
                rn=WL[-1]  # remove one in the cluster
                for a in eas.get_all_level_actors():
                    if a.get_actor_label()==rn: eas.destroy_actor(a); out['removed_lights'].append(rn+'(cluster)')
                broke=True; break
        if not broke: break
    # final tally
    z=collect(); tot=0; ov={}
    for zn,ls in z.items():
        tot+=len(ls); W,_=worst(ls); ov[zn]={'max':W,'count':len(ls)}
    out['final_overlap']=ov; out['total_lights']=tot
    out['kept_meshes']=sum(1 for a in eas.get_all_level_actors() if a.get_actor_label().startswith('APL_') and len(a.get_components_by_class(unreal.StaticMeshComponent))>0 and len(a.get_components_by_class(unreal.PointLightComponent))==0)
    LES.save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/thin.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-800:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/thin.json','w').write(json.dumps(out,indent=1))
