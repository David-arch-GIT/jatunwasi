# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Pone los muros del 2o piso en colision compleja (respeta vanos) y reconstruye el NavMesh.
# Por que se necesito: El usuario no puede pasar por las puertas de la Hacienda (NavMesh no conecta los vanos).
# Resultado obtenido: (ver salida) - colision de muros ajustada y navegacion reconstruida.
import unreal, json, traceback
out={'err':None,'steps':[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ues=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem); world=ues.get_editor_world()
    EAL=unreal.EditorAssetLibrary
    # set Upper walls mesh to complex-as-simple (respect door holes)
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=='HACV7_EXP_ExteriorWalls_Upper':
            smc=a.get_component_by_class(unreal.StaticMeshComponent)
            try:
                m=smc.static_mesh; bs=m.get_editor_property('body_setup')
                bs.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
                EAL.save_loaded_asset(m); out['steps'].append('Upper walls -> complex collision')
            except Exception as e: out['upper_err']=str(e)[:80]
    # read recast agent settings
    for a in eas.get_all_level_actors():
        if a.get_class().get_name()=='RecastNavMesh':
            for p in ['agent_radius','agent_height','agent_max_step_height','cell_size']:
                try: out[p]=round(a.get_editor_property(p),1)
                except: pass
    # rebuild navigation
    try:
        unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation'); out['steps'].append('RebuildNavigation ejecutado')
    except Exception as e: out['rebuild_err']=str(e)[:80]
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    lc=sum(1 for a in eas.get_all_level_actors() for cc in a.get_components_by_class(unreal.LightComponentBase) if cc.get_class().get_name() in ('PointLightComponent','SpotLightComponent'))
    out['light_count']=lc
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_puertas.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_puertas.json','w').write(json.dumps(out,indent=1))
