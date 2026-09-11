# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 17:27
# Que hace este script: Muestrea categorias y detecta mallas duplicadas.
# Por que se necesito: Buscar geometria repetida dibujada dos veces.
# Resultado obtenido: 1 duplicado: PLZP_CanastaChuno y su _Fix.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # sample skip categories to confirm categorization
    LIGHTPROP=['farol','apl_','aplique','vela','candelabr','cirio','lampara','lantern','lamp','gal_','_glow','emis','brasa','fogon']
    samp={'ism':[],'light':[],'arch':[]}
    for a in eas.get_all_level_actors():
        if a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            if len(samp['ism'])<20:
                mn=''
                c=a.get_component_by_class(unreal.InstancedStaticMeshComponent)
                try:
                    if c.static_mesh: mn=c.static_mesh.get_name()
                except: pass
                samp['ism'].append([a.get_actor_label(),mn])
            continue
        nm=a.get_actor_label().lower()
        if any(k in nm for k in LIGHTPROP) and len(samp['light'])<25: samp['light'].append(a.get_actor_label())
    out['sample_ism']=samp['ism']; out['sample_lightprops']=samp['light']
    # ---- duplicate mesh detection (same mesh + same pos + same scale) ----
    from collections import defaultdict
    groups=defaultdict(list)
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_class().get_name()!='StaticMeshComponent': continue  # skip ISM
            m=None
            try: m=c.static_mesh
            except: pass
            if not m: continue
            loc=a.get_actor_location(); s=a.get_actor_scale3d()
            key=(m.get_name(),round(loc.x/10)*10,round(loc.y/10)*10,round(loc.z/10)*10,round(s.x,2),round(s.y,2),round(s.z,2))
            groups[key].append(a.get_actor_label())
    dups=[]
    for k,v in groups.items():
        if len(v)>1: dups.append({'mesh':k[0],'pos':[k[1],k[2],k[3]],'count':len(v),'actors':v[:6]})
    dups.sort(key=lambda d:-d['count'])
    out['duplicate_groups']=len(dups); out['duplicates']=dups[:40]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/dupcheck.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/dupcheck.json','w').write(json.dumps(out,indent=1))
