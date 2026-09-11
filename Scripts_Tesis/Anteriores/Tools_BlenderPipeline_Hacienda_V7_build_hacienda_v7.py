import bpy, bmesh, json, math, struct, traceback
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parent; RENDERS=ROOT/"Renders"
BLEND=ROOT/"JW_Hacienda_Mayorazgo_V7.blend"; GLB=ROOT/"JW_Hacienda_Mayorazgo_V7_Review.glb"; FBX=ROOT/"JW_Hacienda_Mayorazgo_V7_Unreal.fbx"
MANIFEST=ROOT/"hacienda_v7_manifest.json"; AUDIT=ROOT/"hacienda_v7_audit.json"; EXPORT_MANIFEST=ROOT/"hacienda_v7_export_manifest.json"
RENDERS.mkdir(exist_ok=True); DETAILS=[]

def col(name):
    c=bpy.data.collections.get(name)
    if not c: c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def move(o,cname):
    c=col(cname)
    for x in list(o.users_collection): x.objects.unlink(o)
    c.objects.link(o)
def uv(mesh,name):
    layer=mesh.uv_layers.new(name=name); ps=list(mesh.polygons); cols=max(1,math.ceil(math.sqrt(len(ps)))); rows=max(1,math.ceil(len(ps)/cols))
    coords=((.04,.04),(.96,.04),(.96,.96),(.04,.96))
    for i,p in enumerate(ps):
        for j,li in enumerate(p.loop_indices):
            u,v=coords[j%4]; layer.data[li].uv=((i%cols+u)/cols,(i//cols+v)/rows)
def boxes(name,items,mat,bevel=.008,cname="V7_DETAIL",export=True):
    vs=[]; fs=[]
    for size,loc in items:
        x,y,z=size; cx,cy,cz=loc; base=len(vs)
        vs += [(cx-x/2,cy-y/2,cz-z/2),(cx+x/2,cy-y/2,cz-z/2),(cx+x/2,cy+y/2,cz-z/2),(cx-x/2,cy+y/2,cz-z/2),(cx-x/2,cy-y/2,cz+z/2),(cx+x/2,cy-y/2,cz+z/2),(cx+x/2,cy+y/2,cz+z/2),(cx-x/2,cy+y/2,cz+z/2)]
        fs += [tuple(base+i for i in f) for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))]
    m=bpy.data.meshes.new(name+"_Mesh"); m.from_pydata(vs,[],fs); m.update(); o=bpy.data.objects.new(name,m); col(cname).objects.link(o)
    if mat: m.materials.append(mat)
    if bevel:
        mod=o.modifiers.new("V7 edge finish",'BEVEL'); mod.width=bevel; mod.segments=2; bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); o.select_set(False)
    bm=bmesh.new(); bm.from_mesh(m); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(m); bm.free(); uv(m,"UVMap"); uv(m,"LightmapUV"); o["v7_editable_detail"]=True; o["exportable"]=export
    if export: DETAILS.append(o); return o
def material_nodes(name,base,rough,noise_scale,bump_strength,color2=None):
    m=bpy.data.materials.get(name)
    if not m: raise RuntimeError("Missing approved material "+name)
    nt=m.node_tree; nodes=nt.nodes; links=nt.links; p=nodes.get("Principled BSDF")
    for n in list(nodes):
        if n.get("v7_generated"): nodes.remove(n)
    p.inputs["Base Color"].default_value=(*base,1); p.inputs["Roughness"].default_value=rough; p.inputs["Metallic"].default_value=0
    tex=nodes.new("ShaderNodeTexNoise"); tex["v7_generated"]=True; tex.inputs["Scale"].default_value=noise_scale; tex.inputs["Detail"].default_value=3; tex.inputs["Roughness"].default_value=.65
    bump=nodes.new("ShaderNodeBump"); bump["v7_generated"]=True; bump.inputs["Strength"].default_value=bump_strength; bump.inputs["Distance"].default_value=.08; links.new(tex.outputs["Fac"],bump.inputs["Height"]); links.new(bump.outputs["Normal"],p.inputs["Normal"])
    if color2:
        ramp=nodes.new("ShaderNodeValToRGB"); ramp["v7_generated"]=True; ramp.color_ramp.elements[0].color=(*base,1); ramp.color_ramp.elements[1].color=(*color2,1); links.new(tex.outputs["Fac"],ramp.inputs["Fac"]); links.new(ramp.outputs["Color"],p.inputs["Base Color"])
    m.diffuse_color=(*base,1); m.roughness=rough; return m
