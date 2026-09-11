# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:37
# Que hace este script: Aprieta el corte de follaje y mide tris por frame.
# Por que se necesito: Intentar una medicion realista.
# Resultado obtenido: Camino menos 85 por ciento; metrica no concluyente.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    # tighten foliage cull
    def bucket(nm):
        n=nm.lower()
        if any(k in n for k in ['grass','cesped','weed','fern','helecho']): return 2000
        if any(k in n for k in ['shrub','arbust','boxwood','bush','flower','plant','planta','maceta']): return 3500
        return 6000
    changed=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            mn=''
            try:
                if c.static_mesh: mn=c.static_mesh.get_name()
            except: pass
            d=bucket(mn)
            try:
                c.set_editor_property('instance_start_cull_distance',int(d*0.7)); c.set_editor_property('instance_end_cull_distance',int(d)); changed+=1
            except: pass
    out['foliage_recull']=changed
    # realistic per-frame tris (LOD by distance) per zone
    def zone(x,y):
        if abs(x)<1800 and -2600<y<600: return 'Plaza'
        if -9300<x<-4700 and -3300<y<-400: return 'Hacienda'
        if 4400<x<9900 and 3100<y<6900: return 'Convento'
        if -1600<x<1600 and 9500<y<14200: return 'Templo'
        return 'Caminos'
    VP={'Plaza':(0,-1000,200),'Hacienda':(-7000,-1500,300),'Convento':(6500,5000,300),'Templo':(0,12000,300),'Caminos':(0,3000,200)}
    lodcache={}
    def lodtris(m,li):
        k=(m.get_name(),li)
        if k in lodcache: return lodcache[k]
        try: t=m.get_num_triangles(li)
        except: t=0
        lodcache[k]=t; return t
    def pick_lod(m,d):
        nl=1
        try: nl=m.get_num_lods()
        except: nl=1
        if d<1500: li=0
        elif d<3500: li=min(1,nl-1)
        elif d<6000: li=min(2,nl-1)
        else: li=min(3,nl-1)
        return lodtris(m,li)
    before={z:0 for z in VP}; after={z:0 for z in VP}
    for a in eas.get_all_level_actors():
        loc=a.get_actor_location(); z=zone(loc.x,loc.y); vx,vy,vz=VP[z]
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                m=c.static_mesh
                if not m: continue
                N=c.get_instance_count()
                if N==0: continue
                D=c.get_editor_property('instance_end_cull_distance') or 0
                step=max(1,N//350); i=0; s_before=0; s_after=0; sampled=0
                while i<N:
                    p=c.get_instance_transform(i,True).translation
                    d=((p.x-vx)**2+(p.y-vy)**2+(p.z-vz)**2)**0.5
                    s_before+=pick_lod(m,d)          # LODs but no cull
                    if D<=0 or d<=D: s_after+=pick_lod(m,d)  # cull applied
                    sampled+=1; i+=step
                scale=N/max(1,sampled)
                before[z]+=int(s_before*scale); after[z]+=int(s_after*scale)
            except: pass
    out['perframe_tris_LODonly']={z:int(v) for z,v in before.items()}
    out['perframe_tris_LOD_plus_cull']={z:int(v) for z,v in after.items()}
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt5.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt5.json','w').write(json.dumps(out,indent=1))
