# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:03
# Que hace este script: Carga el autosave recuperado y cuenta sus luces.
# Por que se necesito: Recuperar el arreglo denso del usuario.
# Resultado obtenido: Cargadas 141 luces, 0 sombras.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None,'steps':[]}
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    ar.scan_paths_synchronous(['/Game/JWN'],True)
    out['exists']=unreal.EditorAssetLibrary.does_asset_exist('/Game/JWN/MAP_RECOVER_141')
    # try load
    w=unreal.EditorLoadingAndSavingUtils.load_map('/Game/JWN/MAP_RECOVER_141')
    out['loaded']= w is not None
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    n=0; nshadow=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'):
                n+=1
                if bool(c.get_editor_property('cast_shadows')): nshadow+=1
    out['light_count']=n; out['shadows']=nshadow
    out['current_map']=eas.get_all_level_actors()[0].get_world().get_name() if eas.get_all_level_actors() else '?'
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/lr.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-600:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/lr.json','w').write(json.dumps(out,indent=1))
