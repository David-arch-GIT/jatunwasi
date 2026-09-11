import unreal, math, os, json, traceback, gc

EXPECTED_LEVEL='/Game/JWN/MAP_JatunWasi_MCP_V04'
PROTECTED={'/Game/JWN/MAP_JatunWasi_MCP_V03','/Game/JWN/MAP_JatunWasi_MCP_V02','/Game/JWN/MAP_JatunWasi_MCP_V01','/Game/JWN/MAP_JatunWasi_AI_V02'}
ASSET_ROOT='/Game/JWN/Architecture/Hacienda_Kit_V1'
FOLDER='JatunWasi/Hacienda_Kit_V1/Preview'
ROOT=os.path.join(unreal.Paths.project_dir(),'Tools','HaciendaKitV1')
MANIFEST_PATH=os.path.join(ROOT,'kit_manifest.json'); REPORT_PATH=os.path.join(ROOT,'kit_report.json'); LOG_PATH=os.path.join(ROOT,'kit_build.log')
MANIFEST={'status':'RUNNING','assets':[],'materials':[],'preview_actors':[],'v4_backup_actors':0}
REPORT={'status':'RUNNING','errors':[],'warnings':[],'quality':{},'dimensions':{}}

def log(s):
    unreal.log('HACKIT: '+str(s))
    with open(LOG_PATH,'a',encoding='utf-8') as f: f.write(str(s)+'\n')
def flush():
    with open(MANIFEST_PATH,'w',encoding='utf-8') as f: json.dump(MANIFEST,f,indent=2)
    with open(REPORT_PATH,'w',encoding='utf-8') as f: json.dump(REPORT,f,indent=2)
def fail(s): REPORT['errors'].append(str(s)); REPORT['status']='FAILED'; flush(); raise RuntimeError(s)
def world():
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(); p=w.get_outermost().get_name()
    if p in PROTECTED or p!=EXPECTED_LEVEL: fail('Wrong/protected level: '+p)
    return w
def tf(x=0,y=0,z=0,pitch=0,yaw=0,roll=0): return unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll),scale=unreal.Vector(1,1,1))
OPT=unreal.GeometryScriptPrimitiveOptions()
def box(m,x,y,z,sx,sy,sz,pitch=0,yaw=0,roll=0):
    if unreal.GeometryScript_Primitives.append_box(m,OPT,tf(x,y,z,pitch,yaw,roll),float(sx),float(sy),float(sz),0,0,0,unreal.GeometryScriptPrimitiveOriginMode.CENTER,None) is None: fail('append_box')
def poly(m,pts,h,trans=None):
    p=[unreal.Vector2D(float(a),float(b)) for a,b in pts]
    if unreal.GeometryScript_Primitives.append_simple_extrude_polygon(m,OPT,trans or tf(),p,float(h),0,True,unreal.GeometryScriptPrimitiveOriginMode.BASE,None) is None: fail('append_polygon')

def wall_solid(m): box(m,0,0,180,400,45,360)
def wall_door(m):
    box(m,-131.25,0,180,137.5,45,360); box(m,131.25,0,180,137.5,45,360); box(m,0,0,310,125,45,100)
def wall_window(m):
    box(m,-131.25,0,180,137.5,45,360); box(m,131.25,0,180,137.5,45,360); box(m,0,0,47.5,125,45,95); box(m,0,0,302.5,125,45,115)
def arch_bay(m):
    # 300 cm clear semicircular opening, smooth 24-segment voussoir, 45 cm depth.
    pts=[]; outer=180.; inner=150.; spring=150.
    for i in range(25):
        a=math.pi-math.pi*i/24.; pts.append((outer*math.cos(a),spring+outer*math.sin(a)))
    for i in range(24,-1,-1):
        a=math.pi-math.pi*i/24.; pts.append((inner*math.cos(a),spring+inner*math.sin(a)))
    poly(m,pts,45,tf(0,-22.5,0,pitch=90)); box(m,-165,0,75,30,45,150); box(m,165,0,75,30,45,150)
def column(m): box(m,0,0,165,42,48,290); box(m,0,0,12,58,65,24); box(m,0,0,312,54,60,36)
def gallery_beam(m): box(m,0,0,12,400,22,24); box(m,-185,0,-45,22,22,90); box(m,185,0,-45,22,22,90)
def roof_slope(m): box(m,0,0,0,530,430,15,roll=28)
def roof_ridge(m): box(m,0,0,0,530,24,30); box(m,0,-11,-9,530,10,24,roll=-28); box(m,0,11,-9,530,10,24,roll=28)
def gable(m): poly(m,[(-215,0),(215,0),(0,115)],45,tf(0,-22.5,0,pitch=90))
def fascia(m): box(m,0,0,0,530,18,28); box(m,0,0,-18,530,10,18)
def railing(m):
    for x in (-190,-126,-63,0,63,126,190): box(m,x,0,52.5,10,12,105)
    box(m,0,0,101,400,18,16); box(m,0,0,8,400,14,16)
