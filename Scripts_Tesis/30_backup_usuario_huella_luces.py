# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 17:22
# Que hace este script: Crea el backup del estado del usuario y huella de las luces.
# Por que se necesito: Proteger el estado que el usuario armo a mano.
# Resultado obtenido: Backup LUCES_USUARIO y huella de 111 luces.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    EAL=unreal.EditorAssetLibrary
    LES=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    LES.save_current_level()
    src=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_path_name().split(':')[0].split('.')[0]
    dst=src+'_BACKUP_LUCES_USUARIO'
    if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
    ok=EAL.duplicate_asset(src,dst)
    if ok: EAL.save_asset(dst)
    out['backup_made']=bool(ok); out['backup_path']=dst; out['src']=src
    # baseline light fingerprint
    lights=[]
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            cls=c.get_class().get_name()
            if cls not in ('PointLightComponent','SpotLightComponent','DirectionalLightComponent','SkyLightComponent'): continue
            loc=a.get_actor_location()
            rec={'n':a.get_actor_label(),'cls':cls,'x':round(loc.x),'y':round(loc.y),'z':round(loc.z)}
            try: rec['cd']=round(c.get_editor_property('intensity'),2)
            except: pass
            try: rec['r']=round(c.get_editor_property('attenuation_radius'))
            except: pass
            try: rec['K']=round(c.get_editor_property('temperature')) if c.get_editor_property('use_temperature') else 0
            except: pass
            lights.append(rec)
    lights.sort(key=lambda r:r['n'])
    out['light_count']=len(lights)
    out['baseline']=lights
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/baseline_lights.json','w').write(json.dumps(lights,indent=0))
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/backup_user.json','w').write(json.dumps({k:v for k,v in out.items() if k!='baseline'},indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-500:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/backup_user.json','w').write(json.dumps({k:v for k,v in out.items() if k!='baseline'},indent=1))
