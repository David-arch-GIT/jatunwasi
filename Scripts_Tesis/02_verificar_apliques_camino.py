# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 15:27
# Que hace este script: Cuenta apliques y luces de camino existentes.
# Por que se necesito: Revisar el estado tras la edicion manual del usuario.
# Resultado obtenido: Detecto actores de aplique duplicados.
# ------------------------------------------------------------

import unreal, json
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
apl_props=[]; apl_lights=[]; test=[]; camino_farolL=[]
for a in eas.get_all_level_actors():
    nm=a.get_actor_label()
    if nm=='APL_TEST' or nm=='APL_TEST_L': test.append(nm)
    if nm.startswith('APL_') and nm.endswith('_L'): apl_lights.append(nm)
    elif nm.startswith('APL_'): apl_props.append(nm)
    if nm.startswith('LC_FarolL_'): camino_farolL.append(nm)
out={'apl_props':sorted(apl_props),'n_props':len(apl_props),'n_lights':len(apl_lights),
     'stray_test':test,'camino_farol_lights':sorted(camino_farolL)}
# save map (no lighting change)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/p1.json','w').write(json.dumps(out,indent=0))