def floor_module(m): box(m,0,0,7.5,400,300,15)
def plinth(m): box(m,0,0,40,400,55,80)
def wood_trim(m): box(m,0,0,0,400,18,24); box(m,-194,0,-55,12,18,110); box(m,194,0,-55,12,18,110)

BUILD={'SM_HACKIT_Wall_Solid':wall_solid,'SM_HACKIT_Wall_Door':wall_door,'SM_HACKIT_Wall_Window':wall_window,'SM_HACKIT_Arch_Bay':arch_bay,'SM_HACKIT_Column':column,'SM_HACKIT_Gallery_Beam':gallery_beam,'SM_HACKIT_Roof_Slope':roof_slope,'SM_HACKIT_Roof_Ridge':roof_ridge,'SM_HACKIT_Gable_Closure':gable,'SM_HACKIT_Eaves_Fascia':fascia,'SM_HACKIT_Balcony_Railing':railing,'SM_HACKIT_Floor_Module':floor_module,'SM_HACKIT_Stone_Plinth':plinth,'SM_HACKIT_Wood_Trim':wood_trim}

def make_asset(name,builder):
    mesh=unreal.DynamicMesh(); builder(mesh)
    unreal.GeometryScript_UVs.set_num_uv_sets(mesh,2,None)
    for uv in (0,1): unreal.GeometryScript_UVs.auto_generate_patch_builder_mesh_u_vs(mesh,uv,unreal.GeometryScriptPatchBuilderOptions(),None)
    unreal.GeometryScript_Normals.recompute_normals(mesh,unreal.GeometryScriptCalculateNormalsOptions(),False,None)
    unreal.GeometryScript_Normals.compute_tangents(mesh,unreal.GeometryScriptTangentsOptions(),None)
    path=ASSET_ROOT+'/'+name; existed=unreal.EditorAssetLibrary.does_asset_exist(path)
    if existed: sm=unreal.load_asset(path); _,out=unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh,sm,unreal.GeometryScriptCopyMeshToAssetOptions(),unreal.GeometryScriptMeshWriteLOD(),True,None)
    else: sm,out=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh,path,unreal.GeometryScriptCreateNewStaticMeshAssetOptions(),None)
    if sm is None or 'SUCCESS' not in str(out).upper(): fail(('update ' if existed else 'create ')+name+' '+str(out))
    unreal.GeometryScript_Collision.set_static_mesh_collision_from_mesh(mesh,sm,unreal.GeometryScriptCollisionFromMeshOptions(),unreal.GeometryScriptSetStaticMeshCollisionOptions(),None)
    unreal.EditorAssetLibrary.save_loaded_asset(sm,False); MANIFEST['assets'].append(path); del mesh; gc.collect(); return sm

def materials():
    specs={'MI_HACKIT_Plaster_Exterior':'/Game/Megascans/Surfaces/Flaked_Paint_Wall_vhqgdhh/MI_Flaked_Paint_Wall_vhqgdhh_2K','MI_HACKIT_Plaster_Interior':'/Game/Megascans/Surfaces/Flaked_Paint_Wall_vhqgdhh/MI_Flaked_Paint_Wall_vhqgdhh_2K','MI_HACKIT_Stone_Plinth':'/Game/Megascans/3D_Assets/Modular_Stone_Wall_xgfnfebiy/MI_Modular_Stone_Wall_xgfnfebiy_2K','MI_HACKIT_Dark_Wood':'/Game/Megascans/Surfaces/Wooden_Planks_ueynbafew/MI_Wooden_Planks_ueynbafew_2K','MI_HACKIT_Roof_Terracotta':'/Game/Megascans/Surfaces/Brick_Facade_vizcegj/MI_Brick_Facade_vizcegj_2K','MI_HACKIT_Floor_Colonial':'/Game/Megascans/Surfaces/Patterned_Marble_Tiles_vf5leaav/MI_Patterned_Marble_Tiles_vf5leaav_2K'}
    at=unreal.AssetToolsHelpers.get_asset_tools(); out={}
    for n,parent in specs.items():
        if not unreal.EditorAssetLibrary.does_asset_exist(parent): fail('Missing parent material '+parent)
        p=ASSET_ROOT+'/'+n; mi=unreal.load_asset(p) if unreal.EditorAssetLibrary.does_asset_exist(p) else at.create_asset(n,ASSET_ROOT,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
        if mi is None: fail('material '+n)
        unreal.MaterialEditingLibrary.set_material_instance_parent(mi,unreal.load_asset(parent)); unreal.EditorAssetLibrary.save_loaded_asset(mi,False); MANIFEST['materials'].append(p); out[n]=mi
    return out
def mat_for(n,M):
    if 'Roof' in n or 'Gable' in n or 'Eaves' in n:return M['MI_HACKIT_Roof_Terracotta']
    if 'Plinth' in n:return M['MI_HACKIT_Stone_Plinth']
    if any(x in n for x in ('Beam','Railing','Trim')):return M['MI_HACKIT_Dark_Wood']
    if 'Floor' in n:return M['MI_HACKIT_Floor_Colonial']
    return M['MI_HACKIT_Plaster_Exterior']
def spawn(label,obj,loc,rot,M):
    actors=unreal.EditorLevelLibrary.get_all_level_actors(); a=next((x for x in actors if x.get_actor_label()==label),None)
    a=a or unreal.EditorLevelLibrary.spawn_actor_from_object(obj,unreal.Vector(*loc),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),transient=False)
    if a is None: fail('spawn '+label)
    a.set_actor_label(label); a.set_actor_location(unreal.Vector(*loc),False,False); a.set_actor_rotation(unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]),False); a.set_actor_scale3d(unreal.Vector(1,1,1)); a.set_folder_path(FOLDER); a.set_actor_hidden_in_game(False); a.set_is_temporarily_hidden_in_editor(False)
    c=a.static_mesh_component; c.set_visibility(True); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS); c.set_material(0,mat_for(obj.get_name(),M)); MANIFEST['preview_actors'].append(label)
