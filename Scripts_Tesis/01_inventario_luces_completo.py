# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 13:39
# Que hace este script: Vuelca todas las luces, apliques y perillas globales a JSON.
# Por que se necesito: El usuario pidio ver todo para editarlo el mismo.
# Resultado obtenido: Inventario completo de la iluminacion generado.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None,'lights':[],'apl_props':[],'globals':{},'emissive':{}}
try:
    EAL=unreal.EditorAssetLibrary; MEL=unreal.MaterialEditingLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label()
        try: folder=str(a.get_folder_path())
        except: folder=''
        for c in a.get_components_by_class(unreal.LightComponentBase):
            cls=c.get_class().get_name()
            if cls not in ('PointLightComponent','SpotLightComponent'): continue
            loc=a.get_actor_location()
            temp=c.get_editor_property('temperature') if c.get_editor_property('use_temperature') else 0
            out['lights'].append({'n':nm,'f':folder,'t':cls.replace('Component',''),
                'x':round(loc.x),'y':round(loc.y),'z':round(loc.z),
                'cd':round(c.get_editor_property('intensity'),1),'r':round(c.get_editor_property('attenuation_radius')),
                'K':round(temp),'sh':bool(c.get_editor_property('cast_shadows')),'md':round(c.get_editor_property('max_draw_distance'))})
        if nm.startswith('APL_') and not nm.endswith('_L'):
            loc=a.get_actor_location(); out['apl_props'].append({'n':nm,'f':folder,'x':round(loc.x),'y':round(loc.y),'z':round(loc.z)})
        # globals
        if nm=='PP_Master_Noche':
            s=a.get_editor_property('settings')
            out['globals']['EV100']=round(s.get_editor_property('auto_exposure_min_brightness'),2)
            out['globals']['Bloom']=round(s.get_editor_property('bloom_intensity'),2)
        for c in a.get_components_by_class(unreal.SkyLightComponent):
            out['globals']['SkyLight']=round(c.get_editor_property('intensity'),2)
        for c in a.get_components_by_class(unreal.DirectionalLightComponent):
            if 'Moon' in nm or 'moon' in nm: out['globals']['Moon']=round(c.get_editor_property('intensity'),2)
    for mi in ['M_Emis_FarolCalido','M_Emis_Vela','M_Emis_Brasa','M_Emis_Ventana']:
        m=EAL.load_asset('/Game/JWN/Lighting/'+mi)
        if m:
            try: out['emissive'][mi]=round(MEL.get_material_instance_scalar_parameter_value(m,'Intensidad'),2)
            except: pass
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/dump.json','w').write(json.dumps(out,indent=0))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-600:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/dump.json','w').write(json.dumps(out,indent=0))
