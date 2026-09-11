# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 15:28
# Que hace este script: Lista cada aplique/farol con posicion e indica si es luz o malla.
# Por que se necesito: Saber si los duplicados estaban apilados en el mismo punto.
# Resultado obtenido: Duplicados repartidos, no apilados.
# ------------------------------------------------------------

import unreal, json
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lights=0; meshes=0; rows=[]
for a in eas.get_all_level_actors():
    nm=a.get_actor_label()
    if not (nm.startswith('APL_') or nm.startswith('LC_FarolL_')): continue
    haslight=len(a.get_components_by_class(unreal.PointLightComponent))>0
    loc=a.get_actor_location()
    rows.append([nm,'LIGHT' if haslight else 'MESH',round(loc.x),round(loc.y),round(loc.z)])
    if haslight: lights+=1
    else: meshes+=1
# detect stacked lights (same rounded pos)
from collections import Counter
poscount=Counter()
for nm,t,x,y,z in rows:
    if t=='LIGHT': poscount[(x//50,y//50,z//50)]+=1
stacks=[(k,v) for k,v in poscount.items() if v>1]
out={'total_APL_LCFarolL':len(rows),'lights':lights,'meshes':meshes,
     'stacked_light_spots':len(stacks),'max_stack':max([v for _,v in stacks],default=1),
     'rows':rows}
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/p1d.json','w').write(json.dumps(out,indent=0))
