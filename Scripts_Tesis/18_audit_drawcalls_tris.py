# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:17
# Que hace este script: Audita draw calls, triangulos, culling y tick por zona.
# Por que se necesito: Evaluar rendimiento antes de empaquetar.
# Resultado obtenido: Follaje como principal costo; 630 props sin culling.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def zone(x,y):
        if abs(x)<1800 and -2600<y<600: return 'Plaza'
        if -9300<x<-4700 and -3300<y<-400: return 'Hacienda'
        if 4400<x<9900 and 3100<y<6900: return 'Convento'
        if -1600<x<1600 and 9500<y<14200: return 'Templo'
        return 'Caminos/Otro'
    Z=['Plaza','Hacienda','Convento','Templo','Caminos/Otro']
    dc={z:0 for z in Z}      # static mesh components (draw-call proxy)
    ism={z:0 for z in Z}     # ISM/HISM components
    tris={z:0 for z in Z}
    nocull={z:0 for z in Z}; nocull_tot=0
    tick_actors=0; tick_list=[]
    tricache={}
    def mesh_tris(m):
        k=m.get_name()
        if k in tricache: return tricache[k]
        t=0
        try: t=m.get_num_triangles(0)
        except:
            try: t=unreal.EditorStaticMeshLibrary.get_number_triangles(m,0)
            except: t=0
        tricache[k]=t; return t
    transl=set(); masked=set()
    for a in eas.get_all_level_actors():
        loc=a.get_actor_location(); z=zone(loc.x,loc.y)
        # tick
        try:
            pt=a.get_editor_property('primary_actor_tick')
            if pt and pt.get_editor_property('start_with_tick_enabled'):
                tick_actors+=1
                if len(tick_list)<40: tick_list.append(a.get_actor_label())
        except: pass
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            cls=c.get_class().get_name()
            isism='Instanced' in cls
            if isism: ism[z]+=1
            else: dc[z]+=1
            # cull
            try:
                mdd=c.get_editor_property('desired_max_draw_distance') or c.get_cached_max_draw_distance()
            except:
                mdd=0
            try:
                if (not mdd or mdd<=0): nocull[z]+=1; nocull_tot+=1
            except: pass
            # tris
            try:
                m=c.static_mesh
                if m:
                    cnt=1
                    if isism:
                        try: cnt=max(1,c.get_instance_count())
                        except: cnt=1
                    tris[z]+=mesh_tris(m)*cnt
            except: pass
            # materials blend mode
            try:
                for mi in c.get_materials():
                    if not mi: continue
                    bm=str(mi.get_base_material().get_editor_property('blend_mode')) if hasattr(mi,'get_base_material') and mi.get_base_material() else ''
                    if 'Translucent' in bm: transl.add(mi.get_name())
                    elif 'Masked' in bm: masked.add(mi.get_name())
            except: pass
    out['draw_calls_per_zone']=dc
    out['ism_components_per_zone']=ism
    out['tris_per_zone']={z:int(v) for z,v in tris.items()}
    out['props_no_cull_total']=nocull_tot; out['props_no_cull_per_zone']=nocull
    out['tick_actors']=tick_actors; out['tick_sample']=tick_list
    out['translucent_materials']=len(transl); out['masked_materials']=len(masked)
    out['masked_sample']=list(masked)[:20]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit2.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit2.json','w').write(json.dumps(out,indent=1))
