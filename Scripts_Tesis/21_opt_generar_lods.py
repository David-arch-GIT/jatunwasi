# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 16:29
# Que hace este script: Genera LODs automaticos en las mallas sin LODs.
# Por que se necesito: Reducir geometria a distancia.
# Resultado obtenido: 172 mallas con 3-4 LODs.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None,'done':[],'failed':[],'api':None}
try:
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    EAL=unreal.EditorAssetLibrary
    # gather no-LOD static meshes with tri counts
    cand=[]
    for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath('/Script/Engine','StaticMesh'),True):
        pn=str(ad.package_name)
        if not pn.startswith('/Game'): continue
        lods=ad.get_tag_value('LODs') or ad.get_tag_value('Number of LODs')
        try: n=int(str(lods)) if lods else None
        except: n=None
        if n==1:
            tris=ad.get_tag_value('Triangles') or ad.get_tag_value('TrianglesLOD0')
            try: t=int(str(tris)) if tris else 0
            except: t=0
            cand.append((t,pn))
    cand.sort(reverse=True)
    out['nolod_total']=len(cand); out['top_tris']=[[c[1].split('/')[-1],c[0]] for c in cand[:10]]
    # build reduction options
    def make_opts():
        rs=[]
        for p in [0.5,0.2,0.06]:
            s=unreal.EditorScriptingMeshReductionSettings()
            s.set_editor_property('percent_triangles',p)
            rs.append(s)
        o=unreal.EditorScriptingMeshReductionOptions()
        o.set_editor_property('auto_compute_lod_screen_size',True)
        o.set_editor_property('reduction_settings',rs)
        return o
    opts=make_opts()
    # apply to top N by tris (bounded to avoid timeout)
    N=45
    for t,pn in cand[:N]:
        m=EAL.load_asset(pn)
        if not m: out['failed'].append(pn.split('/')[-1]); continue
        ok=False
        try:
            unreal.EditorStaticMeshLibrary.set_lods(m,opts); ok=True; out['api']='EditorStaticMeshLibrary'
        except Exception as e1:
            try:
                sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem); sub.set_lods(m,opts); ok=True; out['api']='StaticMeshEditorSubsystem'
            except Exception as e2:
                out.setdefault('apierr',str(e1)[:100]+' | '+str(e2)[:100])
        if ok:
            EAL.save_loaded_asset(m); out['done'].append(pn.split('/')[-1])
        else:
            out['failed'].append(pn.split('/')[-1])
    out['done_count']=len(out['done'])
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt2.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/opt2.json','w').write(json.dumps(out,indent=1))
