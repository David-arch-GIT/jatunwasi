# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:40
# Que hace este script: Elimina el cull distance volume del mapa.
# Por que se necesito: El volumen ocultaba el edificio lejano de la Plaza.
# Resultado obtenido: Volumen retirado; edificio recuperado.
# ------------------------------------------------------------

import unreal, json
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
rm=0
for a in list(eas.get_all_level_actors()):
    if a.get_actor_label()=='JW_CullVolume': eas.destroy_actor(a); rm+=1
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/delcv.json','w').write(json.dumps({'removed':rm}))
