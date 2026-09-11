# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:33
# Que hace este script: Crea cull volume, verifica impostores, corta decals/glows.
# Por que se necesito: Culling en masa y verificar follaje.
# Resultado obtenido: Impostores OK; 105 luces intactas.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    EAL=unreal.EditorAssetLibrary
    # ---- 1. Cull Distance Volume covering the map ----
    # remove old one if present
    for a in list(eas.get_all_level_actors()):
        if a.get_actor_label()=='JW_CullVolume': eas.destroy_actor(a)
    cv=eas.spawn_actor_from_class(unreal.CullDistanceVolume, unreal.Vector(0,5000,400))
    cv.set_actor_label('JW_CullVolume')
    cv.set_actor_scale3d(unreal.Vector(230,340,70))  # ~23000 x 34000 x 7000 box
    pairs=[]
    for sz,dist in [(80,12000),(300,20000),(800,30000),(2000,45000),(6000,0)]:
        p=unreal.CullDistanceSizePair(); p.set_editor_property('size',float(sz)); p.set_editor_property('cull_distance',float(dist)); pairs.append(p)
    try:
        cv.set_editor_property('cull_distances',pairs); out['cull_volume']='created (generous, faroles safe)'
    except Exception as e: out['cv_err']=str(e)[:120]
    # ---- 2. foliage impostor check (tree meshes LOD info) ----
    imp=[]
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','StaticMesh'),True):
        nm=str(ad.asset_name)
        if any(k in nm for k in ['Maple','Oak','Tree','Arbol','Pine']) and 'Impostor' not in nm:
            m=EAL.load_asset(str(ad.package_name))
            if not m: continue
            try: nl=m.get_num_lods()
            except: nl=0
            lastmat=''
            try:
                sms=m.get_editor_property('static_materials')
                lastmat=','.join([str(s.material_slot_name) for s in sms])
            except: pass
            imp.append([nm,nl,'Impostor' if 'impostor' in lastmat.lower() else lastmat[:40]])
    out['tree_lods']=imp[:15]
    # ---- 3. decals + glow props cull ----
    decals=0; glows=0
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.DecalComponent):
            try: c.set_editor_property('fade_screen_size',0.05); decals+=1
            except: pass
        # glow prop meshes by material name
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                mats=[mm.get_name().lower() for mm in c.get_materials() if mm]
                if any(('glow' in x or 'halo' in x or 'apparition' in x) for x in mats):
                    c.set_editor_property('desired_max_draw_distance',6000.0); glows+=1
            except: pass
    out['decals_faded']=decals; out['glow_props_culled']=glows
    # ---- 4. verify lights unchanged ----
    n=0; sh=0; zc={}
    def zone_of(l):
        if l.startswith('LP_'): return 'Plaza'
        if l.startswith('LC_'): return 'Caminos'
        if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
        if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
        if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
        if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
        return 'Otro'
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            if c.get_class().get_name() in ('PointLightComponent','SpotLightComponent'):
                n+=1
                if bool(c.get_editor_property('cast_shadows')): sh+=1
                z=zone_of(a.get_actor_label()); zc[z]=zc.get(z,0)+1
    out['lights_total']=n; out['shadows']=sh; out['lights_per_zone']=zc
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt3.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt3.json','w').write(json.dumps(out,indent=1))
