import unreal, json, math, gc, os, traceback

PREFIX="HACV5_"
EXPECTED_LEVEL="/Game/JWN/MAP_JatunWasi_MCP_V03"
PROTECTED_LEVELS={"/Game/JWN/MAP_JatunWasi_MCP_V02","/Game/JWN/MAP_JatunWasi_MCP_V01","/Game/JWN/MAP_JatunWasi_AI_V02"}
ASSET_ROOT="/Game/JWN/Architecture/Hacienda_V5"
ROOT=os.path.join(unreal.Paths.project_dir(),"Tools","HaciendaV5")
MANIFEST_PATH=os.path.join(ROOT,"hacienda_v5_manifest.json")
REPORT_PATH=os.path.join(ROOT,"hacienda_v5_report.json")
LOG_PATH=os.path.join(ROOT,"hacienda_v5.log")
MANIFEST={"status":"RUNNING","assets":[],"actors":[],"materials":[],"v4_backup_actors":0}
REPORT={"status":"RUNNING","errors":[],"warnings":[],"stages":{}}

def log(s):
    unreal.log("HACV5: "+str(s))
    with open(LOG_PATH,"a",encoding="utf-8") as f:f.write(str(s)+"\n")
def flush():
    with open(MANIFEST_PATH,"w",encoding="utf-8") as f:json.dump(MANIFEST,f,indent=2)
    with open(REPORT_PATH,"w",encoding="utf-8") as f:json.dump(REPORT,f,indent=2)
def fail(s):
    REPORT["errors"].append(str(s)); REPORT["status"]="FAILED"; flush(); raise RuntimeError(s)
def validate():
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(); p=w.get_outermost().get_name()
    if p in PROTECTED_LEVELS or p!=EXPECTED_LEVEL: fail("Wrong/protected level: "+p)
    return w
def tf(x=0,y=0,z=0,pitch=0,yaw=0,roll=0):
    return unreal.Transform(location=unreal.Vector(x,y,z),rotation=unreal.Rotator(pitch=pitch,yaw=yaw,roll=roll),scale=unreal.Vector(1,1,1))
OPT=unreal.GeometryScriptPrimitiveOptions()
def box(m,x,y,z,sx,sy,sz,yaw=0,pitch=0,roll=0):
    r=unreal.GeometryScript_Primitives.append_box(m,OPT,tf(x,y,z,pitch,yaw,roll),float(sx),float(sy),float(sz),0,0,0,unreal.GeometryScriptPrimitiveOriginMode.CENTER,None)
    if r is None: fail("append_box failed")
def poly(m,pts,h,trans=None):
    p=[unreal.Vector2D(float(a),float(b)) for a,b in pts]
    r=unreal.GeometryScript_Primitives.append_simple_extrude_polygon(m,OPT,trans or tf(),p,float(h),0,True,unreal.GeometryScriptPrimitiveOriginMode.BASE,None)
    if r is None: fail("append polygon failed")
def wallx(m,y,a,b,z,h,t=45): box(m,(a+b)/2,y,z+h/2,abs(b-a),t,h)
def wally(m,x,a,b,z,h,t=45): box(m,x,(a+b)/2,z+h/2,t,abs(b-a),h)
def arch_ring(m,cx,cy,zbase,outer_r,inner_r,depth,along_x=True):
    pts=[]; n=32
    for i in range(n+1):
        a=math.pi-math.pi*i/n; pts.append((cx+outer_r*math.cos(a),zbase+outer_r*math.sin(a)))
    for i in range(n,-1,-1):
        a=math.pi-math.pi*i/n; pts.append((cx+inner_r*math.cos(a),zbase+inner_r*math.sin(a)))
    if along_x: poly(m,pts,depth,tf(0,cy-depth/2,0,pitch=90))
    else: poly(m,pts,depth,tf(cx-depth/2,0,0,pitch=90,yaw=90))
def col(m,x,y,z=0,h=360,r=22):
    pts=[(x+r*math.cos(2*math.pi*i/24),y+r*math.sin(2*math.pi*i/24)) for i in range(24)]
    poly(m,pts,h,tf(0,0,z)); box(m,x,y,z+9,70,70,18); box(m,x,y,z+h-12,78,78,24)

def foundation(m): box(m,0,0,-20,4000,3300,40)
def floors_g(m):
    box(m,0,-1245,2.5,4000,810,5); box(m,0,1245,2.5,4000,810,5); box(m,-1387.5,0,2.5,1225,1680,5); box(m,1387.5,0,2.5,1225,1680,5)
