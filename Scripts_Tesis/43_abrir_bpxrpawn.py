# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Abre BP_XRPawn en el editor para que el usuario corrija el nodo Set Actor Location (Sweep off).
# Por que se necesito: El pawn choca con el marco de la puerta; el fix es desmarcar Sweep (Python no edita BP).
# Resultado obtenido: BP abierto.
import unreal, json
bp=unreal.EditorAssetLibrary.load_asset('/Game/XRFramework/Blueprints/BP_XRPawn')
ok=False
try: unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp]); ok=True
except: pass
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/open_bp.json','w').write(json.dumps({'opened':ok}))
