# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Mapea cobertura de NavMesh en la entrada de la Hacienda y planta baja del Convento; lee config del agente.
# Por que se necesito: El usuario no puede ENTRAR a la Hacienda ni a la planta baja del Convento (bloqueo por NavMesh).
# Resultado obtenido: (ver salida) - puntos con/sin navmesh y parametros del agente.
import unreal, json, traceback
out={'err':None}
try:
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); world=ues.get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ns=unreal.NavigationSystemV1
    # agent config from RecastNavMesh
    for a in eas.get_all_level_actors():
        if a.get_class().get_name()=='RecastNavMesh':
            for p in ['agent_radius','agent_height','agent_max_step_height','agent_max_slope','cell_size','cell_height','tile_size_uu']:
                try: out[p]=round(float(a.get_editor_property(p)),1)
                except Exception as e: out[p]='?'
            break
    def covered(x,y,z):
        try:
            r=ns.project_point_to_navigation(world, unreal.Vector(x,y,z), None, None, unreal.Vector(200,200,300))
            if r is None: return 0
            dx=r.x-x; dy=r.y-y; dz=r.z-z
            d=(dx*dx+dy*dy+dz*dz)**0.5
            if abs(r.x)<1 and abs(r.y)<1 and abs(r.z)<1: return 0
            return 1 if d<350 else 0
        except: return -1
    # Hacienda entrance line (south approach into building), x=-7000
    hac=[]
    y=-3600
    while y<=-1400:
        hac.append([y, covered(-7000,y,60)])
        y+=150
    out['hac_entrance_x-7000']=hac
    # also across the door width at y=-2500
    hacw=[]
    x=-7600
    while x<=-6400:
        hacw.append([x, covered(x,-2500,60)])
        x+=150
    out['hac_door_y-2500']=hacw
    # Convento ground: sample around cloister approach
    conv=[]
    y=3000
    while y<=5200:
        conv.append([y, covered(6500,y,200)])
        y+=200
    out['conv_ground_x6500']=conv
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_entrada.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_entrada.json','w').write(json.dumps(out,indent=1))
