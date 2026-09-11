# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:08
# Que hace este script: Diagnostica que mapa esta cargado y cuantas luces tiene.
# Por que se necesito: El puente se corto a media operacion.
# Resultado obtenido: Confirmado: mapa de trabajo con 105 luces.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    EAL=unreal.EditorAssetLibrary
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    out['current_level']=w.get_name() if w else '?'
    out['CLEAN_exists']=EAL.does_asset_exist('/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN')
    out['RECOVER_exists']=EAL.does_asset_exist('/Game/JWN/MAP_RECOVER_141')
    out['BACKUP_exists']=EAL.does_asset_exist('/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN_BACKUP_LUCES_FINAL')
    n=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'): n+=1
    out['current_lightcount']=n
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-500:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag.json','w').write(json.dumps(out,indent=1))