def floors_u(m):
    box(m,0,-1245,372.5,4000,810,25); box(m,-1900,0,372.5,200,1680,25); box(m,-937.5,0,372.5,325,1680,25); box(m,-1450,-445,372.5,700,790,25); box(m,-1450,670,372.5,700,340,25); box(m,1387.5,0,372.5,1225,1680,25)
def walls_g(m):
    for x in (-1015,1015): wally(m,x,-840,-170,0,360,30); wally(m,x,170,840,0,360,30)
    for y in (-840,840): wallx(m,y,-1015,-420,0,360,30); wallx(m,y,-300,300,0,360,30); wallx(m,y,420,1015,0,360,30)
    for x in (-1450,1450): wally(m,x,-1650,-620,0,360,22); wally(m,x,-500,500,0,360,22); wally(m,x,620,1650,0,360,22)
    for y in (-1250,1250): wallx(m,y,-2000,-1075,0,360,22); wallx(m,y,-955,955,0,360,22); wallx(m,y,1075,2000,0,360,22)
def walls_u(m):
    z=385; h=320
    for y in (-1650,1650): wallx(m,y,-2000,2000,z,h)
    for x in (-2000,2000): wally(m,x,-1650,1650,z,h)
    for y in (-840,840): wallx(m,y,-2000,-1075,z,h,30); wallx(m,y,-955,955,z,h,30); wallx(m,y,1075,2000,z,h,30)
    for x in (-1015,1015): wally(m,x,-840,-300,z,h,30); wally(m,x,-180,180,z,h,30); wally(m,x,300,840,z,h,30)
def stair(m):
    rise=385/22; going=29
    for i in range(11): box(m,-1650+i*going,350,(i+1)*rise/2,going,160,(i+1)*rise)
    box(m,-1302,225,192.5,120,410,25)
    for i in range(11): box(m,-1242-i*going,100,(192.5+(i+1)*rise)/2,going,160,192.5+(i+1)*rise)
    for x in (-1650,-1360,-1302,-1532): box(m,x,255,250,8,8,210)
    box(m,-1505,255,260,330,10,10,pitch=-30)
def ceilings(m):
    box(m,0,-1245,350,4000,810,14); box(m,0,1245,350,4000,810,14); box(m,-1450,0,350,1100,1680,14); box(m,1387.5,0,350,1225,1680,14)

def facade(m):
    x=2000; t=48; h=705
    # two floors with real portal/windows; solid piers, sills and lintels
    for a,b in [(-1650,-980),(-820,-160),(160,820),(980,1650)]: wally(m,x,a,b,0,360,t)
    for a,b in [(-980,-820),(820,980)]: wally(m,x,a,b,0,100,t); wally(m,x,a,b,245,115,t)
    wally(m,x,-160,160,290,70,t)
    for a,b in [(-1650,-1100),(-900,-250),(250,900),(1100,1650)]: wally(m,x,a,b,385,320,t)
    for a,b in [(-1100,-900),(900,1100)]: wally(m,x,a,b,385,95,t); wally(m,x,a,b,625,80,t)
    # side/rear shells retain real openings and thickness
    wally(m,-2000,-1650,1650,0,705,t)
    for y in (-1650,1650):
        for a,b in [(-2000,-950),(-750,350),(550,2000)]: wallx(m,y,a,b,0,705,t)
        for a,b in [(-950,-750),(350,550)]: wallx(m,y,a,b,0,95,t); wallx(m,y,a,b,240,465,t)
def portal(m):
    # Open, traversable portal with deep jambs and a smooth 24-part curved surround.
    box(m,2070,-220,175,110,75,350); box(m,2070,220,175,110,75,350)
    for i in range(25):
        a=math.pi*i/24.0
        y=190*math.cos(a); z=278+190*math.sin(a)
        box(m,2070,y,z,110,38,48,roll=math.degrees(a)-90)
    box(m,2090,0,480,95,560,32); box(m,2110,0,510,135,620,24)
def plinth(m):
    for y in (-1652,1652): wallx(m,y,-2000,2000,0,78,72)
    for x in (-2002,2002): wally(m,x,-1650,1650,0,78,72)
def trim(m):
    for y in (-1620,1620): box(m,0,y,710,4000,18,28)
    for x in (-1970,1970): box(m,x,0,710,18,3240,28)
    box(m,2040,0,365,48,3300,28)
