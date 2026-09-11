# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 15:37
# Que hace este script: Duplica el mapa actual a un backup.
# Por que se necesito: Guardar el estado antes de continuar.
# Resultado obtenido: Backup del mapa creado.
# ------------------------------------------------------------

import unreal, json
EAL=unreal.EditorAssetLibrary
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
src=ues.get_editor_world().get_path_name().split(':')[0].split('.')[0]
dst=src+'_BACKUP_LUCES_FINAL'
if EAL.does_asset_exist(dst): EAL.delete_asset(dst)
ok=EAL.duplicate_asset(src,dst)
if ok: EAL.save_asset(dst)
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/bk.json','w').write(json.dumps({'backup':bool(ok)}))
