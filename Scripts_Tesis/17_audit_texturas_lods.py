# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:16
# Que hace este script: Audita texturas mayores a 2K y mallas sin LODs.
# Por que se necesito: Evaluar rendimiento antes de empaquetar.
# Resultado obtenido: 164 texturas mayores a 2K, 172 mallas sin LODs.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    # TEXTURES > 2K (use Dimensions tag; only /Game)
    big=[]; total_tex=0
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','Texture2D'),True):
        pn=str(ad.package_name)
        if not pn.startswith('/Game'): continue
        total_tex+=1
        dim=ad.get_tag_value('Dimensions')
        w=h=0
        if dim:
            s=str(dim).lower().replace(' ','')
            for sep in ['x','X','×']:
                if sep in s:
                    try: w=int(s.split(sep)[0]); h=int(s.split(sep)[1].split('(')[0])
                    except: pass
                    break
        if max(w,h)>2048: big.append([pn.split('/')[-1],w,h])
    big.sort(key=lambda r:-max(r[1],r[2]))
    out['textures_total']=total_tex; out['textures_over_2k']=len(big); out['tex_top']=big[:25]
    # STATIC MESHES without LODs
    nolod=[]; total_sm=0
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','StaticMesh'),True):
        pn=str(ad.package_name)
        if not pn.startswith('/Game'): continue
        total_sm+=1
        lods=ad.get_tag_value('LODs') or ad.get_tag_value('Number of LODs')
        try: n=int(str(lods)) if lods else None
        except: n=None
        if n==1: nolod.append(pn.split('/')[-1])
    out['staticmesh_total']=total_sm; out['sm_no_lods_count']=len(nolod); out['sm_no_lods_sample']=nolod[:30]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit1.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-600:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit1.json','w').write(json.dumps(out,indent=1))