def cornices(m):
    box(m,2060,0,350,90,3340,34); box(m,2070,0,690,110,3340,38)
    for y in (-1450,-700,700,1450): box(m,2055,y,525,70,90,320)
def balcony(m):
    box(m,2100,0,410,240,1550,30)
    for y in range(-720,721,90): box(m,2210,y,495,8,8,150)
    box(m,2210,0,570,12,1530,14)
    for y in (-650,-325,0,325,650): box(m,2070,y,335,150,14,140,pitch=-25)

def roof_main(m):
    # Four continuous colonial mono-pitch wings around the open patio.
    # Thick closed solids, 65 cm eaves and 27 degree visual pitch.
    box(m,0,-1160,765,4300,1120,38,roll=-27)
    box(m,0,1160,765,4300,1120,38,roll=27)
    box(m,-1590,0,765,1080,2200,38,pitch=27)
    box(m,1590,0,765,1080,2200,38,pitch=-27)
def roof_gallery(m):
    for y,r in ((-720,-18),(720,18)): box(m,0,y,665,2160,430,28,roll=r)
    for x,p in ((-895,18),(895,-18)): box(m,x,0,665,430,1320,28,pitch=p)
def roof_ridges(m):
    for y in (-1245,1245): box(m,0,y,865,4300,26,44)
    for x in (-1508,1508): box(m,x,0,865,26,1900,44)
def roof_gables(m):
    # Closed end fascia blocks; hipped silhouette does not expose triangular open ends.
    for x in (-2145,2145): box(m,x,0,720,38,3300,80)
def eaves(m):
    for y in (-1650,1650): box(m,0,y,690,4300,45,70)
    for x in (-2140,2140): box(m,x,0,690,45,3350,70)
    for y in (-945,945): box(m,0,y,645,2200,32,44)
    for x in (-1110,1110): box(m,x,0,645,32,1450,44)

def gallery(m):
    box(m,0,-720,10,2030,240,20); box(m,0,720,10,2030,240,20); box(m,-895,0,10,240,1200,20); box(m,895,0,10,240,1200,20)
def columns(m):
    for x in (-760,-380,0,380,760): col(m,x,-600); col(m,x,600)
    for y in (-400,0,400): col(m,-775,y); col(m,775,y)
def arches(m):
    for y in (-600,600):
        for x in (-570,-190,190,570): arch_ring(m,x,y,270,178,140,44,True)
    for x in (-775,775):
        for y in (-400,0,400):
            # side arcades represented by supported curved heads and continuous imposts
            box(m,x,y,330,55,340,45)
def upper_gallery(m):
    box(m,0,-720,390,2030,240,24); box(m,0,720,390,2030,240,24); box(m,-895,0,390,240,1200,24); box(m,895,0,390,240,1200,24)
def railings(m):
    for y in (-600,600):
        for x in range(-760,761,95): box(m,x,y,470,8,8,150)
        box(m,0,y,545,1560,12,14)
    for x in (-775,775):
        for y in range(-400,401,100): box(m,x,y,470,8,8,150)
        box(m,x,0,545,12,820,14)
def door(m,w=130,h=280):
    box(m,0,0,h/2,8,w,h)
    for z in (h*.25,h*.5,h*.75): box(m,-6,0,z,5,w-16,7)
def window(m,w=180,h=145):
    for y in (-w/2,w/2): box(m,0,y,h/2,12,12,h)
    for z in (0,h): box(m,0,0,z,12,w,12)
    box(m,0,0,h/2,12,9,h); box(m,0,0,h/2,12,w,9)

