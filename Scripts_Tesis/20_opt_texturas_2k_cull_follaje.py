# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:28
# Que hace este script: Baja texturas a 2K y corta el follaje ISM por distancia.
# Por que se necesito: Reducir memoria de textura y follaje renderizado.
# Resultado obtenido: Menos 1757 MB de textura; 229 ISM con corte.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    EAL=unreal.EditorAssetLibrary
    # ---- A. Textures > 2048 -> max_texture_size 2048 ----
    px_before=0; px_after=0; changed=0; saved_assets=[]
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','Texture2D'),True):
        pn=str(ad.package_name)
        if not pn.startswith('/Game'): continue
        dim=ad.get_tag_value('Dimensions'); w=h=0
        if dim:
            s=str(dim).lower().replace(' ','')
            for sep in ['x','X']:
                if sep in s:
                    try: w=int(s.split(sep)[0]); h=int(s.split(sep)[1].split('(')[0])
                    except: pass
                    break
        if max(w,h)>2048:
            t=EAL.load_asset(pn)
            if not t: continue
            try:
                cur=t.get_editor_property('max_texture_size')
            except: cur=0
            t.set_editor_property('max_texture_size',2048)
            EAL.save_loaded_asset(t)
            changed+=1
            px_before += w*h
            sw=min(w,2048); sh=min(h,2048)
            # scale to keep aspect under 2048
            if w>=h and w>2048: sh=int(h*2048/w); sw=2048
            elif h>w and h>2048: sw=int(w*2048/h); sh=2048
            px_after += sw*sh
    # bytes approx: BC/BC7 ~0.9 byte/px incl mips
    mb_before=px_before*0.9/1048576.0; mb_after=px_after*0.9/1048576.0
    out['textures_changed']=changed
    out['tex_mem_before_MB']=round(mb_before); out['tex_mem_after_MB']=round(mb_after)
    out['tex_mem_saved_MB']=round(mb_before-mb_after)
    # ---- B. Foliage / ISM cull distance ----
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    ism_set=0; foliage_types=0
    def name_bucket(nm):
        n=nm.lower()
        if any(k in n for k in ['grass','cesped','césped','weed','fern','helecho']): return 3000
        if any(k in n for k in ['shrub','arbust','boxwood','bush','flower','plant','planta','maceta']): return 6000
        return 9000
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
            mn=''
            try:
                if c.static_mesh: mn=c.static_mesh.get_name()
            except: pass
            d=name_bucket(mn)
            try:
                c.set_editor_property('instance_start_cull_distance',int(d*0.75))
                c.set_editor_property('instance_end_cull_distance',int(d))
                ism_set+=1
            except: pass
    # InstancedFoliageActor foliage types
    try:
        for a in eas.get_all_level_actors():
            if a.get_class().get_name()=='InstancedFoliageActor':
                for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
                    mn=''
                    try:
                        if c.static_mesh: mn=c.static_mesh.get_name()
                    except: pass
                    d=name_bucket(mn)
                    try:
                        c.set_editor_property('instance_start_cull_distance',int(d*0.75))
                        c.set_editor_property('instance_end_cull_distance',int(d)); foliage_types+=1
                    except: pass
    except Exception as e: out['foliage_err']=str(e)[:120]
    out['ism_cull_set']=ism_set; out['foliage_comp_cull_set']=foliage_types
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt1.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt1.json','w').write(json.dumps(out,indent=1))
