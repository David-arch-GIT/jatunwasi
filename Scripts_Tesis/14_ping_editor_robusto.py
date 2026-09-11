# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:09
# Que hace este script: Ping con captura de error y estado del mapa.
# Por que se necesito: Confirmar el estado real tras el corte.
# Resultado obtenido: Mapa de trabajo cargado con 105 luces.
# ------------------------------------------------------------

import unreal, json, traceback
o={}
try:
    EAL=unreal.EditorAssetLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    w=ues.get_editor_world()
    o['level']=str(w.get_name()) if w else 'NONE'
    o['CLEAN']=EAL.does_asset_exist('/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN')
    o['RECOVER']=EAL.does_asset_exist('/Game/JWN/MAP_RECOVER_141')
    acts=eas.get_all_level_actors()
    o['n_actors']=len(acts)
    n=0
    for a in acts:
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'): n+=1
    o['lights']=n
except Exception as e:
    o['err']=str(e); o['tb']=traceback.format_exc()[-400:]
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ping2.json','w').write(json.dumps(o))