BUILD={
"SM_HACV5_Foundation":foundation,"SM_HACV5_InteriorWalls_Ground":walls_g,"SM_HACV5_InteriorWalls_Upper":walls_u,"SM_HACV5_GroundFloors":floors_g,"SM_HACV5_UpperFloors":floors_u,"SM_HACV5_Staircase":stair,"SM_HACV5_Ceilings":ceilings,
"SM_HACV5_ExteriorFacade":facade,"SM_HACV5_StonePlinth":plinth,"SM_HACV5_MainPortal":portal,"SM_HACV5_WoodTrim":trim,"SM_HACV5_ExteriorBalcony":balcony,"SM_HACV5_Cornices":cornices,
"SM_HACV5_Roof_Main":roof_main,"SM_HACV5_Roof_Galleries":roof_gallery,"SM_HACV5_Roof_Ridges":roof_ridges,"SM_HACV5_Roof_GableClosures":roof_gables,"SM_HACV5_EavesAndFascia":eaves,
"SM_HACV5_CourtyardGallery":gallery,"SM_HACV5_ColonialArches":arches,"SM_HACV5_Columns":columns,"SM_HACV5_UpperGallery":upper_gallery,"SM_HACV5_Railings":railings,
"SM_HACV5_MainDoor_Left":lambda m:door(m,130,280),"SM_HACV5_MainDoor_Right":lambda m:door(m,130,280),"SM_HACV5_InteriorDoor_A":lambda m:door(m,120,250),"SM_HACV5_InteriorDoor_B":lambda m:door(m,120,250),"SM_HACV5_Window_A":lambda m:window(m,170,145),"SM_HACV5_Window_B":lambda m:window(m,200,145)}

def make_asset(name,builder):
    mesh=unreal.DynamicMesh(); builder(mesh)
    unreal.GeometryScript_UVs.set_num_uv_sets(mesh,2,None)
    for uv in (0,1):
        try: unreal.GeometryScript_UVs.auto_generate_patch_builder_mesh_u_vs(mesh,uv,unreal.GeometryScriptPatchBuilderOptions(),None)
        except Exception as e: REPORT["warnings"].append(name+" UV"+str(uv)+": "+repr(e))
    unreal.GeometryScript_Normals.recompute_normals(mesh,unreal.GeometryScriptCalculateNormalsOptions(),False,None)
    path=ASSET_ROOT+"/"+name; existed=unreal.EditorAssetLibrary.does_asset_exist(path)
    if existed: sm=unreal.load_asset(path)
    else:
        opt=unreal.GeometryScriptCreateNewStaticMeshAssetOptions(); sm,out=unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(mesh,path,opt,None)
        if sm is None or "SUCCESS" not in str(out).upper(): fail("create asset "+name+" "+str(out))
        MANIFEST["assets"].append(path)
    if existed:
        _,out=unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(mesh,sm,unreal.GeometryScriptCopyMeshToAssetOptions(),unreal.GeometryScriptMeshWriteLOD(),True,None)
        if "SUCCESS" not in str(out).upper(): fail("update asset "+name)
    try: unreal.GeometryScript_Collision.set_static_mesh_collision_from_mesh(mesh,sm,unreal.GeometryScriptCollisionFromMeshOptions(),unreal.GeometryScriptSetStaticMeshCollisionOptions(),None)
    except Exception as e: REPORT["warnings"].append(name+" collision: "+repr(e))
    unreal.EditorAssetLibrary.save_loaded_asset(sm,False); del mesh; gc.collect(); return sm

