# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Lee cortes de distancia (cull) de todos los ISM y busca colisiones en puertas de la Hacienda.
# Por que se necesito: El horizonte se ve plano (follaje no carga) y hay colisiones que bloquean puertas.
# Resultado obtenido: (ver salida) - valores de cull por follaje y actores con colision en la Hacienda.
import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # bridge sanity: light count
    n=sum(1 for a in eas.get_all_level_actors() for c in a.get_components_by_class(unreal.LightComponentBase) if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'))
    out['light_count']=n
    # ISM cull values
    isms=[]
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            mn=''
            try:
                if c.static_mesh: mn=c.static_mesh.get_name()
            except: pass
            try: end=c.get_editor_property('instance_end_cull_distance')
            except: end=-1
            isms.append([a.get_actor_label(),mn,c.get_instance_count(),end])
    out['isms']=isms
    # Hacienda door/collision candidates
    col=[]
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label(); loc=a.get_actor_location()
        if not (-9500<loc.x<-4500 and -3600<loc.y<-300): continue
        low=nm.lower()
        if any(k in low for k in ['col_','door','puerta','maindoor','collision','shutter','ventana','window','frame']):
            smc=a.get_component_by_class(unreal.StaticMeshComponent)
            prof=''; ctype=''
            if smc:
                try: prof=str(smc.get_collision_profile_name())
                except: pass
                try: ctype=str(smc.get_collision_enabled())
                except: pass
            col.append([nm,round(loc.x),round(loc.y),round(loc.z),prof,ctype])
    out['hac_collision_actors']=col
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_carga.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_carga.json','w').write(json.dumps(out,indent=1))
