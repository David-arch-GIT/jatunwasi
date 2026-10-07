import unreal, json, traceback
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_build.json"
res={"steps":[],"err":None}
try:
    at=unreal.AssetToolsHelpers.get_asset_tools()
    EAL=unreal.EditorAssetLibrary
    eas=unreal.EditorActorSubsystem()
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    _cache={}
    def pkgfor(name):
        if not _cache:
            for ad in ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","StaticMesh"), True):
                _cache[str(ad.asset_name)]=str(ad.package_name)
        return _cache.get(name)
    def meshes(names):
        out=[]
        for n in names:
            p=pkgfor(n)
            if p and EAL.does_asset_exist(p): out.append(EAL.load_asset(p))
        return out
    gpath="/Game/JWN/PCG"; gname="PCG_Relieve"; full=gpath+"/"+gname
    if EAL.does_asset_exist(full):
        g=EAL.load_asset(full)
        for n in list(g.nodes):
            try: g.remove_node(n)
            except: pass
        res["steps"].append("reused+cleared")
    else:
        g=at.create_asset(gname,gpath,unreal.PCGGraph,unreal.PCGGraphFactory()); res["steps"].append("created")
    out_node=g.get_output_node()
    def add_chain(tag, cell, lower, smin, smax, meshlist, weights):
        gnode,gs=g.add_node_of_type(unreal.PCGCreatePointsGridSettings)
        try: gs.set_editor_property("coordinate_space", unreal.PCGCoordinateSpace.LOCAL)
        except Exception as e: res["steps"].append(tag+" cs:"+str(e)[:30])
        gs.set_editor_property("grid_extents", unreal.Vector(10000,12800,1))
        gs.set_editor_property("cell_size", unreal.Vector(cell,cell,1000))
        try: gs.set_editor_property("cull_points_outside_volume", False)
        except: pass
        prev=gnode
        try:
            nnode,ns=g.add_node_of_type(unreal.PCGAttributeNoiseSettings)
            g.add_edge(prev,"Out",nnode,"In"); prev=nnode
        except Exception as e: res["steps"].append(tag+" noise:"+str(e)[:30])
        try:
            fnode,fs=g.add_node_of_type(unreal.PCGDensityFilterSettings)
            try: fs.set_editor_property("lower_bound", lower)
            except: pass
            g.add_edge(prev,"Out",fnode,"In"); prev=fnode
        except Exception as e: res["steps"].append(tag+" filter:"+str(e)[:30])
        try:
            tnode,ts=g.add_node_of_type(unreal.PCGTransformPointsSettings)
            for prop,val in [("absolute_rotation",False),("rotation_min",unreal.Rotator(0,0,0)),("rotation_max",unreal.Rotator(0,0,360)),("uniform_scale",True),("scale_min",unreal.Vector(smin,smin,smin)),("scale_max",unreal.Vector(smax,smax,smax))]:
                try: ts.set_editor_property(prop,val)
                except: pass
            g.add_edge(prev,"Out",tnode,"In"); prev=tnode
        except Exception as e: res["steps"].append(tag+" transform:"+str(e)[:30])
        snode,ss=g.add_node_of_type(unreal.PCGStaticMeshSpawnerSettings)
        msp=ss.get_editor_property("mesh_selector_parameters")
        entries=[]
        for m,w in zip(meshlist,weights):
            e=unreal.PCGMeshSelectorWeightedEntry()
            d=e.get_editor_property("descriptor")
            d.set_editor_property("static_mesh", m)
            try: d.set_editor_property("cast_shadow", False)
            except: pass
            e.set_editor_property("descriptor", d)
            e.set_editor_property("weight", w)
            entries.append(e)
        msp.set_editor_property("mesh_entries", entries)
        g.add_edge(prev,"Out",snode,"In")
        g.add_edge(snode,"Out",out_node,"In")
        res["steps"].append(tag+" chain ok entries="+str(len(entries)))
    gc=meshes(["SM_Fern_01","SM_Fern_02","SM_Mossy_Grass_01","SM_Mossy_Grass_02","SM_ForestBush_01","SM_ForestBush_02","SM_ForestRock_01","SM_ForestRock_02"])
    res["gc"]=len(gc)
    add_chain("GC",250,0.34,0.5,1.5,gc,[3,3,3,3,2,2,1,1][:len(gc)])
    ft=meshes(["SM_ForestRock_01","SM_ForestRock_02","SM_ForestRock_03","SM_FallenLog_01","SM_FallenLog_02","SM_Stump_Old_01","SM_Stump_Cut_01"])
    res["ft"]=len(ft)
    add_chain("FT",520,0.44,0.8,2.7,ft,[4,4,3,2,2,1,1][:len(ft)])
    # capa de PENASCOS GRANDES (relieve rocoso accidentado)
    oc=meshes(["SM_ForestRock_01","SM_ForestRock_02","SM_ForestRock_03"])
    res["oc"]=len(oc)
    add_chain("OC",1500,0.5,2.5,4.3,oc,[1,1,1][:len(oc)])
    EAL.save_asset(full, False); res["steps"].append("saved")
    for a in eas.get_all_level_actors():
        if a.get_actor_label()=="PCG_RelieveVol": eas.destroy_actor(a)
    host=eas.spawn_actor_from_class(unreal.PCGVolume, unreal.Vector(0,4000,-5))
    host.set_actor_label("PCG_RelieveVol")
    comp=host.get_component_by_class(unreal.PCGComponent)
    try: comp.set_editor_property("generation_trigger", unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND)
    except Exception as e: res["steps"].append("trig:"+str(e)[:30])
    comp.set_graph(g)
    comp.generate(True)
    res["steps"].append("generate called")
    res["ok"]=True
except Exception as e:
    res["err"]=traceback.format_exc()
open(OUT,"w").write(json.dumps(res,indent=1,default=str))
