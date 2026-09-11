# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Revisa colision de muros de la Hacienda (simple/compleja), mallas de puerta y presencia de NavMesh.
# Por que se necesito: El usuario no puede pasar por las puertas de la Hacienda (bloqueo).
# Resultado obtenido: (ver salida)
import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def trace_flag(smc):
        try:
            m=smc.static_mesh
            bs=m.get_editor_property('body_setup')
            return str(bs.get_editor_property('collision_trace_flag'))
        except Exception as e: return 'err:'+str(e)[:40]
    walls=[]; doors=[]; navvol=[]; recast=0
    for a in eas.get_all_level_actors():
        nm=a.get_actor_label(); cls=a.get_class().get_name(); loc=a.get_actor_location()
        low=nm.lower()
        if 'NavMeshBounds' in cls or 'navmeshbounds' in low:
            try:
                o=a.get_actor_bounds(False); e=o[1]
                navvol.append([nm,round(loc.x),round(loc.y),round(loc.z),round(e.x),round(e.y),round(e.z)])
            except: navvol.append([nm,round(loc.x),round(loc.y),round(loc.z)])
        if 'RecastNavMesh' in cls: recast+=1
        # Hacienda region
        if -9500<loc.x<-4500 and -3600<loc.y<-300:
            smc=a.get_component_by_class(unreal.StaticMeshComponent)
            if not smc: continue
            if any(k in low for k in ['exteriorwalls','interiorwalls','_wall','foundation']):
                walls.append([nm,str(smc.get_collision_profile_name()),str(smc.get_collision_enabled()),trace_flag(smc)])
            if 'door' in low or 'puerta' in low or 'maindoor' in low:
                doors.append([nm,round(loc.x),round(loc.y),round(loc.z),str(smc.get_collision_profile_name()),str(smc.get_collision_enabled())])
    out['walls']=walls; out['doors']=doors; out['navmesh_volumes']=navvol; out['recast_navmesh_actors']=recast
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_puertas.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_puertas.json','w').write(json.dumps(out,indent=1))