def materials():
    specs={
    "MI_HACV5_Plaster_Exterior":"/Game/Megascans/Surfaces/Flaked_Paint_Wall_vhqgdhh/MI_Flaked_Paint_Wall_vhqgdhh_2K",
    "MI_HACV5_Plaster_Interior":"/Game/Megascans/Surfaces/Flaked_Paint_Wall_vhqgdhh/MI_Flaked_Paint_Wall_vhqgdhh_2K",
    "MI_HACV5_Stone":"/Game/Megascans/3D_Assets/Modular_Stone_Wall_xgfnfebiy/MI_Modular_Stone_Wall_xgfnfebiy_2K",
    "MI_HACV5_Wood":"/Game/Megascans/Surfaces/Wooden_Planks_ueynbafew/MI_Wooden_Planks_ueynbafew_2K",
    "MI_HACV5_Roof":"/Game/Megascans/Surfaces/Brick_Facade_vizcegj/MI_Brick_Facade_vizcegj_2K",
    "MI_HACV5_Floor_Tile":"/Game/Megascans/Surfaces/Patterned_Marble_Tiles_vf5leaav/MI_Patterned_Marble_Tiles_vf5leaav_2K",
    "MI_HACV5_Floor_Wood":"/Game/Megascans/Surfaces/Wooden_Planks_ueynbafew/MI_Wooden_Planks_ueynbafew_2K"}
    out={}; tools=unreal.AssetToolsHelpers.get_asset_tools()
    for n,parent in specs.items():
        path=ASSET_ROOT+"/Materials/"+n; mi=unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else tools.create_asset(n,ASSET_ROOT+"/Materials",unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
        if mi is None: fail("material "+n)
        unreal.MaterialEditingLibrary.set_material_instance_parent(mi,unreal.load_asset(parent)); unreal.EditorAssetLibrary.save_loaded_asset(mi,False)
        MANIFEST["materials"].append(path); out[n]=mi
    return out
def mat_for(n,M):
    if "Roof" in n or "Eaves" in n:return M["MI_HACV5_Roof"]
    if "Plinth" in n or "Foundation" in n or "Staircase" in n:return M["MI_HACV5_Stone"]
    if any(k in n for k in ("Trim","Balcony","Railing","Door","Window")):return M["MI_HACV5_Wood"]
    if "Floor" in n or "Gallery" in n:return M["MI_HACV5_Floor_Tile"]
    if "Interior" in n or "Ceiling" in n:return M["MI_HACV5_Plaster_Interior"]
    return M["MI_HACV5_Plaster_Exterior"]
def l2w(p,yaw=12.09475708,o=(-7000,-2500,5)):
    c=math.cos(math.radians(yaw));s=math.sin(math.radians(yaw));return(o[0]+p[0]*c-p[1]*s,o[1]+p[0]*s+p[1]*c,o[2]+p[2])
def spawn(label,obj,local,lyaw,folder,mat=None):
    pos=l2w(local); yaw=12.09475708+lyaw
    old=next((a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()==label),None)
    a=old or unreal.EditorLevelLibrary.spawn_actor_from_object(obj,unreal.Vector(*pos),unreal.Rotator(pitch=0,yaw=yaw,roll=0),transient=False)
    if a is None: fail("spawn "+label)
    a.set_actor_label(label);a.set_actor_location(unreal.Vector(*pos),False,False);a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=yaw,roll=0),False);a.set_actor_scale3d(unreal.Vector(1,1,1));a.set_folder_path(folder);a.set_actor_hidden_in_game(False);a.set_is_temporarily_hidden_in_editor(False)
    if hasattr(a,"static_mesh_component"):
        a.static_mesh_component.set_visibility(True);a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
        if mat:a.static_mesh_component.set_material(0,mat)
    if not old:MANIFEST["actors"].append(label)
    return a
def backup_v4():
    n=0
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label().startswith("HACV4_"):
            a.set_folder_path("JatunWasi/Hacienda_V4_Backup");a.set_actor_hidden_in_game(True);a.set_is_temporarily_hidden_in_editor(True)
            for c in a.get_components_by_class(unreal.PrimitiveComponent): c.set_visibility(False);c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            n+=1
    MANIFEST["v4_backup_actors"]=n