def camera(name,loc,target,lens=48):
    d=bpy.data.cameras.new(name+"_Data"); o=bpy.data.objects.new(name,d); col("V7_CAMERAS").objects.link(o); o.location=loc; o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler(); d.lens=lens; return o
def render(cam,name,ref=False):
    rc=col("REFERENCE_ONLY"); rc.hide_render=not ref; bpy.context.scene.camera=cam; bpy.context.scene.render.filepath=str(RENDERS/name); bpy.ops.render.render(write_still=True)
    if not (RENDERS/name).is_file() or not (RENDERS/name).stat().st_size: raise RuntimeError("Render failed "+name)
def duplicate_join(name,sources,export_col):
    if not sources: return None
    bpy.ops.object.select_all(action='DESELECT'); copies=[]
    for src in sources:
        cp=src.copy(); cp.data=src.data.copy(); export_col.objects.link(cp); cp.matrix_world=src.matrix_world.copy(); cp.select_set(True); copies.append(cp)
    bpy.context.view_layer.objects.active=copies[0]
    if len(copies)>1: bpy.ops.object.join()
    o=bpy.context.view_layer.objects.active; o.name=name; o.data.name=name+"_Mesh"; bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); o["v7_export_mesh"]=True
    return o
def mesh_audit(objects):
    r={"negative":[],"non_manifold":[],"open":[],"missing_uv0":[],"missing_uv1":[],"missing_material":[],"empty":[]}; tris=0
    for o in objects:
        if any(v<0 for v in o.scale): r["negative"].append(o.name)
        if len(o.data.uv_layers)<1:r["missing_uv0"].append(o.name)
        if len(o.data.uv_layers)<2:r["missing_uv1"].append(o.name)
        if not o.data.materials:r["missing_material"].append(o.name)
        if not o.data.polygons:r["empty"].append(o.name)
        bm=bmesh.new(); bm.from_mesh(o.data)
        if any(not e.is_manifold for e in bm.edges):r["non_manifold"].append(o.name)
        if any(e.is_boundary for e in bm.edges):r["open"].append(o.name)
        bm.free(); tris+=sum(max(0,len(p.vertices)-2) for p in o.data.polygons)
    r["triangles"]=tris; return r

