# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:53
# Que hace este script: Sube radios, borra duplicados y quita las menos importantes.
# Por que se necesito: Re-iluminar la Hacienda sala por sala.
# Resultado obtenido: 13 luces anchas; salas iluminadas, solape 4.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None,'deleted':[],'set':[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # keep-set: name -> (radius, intensity)
    KEEP={
     'LH_Folklore_A':(550,25),'LH_Folklore_B':(550,25),'APL_Folk_1_L':(850,18),'APL_Folk_2_L':(850,18),
     'LH_SalonBaile_1':(850,20),'LH_SalonBaile_2':(850,20),'LH_SalonBaile_3':(850,20),'APL_Salon_1_L':(750,18),'APL_Salon_2_L':(750,18),
     'LH_Comedor':(750,18),'APL_Comedor_1_L':(700,16),
     'LH_Portal_1':(750,18),'APL_Zaguan_1_L':(700,15),'APL_Zaguan_2_L':(700,15),
     'LH_Cocina_Fogon':(700,22),'LH_Cocina_Fogon2':(750,15),
     'LH_Dormitorio':(600,12),'APL_Dormitorio_1_L':(550,10),
     'LH_Patio_1':(750,18),
     'GAL_Farol_1':(500,12),'GAL_Farol_2':(500,12),'GAL_Farol_3':(500,12),
     'APL_Pasillo2_1_L':(650,15),'APL_Pasillo2_2_L':(650,15),'FILL_Hac_Hab2':(550,12),
    }
    def is_hac(l):
        return l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_') or (l.startswith('APL_') and not any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']))
    # delete non-keep Hacienda lights; set keep ones
    for a in list(eas.get_all_level_actors()):
        nm=a.get_actor_label()
        if not is_hac(nm): continue
        haslight=len(a.get_components_by_class(unreal.PointLightComponent))+len(a.get_components_by_class(unreal.SpotLightComponent))>0
        if not haslight: continue
        if nm in KEEP:
            r,cd=KEEP[nm]
            for c in a.get_components_by_class(unreal.LightComponentBase):
                cls=c.get_class().get_name()
                if cls not in ('PointLightComponent','SpotLightComponent'): continue
                c.set_editor_property('cast_shadows',False)
                c.set_editor_property('attenuation_radius',float(r))
                c.set_editor_property('intensity',float(cd))
                c.set_editor_property('max_draw_distance',1800.0); c.set_editor_property('max_distance_fade_range',400.0)
            out['set'].append(nm)
        else:
            eas.destroy_actor(a); out['deleted'].append(nm)
    # ---- greedy overlap repair: removal only, remove least important ----
    def imp(nm):
        if nm.startswith('LH_SalonBaile') or nm.startswith('LH_Folklore') or nm=='LH_Cocina_Fogon': return 10
        if nm in ('LH_Comedor','LH_Portal_1','LH_Dormitorio','LH_Patio_1'): return 7
        if nm.startswith('APL_Folk') or nm.startswith('APL_Salon'): return 6
        if nm=='LH_Cocina_Fogon2': return 5
        if nm.startswith('APL_'): return 5
        if nm=='FILL_Hac_Hab2': return 3
        if nm.startswith('GAL_Farol'): return 2
        return 4
    def hac_lights():
        res=[]
        for a in eas.get_all_level_actors():
            nm=a.get_actor_label()
            if not is_hac(nm): continue
            for c in a.get_components_by_class(unreal.LightComponentBase):
                if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'):
                    loc=a.get_actor_location(); res.append({'a':a,'n':nm,'x':loc.x,'y':loc.y,'z':loc.z,'r':c.get_editor_property('attenuation_radius')})
        return res
    def worst(ls):
        if not ls: return 0,None
        xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
        x0,x1=min(xs)-90,max(xs)+90;y0,y1=min(ys)-90,max(ys)+90;z0,z1=min(zs)-90,max(zs)+90
        sx=max(75,(x1-x0)/26);sy=max(75,(y1-y0)/26);sz=max(75,(z1-z0)/9);W=0;WL=None
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
    removed_overlap=[]
    for _ in range(30):
        ls=hac_lights(); W,WL=worst(ls)
        if W<=4: break
        WL.sort(key=lambda l:imp(l['n']))
        victim=WL[0]
        eas.destroy_actor(victim['a']); removed_overlap.append(victim['n'])
    out['removed_overlap']=removed_overlap
    ls=hac_lights(); W,_=worst(ls)
    out['hac_final_count']=len(ls); out['hac_overlap']=W
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/consol.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-800:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/consol.json','w').write(json.dumps(out,indent=1))
