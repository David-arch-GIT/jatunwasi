# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:09
# Que hace este script: Ping simple para ver si el editor responde.
# Por que se necesito: El puente MCP dejo de responder.
# Resultado obtenido: Editor respondia pero sin escribir archivo.
# ------------------------------------------------------------

import unreal, json
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
n=sum(1 for a in eas.get_all_level_actors() for c in a.get_components_by_class(unreal.LightComponentBase) if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'))
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/ping.json','w').write(json.dumps({'level':w.get_name() if w else '?','lights':n}))