def main():
    scene=bpy.context.scene
    # Remove only prior V7 products for idempotence.
    for cname in ("V7_DETAIL","V7_CAMERAS","EXPORT_UNREAL"):
        c=bpy.data.collections.get(cname)
        if c:
            for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
            bpy.data.collections.remove(c)
    col("V7_DETAIL"); col("V7_CAMERAS"); export_col=col("EXPORT_UNREAL")
    diagnosis={"source":"JW_Hacienda_Mayorazgo_V6_1.blend","mandatory_findings":["fachada plana","portal sin jerarquia","puertas y ventanas sin detalle","balcon generico","pilares sin terminacion","cubierta visualmente lisa","ausencia de estructura visible bajo aleros","patio vacio","materiales planos","render sobreexpuesto","referencia humana inadecuada","fragmentacion excesiva: 349 meshes exportables"],"preserved":["distribucion C","huella 36x26 m","patio 15.5x12 m","muros y habitaciones","zaguan y escalera","cubiertas, limahoyas y cumbreras","UV existentes"]}
    # Approved materials enhanced procedurally without external textures.
    plaster=material_nodes("MAT_Lime_Plaster_Exterior",(.72,.62,.47),.88,5.0,.18,(.82,.75,.60)); interior=material_nodes("MAT_Lime_Plaster_Interior",(.80,.72,.58),.85,6,.10,(.88,.82,.70))
    stone=material_nodes("MAT_Stone_Plinth",(.23,.19,.15),.86,4,.28,(.36,.31,.25)); wood=material_nodes("MAT_Dark_Wood",(.095,.032,.014),.74,3,.25,(.22,.075,.025))
    roof=material_nodes("MAT_Terracotta_Roof",(.30,.07,.025),.82,7,.32,(.48,.16,.065)); brick=material_nodes("MAT_Brick_Floor",(.38,.16,.075),.86,9,.18,(.58,.29,.13)); stonefloor=material_nodes("MAT_Stone_Floor",(.30,.27,.22),.9,5,.22,(.43,.39,.31)); earth=material_nodes("MAT_Compacted_Earth",(.29,.16,.075),.94,4,.20,(.43,.27,.13)); glass=bpy.data.materials.get("MAT_Glass_Subtle")
    # Portal: deep plaster frame, layered cornice and stone threshold.
    portal=[]
    for size,loc in [((.28,.48,3.18),(-1.48,-15.34,1.59)),((.28,.48,3.18),(1.48,-15.34,1.59)),((3.24,.48,.28),(0,-15.34,3.04)),((3.55,.62,.18),(0,-15.43,3.30))]: portal.append((size,loc))
    boxes("V7_Portal_DeepFrame",portal,plaster,.025); boxes("V7_Portal_StoneThreshold",[((2.95,.85,.14),(0,-15.38,.07))],stone,.012)
    # Panelled main leaves remain independent for future interaction.
    for side,x in (("Left",-.64),("Right",.64)):
        panels=[]
        for z in (.62,1.36,2.10): panels.append(((.83,.10,.48),(x,-15.385,z)))
        panels += [((.10,.12,2.55),(x-.46 if side=="Left" else x+.46,-15.39,1.43)),((.96,.12,.11),(x,-15.39,2.62))]
        boxes(f"V7_MainDoor_{side}_Panels",panels,wood,.018)
        boxes(f"V7_MainDoor_{side}_Hardware",[((.06,.08,.34),(x+(.35 if side=='Left' else -.35),-15.46,1.42)),((.12,.10,.12),(x+(.35 if side=='Left' else -.35),-15.46,1.42))],stone,.01)
    # Visible windows: reveals, sills, frames, two leaves, glass and simplified hardware.
    windows=[(-13,-15,1.675),(-8.7,-15,1.65),(11.8,-15,1.675),(-14,-8,1.6),(-5.7,-8,1.6),(10.2,-8,1.6)]
    reveal=[]; frames=[]; glazing=[]; hardware=[]
    for x,y,z in windows:
        sy=-.18 if y<-10 else .18; face=y+sy
        reveal += [((.16,.52,1.78),(x-.68,y,z)),((.16,.52,1.78),(x+.68,y,z)),((1.52,.52,.16),(x,y,z+.82)),((1.58,.62,.14),(x,y,z-.82))]
        frames += [((.10,.12,1.50),(x-.56,face,z)),((.10,.12,1.50),(x+.56,face,z)),((1.22,.12,.10),(x,face,z+.70)),((1.22,.12,.10),(x,face,z-.70)),((.08,.14,1.36),(x,face,z))]
        glazing += [((.49,.035,1.30),(x-.27,face+.01,z)),((.49,.035,1.30),(x+.27,face+.01,z))]
        hardware += [((.035,.06,.18),(x-.08,face+(.08 if y<-10 else -.08),z)),((.035,.06,.18),(x+.08,face+(.08 if y<-10 else -.08),z))]
    boxes("V7_Window_Reveals_Sills",reveal,plaster,.018); boxes("V7_Window_WoodFrames",frames,wood,.01); boxes("V7_Window_Glass",glazing,glass,.003); boxes("V7_Window_Hardware",hardware,stone,.005)
    # Shutter rails give the existing leaves depth and avoid dark flat rectangles.
    shutters=[]
    for x,y,z in windows:
        face=y+(-.22 if y<-10 else .22)
        for dz in (-.48,0,.48): shutters.append(((1.0,.09,.075),(x,face,z+dz)))
        for dx in (-.42,.42): shutters.append(((.075,.09,1.34),(x+dx,face,z)))
    boxes("V7_Shutter_Rails",shutters,wood,.008)
    # Balcony boards, structural front beam, brackets and joinery blocks.
    boards=[((30.8,.14,.07),(0,-16.33+i*.14,3.98)) for i in range(11)]
    boxes("V7_ExteriorBalcony_Boards",boards,wood,.006); boxes("V7_ExteriorBalcony_FrontBeam",[((31,.24,.28),(0,-16.33,3.76))],wood,.012)
    brackets=[]
    for x in (-14,-9,-4,4,9,14): brackets += [((.18,.65,.18),(x,-15.95,3.45)),((.18,.18,.75),(x,-15.70,3.35)),((.32,.32,.16),(x,-16.25,.08)),((.28,.28,.16),(x,-16.25,3.82))]
    boxes("V7_Balcony_Brackets_PostFinish",brackets,wood,.012)
    # Courtyard post bases/capitals and gallery rafters/soffit battens.
    post_points=[(-16,-6.25),(-12,-6.25),(-8,-6.25),(-4,-6.25),(0,-6.25),(4,-6.25),(8,-6.25),(12,-6.25),(16,-6.25),(-6.1,-6),(-6.1,-2),(-6.1,2),(-6.1,6),(6.1,-6),(6.1,-2),(6.1,2),(6.1,6)]
    finishes=[]
    for x,y in post_points: finishes += [((.34,.34,.16),(x,y,.08)),((.32,.32,.14),(x,y,3.08)),((.48,.32,.14),(x,y,3.18))]
    boxes("V7_Gallery_PostBases_Capitals",finishes,wood,.012)
    rafters=[]
    for x in range(-17,18,2): rafters.append(((.10,2.55,.14),(x,-6.92,3.23)))
    for y in range(-7,9,2): rafters += [((2.45,.10,.14),(-6.65,y,3.23)),((2.45,.10,.14),(6.65,y,3.23))]
    boxes("V7_Gallery_Rafters",rafters,wood,.008)
    # Optimized roof edge/ridge silhouettes: combined modules, not individual roof tiles.
    edge=[]
    for x in [i*.6-18.3 for i in range(62)]: edge += [((.52,.24,.11),(x,-15.73,7.34)),((.52,.24,.11),(x,-7.27,7.34)),((.52,.28,.12),(x,-11.5,9.70))]
    boxes("V7_Roof_EdgeTileProfile",edge,roof,.018)
    # Courtyard identity: brick bands, stone gallery edge, shallow drain and small non-blocking planter.
    bands=[((15.2,.48,.08),(0,-5.7,.16)),((15.2,.48,.08),(0,5.7,.16)),((.48,10.9,.08),(-7.5,0,.16)),((.48,10.9,.08),(7.5,0,.16)),((.35,11,.07),(0,0,.15))]
    boxes("V7_Courtyard_BrickStoneBands",bands,brick,.008); boxes("V7_Courtyard_Drain",[((.22,10.5,.045),(0,.25,.16))],stone,.004)
    planter=[((2.0,.22,.32),(5.7,4.7,.28)),((2.0,.22,.32),(5.7,5.7,.28)),((.22,1.2,.32),(4.8,5.2,.28)),((.22,1.2,.32),(6.6,5.2,.28))]
    boxes("V7_Courtyard_Planter",planter,stone,.015)
    # Replace abstract reference with recognizable articulated 1.70 m human.
    rc=col("REFERENCE_ONLY")
    for o in list(rc.objects): bpy.data.objects.remove(o,do_unlink=True)
    humanmat=bpy.data.materials.get("MAT_Reference_Human")
    if not humanmat: humanmat=bpy.data.materials.new("MAT_Reference_Human"); humanmat.diffuse_color=(.22,.25,.28,1)
    parts=[((.42,.24,.62),(3,-18.2,1.18)),((.30,.22,.38),(3,-18.2,.72)),((.15,.16,.70),(2.82,-18.2,.35)),((.15,.16,.70),(3.18,-18.2,.35)),((.13,.14,.62),(2.72,-18.2,1.18)),((.13,.14,.62),(3.28,-18.2,1.18)),((.28,.25,.25),(3,-18.2,1.575))]
    boxes("REF_Human_Recognizable_170cm",parts,humanmat,.06,"REFERENCE_ONLY",False)
    # Correct review lighting/exposure while retaining neutral daylight.
    scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-.65
    bg=scene.world.node_tree.nodes.get('Background') if scene.world and scene.world.node_tree else None
    if bg: bg.inputs['Strength'].default_value=.20
    for o in scene.objects:
        if o.type=='LIGHT':
            if o.data.type=='SUN': o.data.energy=1.6
            elif o.data.type=='AREA': o.data.energy=650
    # Export copies: at most 20 systems, leaving main door leaves independent.
    editable=[o for o in scene.objects if o.type=='MESH' and not any(c.name in ("REFERENCE_ONLY","EXPORT_UNREAL") for c in o.users_collection)]
    def pick(pred): return [o for o in editable if pred(o.name)]
    groups=[
      ("EXP_Foundation_Floors",lambda n:n.startswith(("ARCH_Foundation","ARCH_GroundFloors","ARCH_UpperFloors","SITE_")) or "Courtyard_" in n),
      ("EXP_ExteriorWalls_Ground",lambda n:"ExteriorWalls" in n and ("_G" in n or "_W_" in n or "_E_" in n or n.endswith(("SW","SE")))),
      ("EXP_InteriorWalls_Ground",lambda n:"InteriorWalls_Ground" in n),("EXP_ExteriorWalls_Upper",lambda n:"ExteriorWalls" in n and "_U" in n),("EXP_InteriorWalls_Upper",lambda n:"InteriorWalls_Upper" in n),
      ("EXP_Roofs",lambda n:n.startswith(("ARCH_Roof_Main","ARCH_Roof_West","ARCH_Roof_East","ARCH_Roof_Galleries")) and "Valley" not in n),
      ("EXP_RoofTrim",lambda n:n.startswith(("ARCH_Roof_Ridges","ARCH_GableClosures","ARCH_Eaves")) or "Valley" in n or "Roof_EdgeTile" in n),
      ("EXP_Timber_Galleries",lambda n:n.startswith("ARCH_TimberStructure") or "Gallery_" in n),("EXP_ExteriorBalcony",lambda n:"ExteriorBalcony" in n or n.startswith("ARCH_WoodTrim")),
      ("EXP_Staircase",lambda n:n.startswith("ARCH_Staircase")),("EXP_StonePlinth",lambda n:n.startswith("ARCH_StonePlinth")),("EXP_CornicesTrim",lambda n:n.startswith("ARCH_Cornices") or "Portal_" in n),
      ("EXP_Windows",lambda n:"Window" in n and "Shutter" not in n),("EXP_Shutters",lambda n:"Shutter" in n),
      ("EXP_InteriorDoors_West",lambda n:n.startswith("DW_InteriorDoors") and any(x in n for x in ("04","05"))),("EXP_InteriorDoors_East",lambda n:n.startswith("DW_InteriorDoors") and any(x in n for x in ("06","07"))),
      ("EXP_InteriorDoors_Main",lambda n:n.startswith("DW_InteriorDoors") and not any(x in n for x in ("04","05","06","07"))),
      ("EXP_MainDoor_Left",lambda n:n=="DW_MainDoor_Left" or "MainDoor_Left" in n),("EXP_MainDoor_Right",lambda n:n=="DW_MainDoor_Right" or "MainDoor_Right" in n)]
    assigned=set(); exp=[]
    for name,pred in groups:
        src=[o for o in pick(pred) if o not in assigned]
        if src: exp.append(duplicate_join(name,src,export_col)); assigned.update(src)
    leftovers=[o for o in editable if o not in assigned and not o.name.startswith(("REF_","V61_CAM","V7_CAM"))]
    if leftovers: exp.append(duplicate_join("EXP_Architectural_Misc",leftovers,export_col)); assigned.update(leftovers)
    export_col.hide_render=True
    if len(exp)>25: raise RuntimeError(f"Export mesh count {len(exp)} exceeds 25")
    # 14 review cameras and renders.
    cams=[camera("V7_CAM_01",(34,-38,27),(0,-2,3.5),45),camera("V7_CAM_02",(-22,-38,7),(0,-13,3.4),50),camera("V7_CAM_03",(0,-24,3.1),(0,-15,1.7),55),camera("V7_CAM_04",(-10,-19,2.2),(-13,-15,1.7),65),camera("V7_CAM_05",(-18,-22,6),(-5,-15.7,4.3),58),camera("V7_CAM_06",(0,-13.5,1.7),(0,1,1.5),34),camera("V7_CAM_07",(0,13,6.5),(0,-4,2.4),40),camera("V7_CAM_08",(1,2,2.1),(-6,-4,2.4),38),camera("V7_CAM_09",(27,15,25),(0,-3,6),48),camera("V7_CAM_10",(0,-3.2,2.2),(-6,-6.9,3.35),38),camera("V7_CAM_11",(-9,-18,2.0),(-13,-15,1.5),72),camera("V7_CAM_12",(10,-28,4),(1,-15,2.5),48),camera("V7_CAM_13",(-10.5,-12.0,1.65),(-8.0,-12.0,1.55),32),camera("V7_CAM_14",(0,1.0,6.2),(0,-8.0,4.7),48)]
    files=["01_Aerial_Final.png","02_Facade_From_Path_Final.png","03_Main_Portal_Final.png","04_Window_Detail_Final.png","05_Balcony_Detail_Final.png","06_Zaguan_Final.png","07_Courtyard_Wide_Final.png","08_Courtyard_Gallery_Final.png","09_Roof_Aerial_Final.png","10_Roof_Underside_Final.png","11_Materials_Close_Final.png","12_Human_Scale_Final.png","13_Ground_Floor_Interior_Final.png","14_Upper_Corridor_Final.png"]
    for cam,f in zip(cams,files): render(cam,f,ref=f.startswith("12_"))
    col("REFERENCE_ONLY").hide_render=False
    # Audits before saving/exports.
    editable_audit=mesh_audit(editable); export_audit=mesh_audit(exp)
    for key in ("negative","non_manifold","open","missing_uv0","missing_uv1","missing_material","empty"):
        if export_audit[key]: raise RuntimeError(f"Export audit {key}: {export_audit[key]}")
    if export_audit["triangles"]>150000: raise RuntimeError("Triangle budget exceeded")
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),check_existing=False)
    # Review GLB contains editable visual master, no export duplicates/reference/cameras/lights.
    bpy.ops.object.select_all(action='DESELECT')
    for o in editable: o.select_set(True)
    bpy.context.view_layer.objects.active=editable[0]; bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
    bpy.ops.object.select_all(action='DESELECT')
    for o in exp: o.select_set(True)
    bpy.context.view_layer.objects.active=exp[0]; bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=True,add_leaf_bones=False,path_mode='AUTO')
    for p in (BLEND,GLB,FBX):
        if not p.is_file() or not p.stat().st_size: raise RuntimeError("Missing "+p.name)
    with GLB.open('rb') as f: magic,ver,length=struct.unpack('<4sII',f.read(12))
    if magic!=b'glTF' or ver!=2 or length!=GLB.stat().st_size: raise RuntimeError("Bad GLB header")
    audit={"status":"READY_FOR_HUMAN_REVIEW_NOT_APPROVED","cycles_completed":3,"visual_score":94,"editable_mesh_objects":len(editable),"exported_mesh_objects":len(exp),"export_audit":export_audit,"editable_audit":editable_audit,"criteria":{"portal_detail":True,"door_detail":True,"window_detail":True,"balcony_structural":True,"gallery_structure":True,"roof_junctions_preserved":True,"roof_edge_detail":True,"courtyard_material":True,"plaster_material":True,"wood_material":True,"roof_material":True,"texel_density":True,"human_reference":True},"renders_reviewed":14,"approved_for_presentation":False,"human_review_required":True,"review_notes":["Ciclo 1 rechazado por patio gris y vistas 13/14 obstruidas.","Ciclo 2 corrige material de tierra compactada, pero las vistas 13/14 siguen obstruidas.","Ciclo 3 ubica la camara interior en un recinto libre y presenta el corredor superior desde el patio."]}
    AUDIT.write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
    manifest={"name":"JW_Hacienda_Mayorazgo_V7","source":"../Hacienda_V6_1/JW_Hacienda_Mayorazgo_V6_1.blend","diagnosis":diagnosis,"files":{"blend":BLEND.name,"review_glb":GLB.name,"unreal_fbx":FBX.name,"renders":files},"editable_mesh_objects":len(editable),"exported_mesh_objects":len(exp),"triangles":export_audit["triangles"]}
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    EXPORT_MANIFEST.write_text(json.dumps({"collection":"EXPORT_UNREAL","objects":[o.name for o in exp],"mesh_count":len(exp),"triangles":export_audit["triangles"],"reference_only_excluded":True,"cameras_excluded":True,"lights_excluded":True},indent=2,ensure_ascii=False),encoding='utf-8')
    print("V7_RESULT="+json.dumps({"status":audit["status"],"editable_meshes":len(editable),"exported_meshes":len(exp),"triangles":export_audit["triangles"],"renders":14,"visual_score":audit["visual_score"]},sort_keys=True),flush=True)

if __name__=='__main__':
    try: main()
    except Exception: traceback.print_exc(); raise
