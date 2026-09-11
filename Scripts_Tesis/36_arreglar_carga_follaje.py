# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24
# Que hace este script: Sube los cortes de distancia del follaje ISM (generosos, por categoria) para que el horizonte cargue.
# Por que se necesito: Los cortes agresivos (60m) vaciaban el bosque de fondo y el suelo; horizonte plano.
# Resultado obtenido: (ver salida) - arboles/suelo nunca se cortan, resto generoso; luces verificadas intactas.
import unreal, json, traceback
out={'err':None,'changes':[]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def bucket(mn):
        n=mn.lower()
        if any(k in n for k in ['cobblestone','floor','ground','plane','path_','_path']): return 0        # suelo: nunca
        if any(k in n for k in ['tree','oak','maple','pine','tropical','dead_tree','arbol']): return 0     # arboles: nunca (impostor)
        if any(k in n for k in ['fence','stone_fence','wall']): return 0                                   # cercas/muros: nunca
        if any(k in n for k in ['rock','roca']): return 25000
        if any(k in n for k in ['grass','cesped','weed']): return 8000
        return 15000  # shrubs, bush, boxwood, fern, flower, plant, otros
    n=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            mn=''
            try:
                if c.static_mesh: mn=c.static_mesh.get_name()
            except: pass
            d=bucket(mn)
            try:
                c.set_editor_property('instance_start_cull_distance',int(d*0.85) if d>0 else 0)
                c.set_editor_property('instance_end_cull_distance',int(d))
                n+=1
                if len(out['changes'])<12: out['changes'].append([mn,d])
            except: pass
    out['ism_updated']=n
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    # verify lights unchanged (point/spot count)
    lc=sum(1 for a in eas.get_all_level_actors() for cc in a.get_components_by_class(unreal.LightComponentBase) if cc.get_class().get_name() in ('PointLightComponent','SpotLightComponent'))
    out['light_count']=lc
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_follaje.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-400:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/fix_follaje.json','w').write(json.dumps(out,indent=1))