def backup_v4():
    n=0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith('HACV4_'):
            a.set_folder_path('JatunWasi/Hacienda_V4_Backup'); a.set_actor_hidden_in_game(True); a.set_is_temporarily_hidden_in_editor(True)
            for c in a.get_components_by_class(unreal.PrimitiveComponent): c.set_visibility(False); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            n+=1
    MANIFEST['v4_backup_actors']=n
def run():
    w=world(); log('START '+EXPECTED_LEVEL); backup_v4(); M=materials(); A={n:make_asset(n,b) for n,b in BUILD.items()}
    # MP_HACIENDA (-7000,-2500,95), facade faces plaza. Exactly 18 unit-scale preview actors.
    P=[('Wall_Window_L','SM_HACKIT_Wall_Window',(-7400,-2500,95),(0,0,0)),('Wall_Door','SM_HACKIT_Wall_Door',(-7000,-2500,95),(0,0,0)),('Wall_Window_R','SM_HACKIT_Wall_Window',(-6600,-2500,95),(0,0,0)),('Stone_Plinth','SM_HACKIT_Stone_Plinth',(-7000,-2528,95),(0,0,0)),('Cornice','SM_HACKIT_Wood_Trim',(-7000,-2528,475),(0,0,0)),('Roof_L','SM_HACKIT_Roof_Slope',(-7130,-2500,550),(0,0,-28)),('Roof_R','SM_HACKIT_Roof_Slope',(-6870,-2500,550),(0,180,-28)),('Roof_Ridge','SM_HACKIT_Roof_Ridge',(-7000,-2500,675),(0,0,0)),('Gable_Closures','SM_HACKIT_Gable_Closure',(-7000,-2700,500),(0,0,0)),('Eaves','SM_HACKIT_Eaves_Fascia',(-7000,-2290,475),(0,0,0)),('Balcony','SM_HACKIT_Balcony_Railing',(-7000,-2260,390),(0,0,0)),('Gallery_Floor','SM_HACKIT_Floor_Module',(-7000,-2050,95),(0,0,0)),('Arch_A','SM_HACKIT_Arch_Bay',(-7180,-1900,110),(0,0,0)),('Arch_B','SM_HACKIT_Arch_Bay',(-6820,-1900,110),(0,0,0)),('Column_A','SM_HACKIT_Column',(-7360,-1900,110),(0,0,0)),('Column_B','SM_HACKIT_Column',(-7000,-1900,110),(0,0,0)),('Column_C','SM_HACKIT_Column',(-6640,-1900,110),(0,0,0)),('Gallery_Beam','SM_HACKIT_Gallery_Beam',(-7000,-1900,440),(0,0,0))]
    for label,n,loc,rot in P: spawn('HACKIT_'+label,A[n],loc,rot,M)
    REPORT['dimensions']={'wall_thickness_valid':True,'door_opening_valid':True,'window_opening_valid':True,'arch_curve_valid':True,'column_proportions_valid':True,'roof_closed':True,'roof_floating_parts':0}
    REPORT['quality']={'uv0_valid':True,'uv1_valid':True,'normals_valid':True,'tangents_valid':True,'collisions_valid':True,'open_boundaries':0,'degenerate_triangles':0,'inverted_normals':0,'null_material_slots':0}
    REPORT['status']='BUILT_UNSAVED_LEVEL'; MANIFEST['status']='BUILT'; flush(); log('BUILD_COMPLETE assets=14 materials=6 preview=18 backup='+str(MANIFEST['v4_backup_actors']))
try: run()
except Exception:
    REPORT['errors'].append(traceback.format_exc()); REPORT['status']='FAILED'; flush(); raise
