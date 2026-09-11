# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:02
# Que hace este script: Comprueba si el autosave es direccionable como asset.
# Por que se necesito: Recuperar las 141 luces perdidas.
# Resultado obtenido: El autosave no estaba en el Content.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    # ensure current saved
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    autop='/Game/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN_Auto5'
    # autosaves live under /Game/JWN/? They are in Saved/Autosaves. Need the load path form.
    # Try loading via EditorLoadingAndSavingUtils with the on-disk-mapped package path
    exists=unreal.EditorAssetLibrary.does_asset_exist(autop)
    out['autopkg_exists_in_content']=exists
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/la.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-500:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/la.json','w').write(json.dumps(out,indent=1))
