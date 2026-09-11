# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Sube la altura de escalon del agente de NavMesh y reconstruye (refuerzo para entradas).
# Por que se necesito: El pawn se frena en las puertas; refuerzo por si hay un umbral que corta el navmesh.
# Resultado obtenido: (ver salida)
import unreal, json, traceback
out={'err':None,'steps':[]}
try:
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); world=ues.get_editor_world()
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        if a.get_class().get_name()=='RecastNavMesh':
            for prop,val in [('agent_max_step_height',60.0)]:
                try:
                    old=a.get_editor_property(prop); a.set_editor_property(prop,val)
                    out['steps'].append('%s %s->%s'%(prop,old,val))
                except Exception as e: out['set_err_'+prop]=str(e)[:80]
            break
    try:
        unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation'); out['steps'].append('RebuildNavigation')
    except Exception as e: out['rebuild_err']=str(e)[:80]
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # re-verify paths + lights
    ns=unreal.NavigationSystemV1
    def path(s,e):
        p=ns.find_path_to_location_synchronously(world, unreal.Vector(*s), unreal.Vector(*e))
        try: return [bool(p.is_valid()), len(p.path_points)] if p else [False,0]
        except: return [bool(p),0]
    out['path_hac']=path((-7000,-3450,40),(-6700,-1300,90))
    out['path_conv']=path((6300,2950,150),(6300,4600,200))
    out['light_count']=sum(1 for a in eas.get_all_level_actors() for cc in a.get_components_by_class(unreal.LightComponentBase) if cc.get_class().get_name() in ('PointLightComponent','SpotLightComponent'))
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nav_step.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/nav_step.json','w').write(json.dumps(out,indent=1))
