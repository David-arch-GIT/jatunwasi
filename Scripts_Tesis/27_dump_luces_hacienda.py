# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:49
# Que hace este script: Vuelca las luces de la Hacienda agrupadas por sala.
# Por que se necesito: Diagnosticar por que los interiores se veian oscuros.
# Resultado obtenido: Confirmado: radios de 350-400 en salas grandes.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def room(nm):
        n=nm
        if 'Folk' in n: return 'Folklore'
        if 'Salon' in n or 'SalonBaile' in n: return 'Salon'
        if 'Comedor' in n: return 'Comedor'
        if 'Zaguan' in n or 'Portal' in n: return 'Zaguan'
        if 'Cocina' in n: return 'Cocina'
        if 'Dormitorio' in n: return 'Dormitorio'
        if 'Pasillo2' in n or 'GAL_Farol' in n or 'Hab2' in n: return 'Pasillo2/Galeria'
        if 'Patio' in n: return 'Patio'
        return 'Otro_Hac'
    def is_hac(l):
        return l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_') or (l.startswith('APL_') and not any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']))
    rooms={}
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label()
        if not is_hac(nm): continue
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
            loc=a.get_actor_location()
            K=c.get_editor_property('temperature') if c.get_editor_property('use_temperature') else 0
            r=room(nm)
            rooms.setdefault(r,[]).append({'n':nm,'x':round(loc.x),'y':round(loc.y),'z':round(loc.z),
                'cd':round(c.get_editor_property('intensity'),1),'r':round(c.get_editor_property('attenuation_radius')),'K':round(K),
                't':c.get_class().get_name().replace('Component','')})
    summary={}
    for r,ls in rooms.items():
        rr=[l['r'] for l in ls]; cc=[l['cd'] for l in ls]
        summary[r]={'count':len(ls),'radius_min':min(rr),'radius_max':max(rr),'cd_min':min(cc),'cd_max':max(cc)}
    out['summary']=summary
    out['rooms']=rooms
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hacdump.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-600:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/hacdump.json','w').write(json.dumps(out,indent=1))
