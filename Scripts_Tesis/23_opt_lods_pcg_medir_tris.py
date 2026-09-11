# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:35
# Que hace este script: Da LODs al follaje PCG y mide triangulos renderizados.
# Por que se necesito: Cerrar los LODs y medir el efecto.
# Resultado obtenido: Medicion estatica poco fiable.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    EAL=unreal.EditorAssetLibrary
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    # fix any remaining 1-LOD foliage/tree meshes
    def make_opts():
        rs=[]
        for p in [0.4,0.15,0.05]:
            s=unreal.EditorScriptingMeshReductionSettings(); s.set_editor_property('percent_triangles',p); rs.append(s)
        o=unreal.EditorScriptingMeshReductionOptions(); o.set_editor_property('auto_compute_lod_screen_size',True); o.set_editor_property('reduction_settings',rs); return o
    fixed=[]
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','StaticMesh'),True):
        nm=str(ad.asset_name); pn=str(ad.package_name)
        if not pn.startswith('/Game'): continue
        if any(k in nm for k in ['PCG_Tree','Tree','Arbol','Plant','Foliage','Shrub','Bush','Grass']):
            m=EAL.load_asset(pn)
            if not m: continue
            try:
                if m.get_num_lods()<=1:
                    unreal.EditorStaticMeshLibrary.set_lods(m,make_opts()); EAL.save_loaded_asset(m); fixed.append(nm)
            except: pass
    out['extra_foliage_lodded']=fixed
    # measure rendered tris within cull, per zone
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    def zone(x,y):
        if abs(x)<1800 and -2600<y<600: return 'Plaza'
        if -9300<x<-4700 and -3300<y<-400: return 'Hacienda'
        if 4400<x<9900 and 3100<y<6900: return 'Convento'
        if -1600<x<1600 and 9500<y<14200: return 'Templo'
        return 'Caminos'
    VP={'Plaza':(0,-1000,200),'Hacienda':(-7000,-1500,300),'Convento':(6500,5000,300),'Templo':(0,12000,300),'Caminos':(0,3000,200)}
    before={z:0 for z in VP}; after={z:0 for z in VP}
    tcache={}
    def tris0(m):
        k=m.get_name()
        if k in tcache: return tcache[k]
        try: t=m.get_num_triangles(0)
        except: t=0
        tcache[k]=t; return t
    for a in eas.get_all_level_actors():
        loc=a.get_actor_location(); z=zone(loc.x,loc.y); vp=VP[z]
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            try:
                m=c.static_mesh
                if not m: continue
                t0=tris0(m); N=c.get_instance_count()
                if N==0 or t0==0: continue
                D=c.get_editor_property('instance_end_cull_distance') or 0
                before[z]+=t0*N
                if D<=0:
                    after[z]+=t0*N; continue
                # sample instances for fraction within cull
                step=max(1,N//400); inside=0; sampled=0
                i=0
                while i<N:
                    tr=c.get_instance_transform(i,True); p=tr.translation
                    if (p.x-vp[0])**2+(p.y-vp[1])**2+(p.z-vp[2])**2 <= D*D: inside+=1
                    sampled+=1; i+=step
                frac=inside/max(1,sampled)
                after[z]+=int(t0*N*frac)
            except: pass
    out['tris_before']={z:int(v) for z,v in before.items()}
    out['tris_after_within_cull']={z:int(v) for z,v in after.items()}
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt4.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt4.json','w').write(json.dumps(out,indent=1))
