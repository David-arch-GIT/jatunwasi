# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:05
# Que hace este script: Reduce radios y quita luces hasta menor o igual a 4 sin borrar canonicas.
# Por que se necesito: Recuperar la densidad respetando el limite de Quest.
# Resultado obtenido: 105 luces, todas las zonas menor o igual a 4.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    CANON=set([
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
    def is_ext(l): return l.startswith('LP_') or l.startswith('LC_')
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
        if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    # mesh positions (aplique props, no light) for emissive-kept classification
    meshpos=[]
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label()
        if nm.startswith('APL_') and len(a.get_components_by_class(unreal.PointLightComponent))==0 and len(a.get_components_by_class(unreal.StaticMeshComponent))>0:
            l=a.get_actor_location(); meshpos.append((l.x,l.y,l.z))
    def near_mesh(x,y,z):
        for (mx,my,mz) in meshpos:
            if (mx-x)**2+(my-y)**2+(mz-z)**2 < 200*200: return True
        return False
    # PHASE A: enforce shadows off, maxdraw, radius cap. count reduced.
    IN_CAP=430; EX_CAP=900; reduced=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
            nm=a.get_actor_label()
            c.set_editor_property('cast_shadows',False)
            r=c.get_editor_property('attenuation_radius')
            if is_ext(nm):
                if r>EX_CAP: c.set_editor_property('attenuation_radius',float(EX_CAP)); reduced+=1
                c.set_editor_property('max_draw_distance',3500.0); c.set_editor_property('max_distance_fade_range',500.0)
            else:
                if r>IN_CAP: c.set_editor_property('attenuation_radius',float(IN_CAP)); reduced+=1
                c.set_editor_property('max_draw_distance',1800.0); c.set_editor_property('max_distance_fade_range',400.0)
    out['radii_reduced']=reduced
    # helpers to work per zone
    def zone_lights(zn):
        res=[]
        for a in eas.get_all_level_actors():
            nm=a.get_actor_label()
            if zone_of(nm)!=zn: continue
            for c in a.get_components_by_class(unreal.LightComponentBase):
                if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'):
                    loc=a.get_actor_location(); res.append({'a':a,'n':nm,'x':loc.x,'y':loc.y,'z':loc.z,'c':c,'r':c.get_editor_property('attenuation_radius')})
        return res
    def worst(ls):
        if not ls: return 0,None
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-80,max(xs)+80;y0,y1=min(ys)-80,max(ys)+80;z0,z1=min(zs)-80,max(zs)+80
        sx=max(70,(x1-x0)/24);sy=max(70,(y1-y0)/24);sz=max(70,(z1-z0)/8);W=0;WL=None
        zz=z0
        while zz<=z1:
            yy=y0
            while yy<=y1:
                xx=x0
                while xx<=x1:
                    cc=[l for l in ls if (xx-l['x'])**2+(yy-l['y'])**2+(zz-l['z'])**2<=l['r']*l['r']]
                    if len(cc)>W: W=len(cc);WL=cc
                    xx+=sx
                yy+=sy
            zz+=sz
        return W,WL
    emissive_kept=0; deleted=0; removed_canon=[]
    RFLOOR=400
    for zn in ['Plaza','Caminos','Hacienda','Convento','Templo','Otro']:
        guard=0
        while guard<400:
            guard+=1
            ls=zone_lights(zn)
            W,WL=worst(ls)
            if W<=4: break
            # tool1: reduce radii of interior lights in cluster still >floor
            red=[l for l in WL if (not is_ext(l['n'])) and l['r']>RFLOOR]
            if red:
                for l in red:
                    nr=max(RFLOOR,l['r']-40); l['c'].set_editor_property('attenuation_radius',float(nr))
                continue
            # tool4/5: remove least-important (non-canon first)
            noncanon=[l for l in WL if l['n'] not in CANON]
            pick = noncanon[0] if noncanon else WL[0]
            x,y,z=pick['x'],pick['y'],pick['z']
            if pick['n'] in CANON: removed_canon.append(pick['n'])
            if pick['n'].startswith('APL_') and near_mesh(x,y,z): emissive_kept+=1
            else: deleted+=1
            eas.destroy_actor(pick['a'])
    # final tally
    tot=0; ov={}; cnt={}
    for zn in ['Plaza','Caminos','Hacienda','Convento','Templo']:
        ls=zone_lights(zn); tot+=len(ls); W,_=worst(ls); ov[zn]=W; cnt[zn]=len(ls)
    out['emissive_kept']=emissive_kept; out['deleted']=deleted; out['removed_canon']=removed_canon
    out['final_counts']=cnt; out['final_overlap']=ov; out['total']=tot
    # SAVE AS working map
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    tgt='/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN'
    ok=unreal.EditorLoadingAndSavingUtils.save_map(w,tgt)
    out['saved_as']=bool(ok); out['tgt']=tgt
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/repair.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-800:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/repair.json','w').write(json.dumps(out,indent=1))