def add_props():
    P={"table":"/Game/Megascans/3D_Assets/Wooden_Table_veigfjmaw/S_Wooden_Table_veigfjmaw_lod3_Var1","chair":"/Game/Megascans/3D_Assets/Wooden_Chair_wjglai2s/S_Wooden_Chair_wjglai2s_lod3_Var1","shelf":"/Game/Megascans/3D_Assets/Wooden_Bookshelf_vmjhbix/S_Wooden_Bookshelf_vmjhbix_lod3","book":"/Game/Megascans/3D_Assets/Old_Book_wldocam/S_Old_Book_wldocam_lod3_Var1","bench":"/Game/Megascans/3D_Assets/Wooden_Bench_wjfjahl/S_Wooden_Bench_wjfjahl_lod3","case":"/Game/Megascans/3D_Assets/Leather_Luggage_Suitcase_wk2iafu/S_Leather_Luggage_Suitcase_wk2iafu_lod3","lantern":"/Game/Megascans/3D_Assets/Traditional_Lantern_xccpecydw/S_Traditional_Lantern_xccpecydw_lod3"}
    items=[]
    for i,(x,y,r) in enumerate([(-1580,-1300,90),(-1580,-1100,90),(-1580,-900,90)]):items.append((f"Archive_Shelf_{i+1:02}","shelf",(x,y,5),r))
    items += [("Archive_Table","table",(-1320,-1080,5),0),("Archive_Chair_A","chair",(-1160,-1080,5),180),("Archive_Chair_B","chair",(-1320,-1260,5),90),("Archive_Book_A","book",(-1320,-1080,85),10),("Archive_Book_B","book",(-1280,-1080,85),-8)]
    items.append(("Dining_Table","table",(1350,-1100,5),0))
    chairs=[(1120,-1100,0),(1580,-1100,180),(1200,-1320,90),(1350,-1320,90),(1500,-1320,90),(1200,-880,-90),(1350,-880,-90),(1500,-880,-90)]
    for i,(x,y,r) in enumerate(chairs):items.append((f"Dining_Chair_{i+1:02}","chair",(x,y,5),r))
    items += [("Salon_Bench_A","bench",(1450,1120,5),180),("Salon_Bench_B","bench",(1120,1120,5),170),("Salon_Table","table",(1300,1320,5),0),("Salon_Chair_A","chair",(1080,1350,5),25),("Salon_Chair_B","chair",(1520,1350,5),-25),("History_Bench_A","bench",(-1450,1120,5),0),("History_Bench_B","bench",(-1200,1350,5),-45),("History_Case_A","case",(-1200,1180,5),12),("History_Case_B","case",(-1120,1220,5),-18),("History_Book","book",(-1320,1300,85),15),("Kitchen_Table","table",(1500,300,5),90),("Kitchen_Bench","bench",(1650,300,5),90),("Kitchen_Shelf","shelf",(1850,300,5),90),("Upper_Bench","bench",(-200,1200,390),180),("Upper_Chair","chair",(300,1200,390),160)]
    for n,k,p,r in items: spawn(PREFIX+n,unreal.load_asset(P[k]),p,r,"JatunWasi/Hacienda_V5/Interiors")
    locs=[(-1400,-1100,280),(1350,-1100,280),(-1400,1120,280),(1500,300,280),(0,-720,650),(0,720,650)]
    for i,p in enumerate(locs,1):
        spawn(PREFIX+f"Lantern_{i:02}",unreal.load_asset(P["lantern"]),p,0,"JatunWasi/Hacienda_V5/Lighting")
        label=PREFIX+f"Light_{i:02}"; old=next((a for a in unreal.EditorLevelLibrary.get_all_level_actors() if a.get_actor_label()==label),None);wp=l2w((p[0],p[1],p[2]-25))
        l=old or unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PointLight,unreal.Vector(*wp),unreal.Rotator(),transient=False);l.set_actor_label(label);l.set_folder_path("JatunWasi/Hacienda_V5/Lighting");l.set_actor_hidden_in_game(False);l.set_is_temporarily_hidden_in_editor(False)
        c=l.point_light_component;c.set_editor_property("intensity",55.0);c.set_editor_property("attenuation_radius",230.0);c.set_editor_property("cast_shadows",False);c.set_editor_property("use_temperature",True);c.set_editor_property("temperature",3900.0)
        if not old:MANIFEST["actors"].append(label)
def run():
    validate();log("START "+EXPECTED_LEVEL);backup_v4();M=materials();assets={}
    for n,b in BUILD.items(): assets[n]=make_asset(n,b);flush()
    for n,obj in assets.items():
        if any(k in n for k in ("Door","Window")):continue
        spawn(PREFIX+n.replace("SM_HACV5_",""),obj,(0,0,0),0,"JatunWasi/Hacienda_V5/Architecture",mat_for(n,M))
    placements=[("MainDoor_Left","SM_HACV5_MainDoor_Left",(2004,-65,0),90),("MainDoor_Right","SM_HACV5_MainDoor_Right",(2004,65,0),-90),("InteriorDoor_A","SM_HACV5_InteriorDoor_A",(1018,-220,0),90),("InteriorDoor_B","SM_HACV5_InteriorDoor_B",(-1018,220,0),-90),("Window_Front_A","SM_HACV5_Window_A",(2004,-900,100),0),("Window_Front_B","SM_HACV5_Window_A",(2004,900,100),0),("Window_Side_A","SM_HACV5_Window_B",(-850,-1654,95),0),("Window_Side_B","SM_HACV5_Window_B",(450,1654,95),0)]
    for label,n,p,r in placements:spawn(PREFIX+label,assets[n],p,r,"JatunWasi/Hacienda_V5/Openings",M["MI_HACV5_Wood"])
    add_props();REPORT["stages"]={"backup":True,"assets":True,"architecture":True,"interiors":True,"lighting":True};REPORT["status"]="BUILT_UNSAVED_LEVEL";MANIFEST["status"]="BUILT";flush();log("BUILD_COMPLETE assets=%d actors=%d"%(len(MANIFEST["assets"]),len(MANIFEST["actors"])))
try:run()
except Exception:
    REPORT["errors"].append(traceback.format_exc());REPORT["status"]="FAILED";flush();raise
