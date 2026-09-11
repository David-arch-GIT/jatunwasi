# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:11
# Que hace este script: Coloca la camara del visor y activa game view.
# Por que se necesito: Tomar capturas a altura de ojos sin guias.
# Resultado obtenido: Helper reutilizado en todas las capturas.
# ------------------------------------------------------------

import unreal, json
p=json.load(open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cap_params.json'))
try: unreal.get_editor_subsystem(unreal.EditorActorSubsystem).set_selected_level_actors([])
except: pass
ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(float(p['x']),float(p['y']),float(p['z'])),unreal.Rotator(0.0,float(p['p']),float(p['yaw'])))
try: unreal.EditorLevelLibrary.editor_set_game_view(True)
except: pass
