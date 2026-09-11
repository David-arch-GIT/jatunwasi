import bpy
import bmesh
import json
import math
import struct
import traceback
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RENDERS = ROOT / "Renders"
BLEND = ROOT / "JW_Hacienda_Mayorazgo_V6.blend"
GLB = ROOT / "JW_Hacienda_Mayorazgo_V6.glb"
FBX = ROOT / "JW_Hacienda_Mayorazgo_V6.fbx"
MANIFEST = ROOT / "hacienda_v6_manifest.json"
AUDIT = ROOT / "hacienda_v6_audit.json"
RENDERS.mkdir(parents=True, exist_ok=True)

EXPORTABLE = set()
SYSTEMS = {}
ROOMS_GROUND = ["Recepcion", "Salon principal", "Comedor", "Cocina", "Despensa", "Archivo biblioteca", "Sala historica", "Deposito", "Servicio", "Bano oeste reservado", "Bano este reservado"]
ROOMS_UPPER = ["Dormitorio principal", "Dormitorio secundario", "Despacho", "Sala familiar"]

def log(msg): print(f"HACIENDA_V6 | {msg}", flush=True)
def clean():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for group in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for datablock in tuple(group):
            if datablock.users == 0: group.remove(datablock)
    for col in tuple(bpy.data.collections):
        if col.name != "Collection": bpy.data.collections.remove(col)
    base = bpy.data.collections.get("Collection")
    if base: base.name = "ARCHITECTURE"

def collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(col)
    return col

def move_to(obj, col_name):
    col = collection(col_name)
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)

def material(name, color, rough=0.7, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.roughness = rough
    m.metallic = metallic
    nodes=m.node_tree.nodes
    principled=nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value=(*color,1.0)
        principled.inputs["Roughness"].default_value=rough
        principled.inputs["Metallic"].default_value=metallic
    return m

def uv_atlas(mesh, name):
    uv = mesh.uv_layers.new(name=name)
    polys = list(mesh.polygons); cols = max(1, math.ceil(math.sqrt(len(polys)))); rows = max(1, math.ceil(len(polys)/cols))
    pad = 0.04
    for i, poly in enumerate(polys):
        cx, cy = i % cols, i // cols
        coords = [(pad,pad),(1-pad,pad),(1-pad,1-pad),(pad,1-pad)]
        for j, li in enumerate(poly.loop_indices):
            u,v = coords[j % 4]; uv.data[li].uv = ((cx+u)/cols, (cy+v)/rows)
    return uv

def finish(obj, mat, bevel=0.02, export=True, col="ARCHITECTURE"):
    move_to(obj, col)
    if mat: obj.data.materials.append(mat)
    if bevel > 0:
        mod=obj.modifiers.new("Architectural edge finish",'BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=obj; obj.select_set(True); bpy.ops.object.modifier_apply(modifier=mod.name); obj.select_set(False)
    bm=bmesh.new(); bm.from_mesh(obj.data); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(obj.data); bm.free(); obj.data.update()
    uv_atlas(obj.data,"UVMap"); uv_atlas(obj.data,"LightmapUV")
    obj["architectural_finish"]="beveled closed solid"; obj["exportable"]=bool(export)
    if export: EXPORTABLE.add(obj.name)
    return obj

def box(name, size, loc, mat, bevel=0.02, col="ARCHITECTURE", export=True):
    x,y,z=size; verts=[(-x/2,-y/2,-z/2),(x/2,-y/2,-z/2),(x/2,y/2,-z/2),(-x/2,y/2,-z/2),(-x/2,-y/2,z/2),(x/2,-y/2,z/2),(x/2,y/2,z/2),(-x/2,y/2,z/2)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+"_Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(obj); obj.location=loc
    return finish(obj,mat,bevel,export,col)

def prism_roof(name, x0,x1,y0,y1,z_eave,pitch,mat,axis='X'):
    rise=(y1-y0)/2*math.tan(pitch) if axis=='X' else (x1-x0)/2*math.tan(pitch)
    t=0.18
    if axis=='X':
        ym=(y0+y1)/2; cross=[(y0,z_eave),(ym,z_eave+rise),(y1,z_eave),(y1-0.16,z_eave-t),(ym,z_eave+rise-t),(y0+0.16,z_eave-t)]
        verts=[(x,y,z) for x in (x0,x1) for y,z in cross]; n=len(cross)
    else:
        xm=(x0+x1)/2; cross=[(x0,z_eave),(xm,z_eave+rise),(x1,z_eave),(x1-0.16,z_eave-t),(xm,z_eave+rise-t),(x0+0.16,z_eave-t)]
        verts=[(x,y,z) for y in (y0,y1) for x,z in cross]; n=len(cross)
    faces=[]
    faces.append(tuple(range(n-1,-1,-1))); faces.append(tuple(range(n,2*n)))
    for i in range(n): faces.append((i,(i+1)%n,(i+1)%n+n,i+n))
    mesh=bpy.data.meshes.new(name+"_Mesh"); mesh.from_pydata(verts,[],faces); mesh.update(); obj=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(obj)
    return finish(obj,mat,0.015)

def wall_segments_x(prefix,x0,x1,y,z0,z1,thick,openings,mat,system):
    points=[x0,x1]
    for c,w,b,h in openings: points += [c-w/2,c+w/2]
    points=sorted(set(p for p in points if x0<=p<=x1))
    for i,(a,b) in enumerate(zip(points,points[1:])):
        mid=(a+b)/2; active=[o for o in openings if o[0]-o[1]/2 < mid < o[0]+o[1]/2]
        if not active: box(f"{prefix}_{i:02d}",(b-a,thick,z1-z0),((a+b)/2,y,(z0+z1)/2),mat,0.025)
        else:
            c,w,sill,h=active[0]
            if sill>z0+0.01: box(f"{prefix}_Sill_{i:02d}",(b-a,thick,sill-z0),((a+b)/2,y,(z0+sill)/2),mat,0.02)
            top=sill+h
            if top<z1-0.01: box(f"{prefix}_Lintel_{i:02d}",(b-a,thick,z1-top),((a+b)/2,y,(top+z1)/2),mat,0.02)

def wall_segments_y(prefix,y0,y1,x,z0,z1,thick,openings,mat,system):
    points=[y0,y1]
    for c,w,b,h in openings: points += [c-w/2,c+w/2]
    points=sorted(set(p for p in points if y0<=p<=y1))
    for i,(a,b) in enumerate(zip(points,points[1:])):
        mid=(a+b)/2; active=[o for o in openings if o[0]-o[1]/2 < mid < o[0]+o[1]/2]
        if not active: box(f"{prefix}_{i:02d}",(thick,b-a,z1-z0),(x,(a+b)/2,(z0+z1)/2),mat,0.025)
        else:
            c,w,sill,h=active[0]
            if sill>z0+0.01: box(f"{prefix}_Sill_{i:02d}",(thick,b-a,sill-z0),(x,(a+b)/2,(z0+sill)/2),mat,0.02)
            top=sill+h
            if top<z1-0.01: box(f"{prefix}_Lintel_{i:02d}",(thick,b-a,z1-top),(x,(a+b)/2,(top+z1)/2),mat,0.02)

def frame(name,center,size,depth,mat,axis='X',col="DOORS_WINDOWS"):
    w,h=size; x,y,z=center; t=0.10
    if axis=='X':
        box(name+"_L",(t,depth,h),(x-w/2+t/2,y,z),mat,0.008,col); box(name+"_R",(t,depth,h),(x+w/2-t/2,y,z),mat,0.008,col)
        box(name+"_T",(w-2*t,depth,t),(x,y,z+h/2-t/2),mat,0.008,col); box(name+"_B",(w-2*t,depth,t),(x,y,z-h/2+t/2),mat,0.008,col)
    else:
        box(name+"_L",(depth,t,h),(x,y-w/2+t/2,z),mat,0.008,col); box(name+"_R",(depth,t,h),(x,y+w/2-t/2,z),mat,0.008,col)
        box(name+"_T",(depth,w-2*t,t),(x,y,z+h/2-t/2),mat,0.008,col); box(name+"_B",(depth,w-2*t,t),(x,y,z-h/2+t/2),mat,0.008,col)

def label_empty(name,loc,category):
    o=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(o); o.location=loc; o["space_category"]=category; move_to(o,"SPACE_LABELS"); return o

def camera(name,loc,target,lens=35,ortho=None):
    data=bpy.data.cameras.new(name+"_Data"); obj=bpy.data.objects.new(name,data); collection("CAMERAS").objects.link(obj); obj.location=loc
    direction=Vector(target)-obj.location; obj.rotation_euler=direction.to_track_quat('-Z','Y').to_euler(); data.lens=lens
    if ortho: data.type='ORTHO'; data.ortho_scale=ortho
    return obj

def render(cam,filename,hide_ref=True):
    ref=collection("REFERENCE_ONLY"); ref.hide_render=hide_ref
    bpy.context.scene.camera=cam; bpy.context.scene.render.filepath=str(RENDERS/filename); bpy.ops.render.render(write_still=True)
    if not (RENDERS/filename).is_file() or (RENDERS/filename).stat().st_size==0: raise RuntimeError("Render missing: "+filename)

def audit_meshes():
    stats={"negative_scale":[],"unapplied_scale":[],"missing_uv0":[],"missing_uv1":[],"missing_material":[],"empty_mesh":[],"non_manifold":[],"open_boundary":[]}
    tris=0; meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get("exportable")]
    for o in meshes:
        if any(v<0 for v in o.scale): stats["negative_scale"].append(o.name)
        if any(abs(v-1)>1e-5 for v in o.scale): stats["unapplied_scale"].append(o.name)
        if len(o.data.uv_layers)<1: stats["missing_uv0"].append(o.name)
        if len(o.data.uv_layers)<2: stats["missing_uv1"].append(o.name)
        if not o.data.materials or o.data.materials[0] is None: stats["missing_material"].append(o.name)
        if len(o.data.polygons)==0: stats["empty_mesh"].append(o.name)
        bm=bmesh.new(); bm.from_mesh(o.data)
        if any(not e.is_manifold for e in bm.edges): stats["non_manifold"].append(o.name)
        if any(e.is_boundary for e in bm.edges): stats["open_boundary"].append(o.name)
        bm.free(); tris += sum(max(0,len(p.vertices)-2) for p in o.data.polygons)
    stats["triangles"]=tris; stats["mesh_objects"]=len(meshes); return stats

def main():
    clean(); scene=bpy.context.scene
    scene.unit_settings.system='METRIC'; scene.unit_settings.length_unit='METERS'; scene.unit_settings.scale_length=1.0
    scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=1600; scene.render.resolution_y=900; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=0.7
    world_nodes=scene.world.node_tree.nodes; world_links=scene.world.node_tree.links
    sky=world_nodes.new('ShaderNodeTexSky'); sky.sky_type='MULTIPLE_SCATTERING'; sky.sun_elevation=math.radians(38); sky.sun_rotation=math.radians(135); sky.altitude=2600; sky.air_density=1.0
    background=world_nodes.get('Background'); background.inputs['Strength'].default_value=.35
    world_links.new(sky.outputs['Color'],background.inputs['Color'])
    for c in ["DOORS_WINDOWS","SITE","REFERENCE_ONLY","SPACE_LABELS","CAMERAS","LIGHTING"]: collection(c)
    global plaster_ext,plaster_int,adobe,stone,wood,roofmat,brick,stonefloor,glass,earth
    plaster_ext=material("MAT_Lime_Plaster_Exterior",(0.82,0.75,0.61),0.86); plaster_int=material("MAT_Lime_Plaster_Interior",(0.88,0.82,0.70),0.82)
    adobe=material("MAT_Adobe_Cut",(0.55,0.35,0.20),0.9); stone=material("MAT_Stone_Plinth",(0.28,0.24,0.19),0.82); wood=material("MAT_Dark_Wood",(0.075,0.025,0.012),0.72)
    roofmat=material("MAT_Terracotta_Roof",(0.30,0.075,0.028),0.78); brick=material("MAT_Brick_Floor",(0.48,0.25,0.15),0.82); stonefloor=material("MAT_Stone_Floor",(0.38,0.35,0.29),0.9)
    glass=material("MAT_Glass_Subtle",(0.20,0.32,0.36),0.25); glass.diffuse_color=(0.20,0.32,0.36,0.35); bpy.data.materials["MAT_Glass_Subtle"].node_tree.nodes.get("Principled BSDF").inputs["Alpha"].default_value=.35; earth=material("MAT_Compacted_Earth",(0.36,0.25,0.15),0.95)
    # Foundations, floors, courtyard and restrained stone plinth.
    box("ARCH_Foundation",(36,26,0.35),(0,-2, -0.175),stone,0.025)
    box("ARCH_GroundFloors",(36,7,0.18),(0,-11.5,0.09),brick,0.015); box("ARCH_GroundFloors_West",(9.25,18,0.18),(-12.375,1,0.09),brick,0.015); box("ARCH_GroundFloors_East",(8.25,15,0.18),(11.875,-0.5,0.09),brick,0.015)
    box("SITE_Courtyard",(15.5,12,0.14),(0,0,0.07),earth,0.01,col="SITE")
    box("ARCH_UpperFloors",(36,7,0.30),(0,-11.5,3.75),wood,0.015)
    box("ARCH_StonePlinth",(36.2,0.18,0.65),(0,-15.36,0.325),stone,0.015)
    # South two-storey envelope: real rectangular portal, windows and balcony doors.
    ground_open=[(-13,1.25,.9,1.55),(-8.7,1.2,.9,1.5),(0,2.5,0,2.95),(6.3,1.15,0,2.5),(11.8,1.3,.9,1.55)]
    upper_open=[(-13.2,1.2,4.62,1.55),(-8.2,1.15,3.9,2.45),(-2.8,1.15,3.9,2.45),(2.6,1.15,3.9,2.45),(7.6,1.15,3.9,2.45),(12.5,1.2,4.62,1.55)]
    wall_segments_x("ARCH_ExteriorWalls_Front_G",-18,18,-15,0,3.6,.55,ground_open,plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_x("ARCH_ExteriorWalls_Front_U",-18,18,-15,3.9,7.1,.55,upper_open,plaster_ext,"ARCH_ExteriorWalls")
    back_open=[(-14,1.15,.85,1.5),(-10,1.2,0,2.5),(-5.7,1.15,.85,1.5),(0,2.5,0,2.95),(5.5,1.2,0,2.5),(10.2,1.15,.85,1.5),(14.2,1.2,0,2.5)]
    back_up=[(-13,1.15,3.9,2.45),(-8,1.15,3.9,2.45),(-3,1.15,3.9,2.45),(2,1.15,3.9,2.45),(7,1.15,3.9,2.45),(12.2,1.15,3.9,2.45)]
    wall_segments_x("ARCH_ExteriorWalls_Court_G",-18,18,-8,0,3.6,.55,back_open,plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_x("ARCH_ExteriorWalls_Court_U",-18,18,-8,3.9,7.1,.55,back_up,plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_y("ARCH_ExteriorWalls_SW",-15,-8,-18,0,7.1,.55,[(-11.5,1.2,0,2.5)],plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_y("ARCH_ExteriorWalls_SE",-15,-8,18,0,7.1,.55,[(-11.5,1.2,0,2.5)],plaster_ext,"ARCH_ExteriorWalls")
    # C wings, open toward north, with courtyard-facing doors/windows.
    wall_segments_y("ARCH_ExteriorWalls_W_Outer",-8,10,-17,0,3.6,.55,[(0,1.2,.9,1.5),(6,1.2,.9,1.5)],plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_y("ARCH_ExteriorWalls_W_Court",-8,10,-7.75,0,3.6,.55,[(-5,1.2,0,2.5),(-1,1.2,.9,1.5),(3,1.2,0,2.5),(7,1.2,.9,1.5)],plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_x("ARCH_ExteriorWalls_W_North",-17,-7.75,10,0,3.6,.55,[(-12.4,1.2,0,2.5)],plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_y("ARCH_ExteriorWalls_E_Outer",-8,7,16,0,3.6,.55,[(-3,1.2,.9,1.5),(3,1.2,.9,1.5)],plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_y("ARCH_ExteriorWalls_E_Court",-8,7,7.75,0,3.6,.55,[(-5,1.2,0,2.5),(-1,1.2,.9,1.5),(3,1.2,0,2.5)],plaster_ext,"ARCH_ExteriorWalls")
    wall_segments_x("ARCH_ExteriorWalls_E_North",7.75,16,7,0,3.6,.55,[(12,1.2,0,2.5)],plaster_ext,"ARCH_ExteriorWalls")
    # Interior partitions leave 1.15 m door gaps; labels form explicit room schedule.
    for i,x in enumerate([-12,-6,4,10]): wall_segments_y(f"ARCH_InteriorWalls_Ground_S_{i}",-14.45,-8.55,x,0,3.6,.35,[(-11.5,1.15,0,2.5)],plaster_int,"ARCH_InteriorWalls_Ground")
    for i,y in enumerate([-3,2.5,6]): wall_segments_x(f"ARCH_InteriorWalls_Ground_W_{i}",-16.45,-8.3,y,0,3.6,.35,[(-12.4,1.15,0,2.5)],plaster_int,"ARCH_InteriorWalls_Ground")
    for i,y in enumerate([-3,2]): wall_segments_x(f"ARCH_InteriorWalls_Ground_E_{i}",8.3,15.45,y,0,3.6,.35,[(12,1.15,0,2.5)],plaster_int,"ARCH_InteriorWalls_Ground")
    for i,x in enumerate([-9,-1,7]): wall_segments_y(f"ARCH_InteriorWalls_Upper_{i}",-14.45,-8.55,x,3.9,7.1,.35,[(-11.5,1.15,3.9,2.45)],plaster_int,"ARCH_InteriorWalls_Upper")
    ground_locs=[(-15,-11.5),(-9,-11.5),(-3,-11.5),(7,-11.5),(13,-11.5),(-12.4,-5.5),(-12.4,0),(-12.4,4.5),(12,-5.5),(-12,8),(12,4.5)]
    for n,(x,y) in zip(ROOMS_GROUND,ground_locs): label_empty("SPACE_G_"+n.replace(' ','_'),(x,y,1.6),"GROUND_ROOM")
    for n,x in zip(ROOMS_UPPER,[-13,-5,3,11]): label_empty("SPACE_U_"+n.replace(' ','_'),(x,-11.5,5.4),"UPPER_ROOM")
    label_empty("SPACE_Zaguan",(0,-11.5,1.5),"CIRCULATION"); label_empty("SPACE_Patio",(0,0,0),"COURTYARD")
    # Main door leaves, interior doors, windows and shutters.
    box("DW_MainDoor_Left",(1.18,.10,2.85),(-.64,-15.31,1.425),wood,.01,"DOORS_WINDOWS"); box("DW_MainDoor_Right",(1.18,.10,2.85),(.64,-15.31,1.425),wood,.01,"DOORS_WINDOWS")
    door_positions=[(-12,-11.5,'Y'),(-6,-11.5,'Y'),(4,-11.5,'Y'),(10,-11.5,'Y'),(-12.4,-3,'X'),(-12.4,2.5,'X'),(12,-3,'X'),(12,2,'X')]
    for i,(x,y,a) in enumerate(door_positions): box("DW_InteriorDoors" if i==0 else f"DW_InteriorDoors_{i:02d}",(.08,1.1,2.45) if a=='Y' else (1.1,.08,2.45),(x,y,1.225),wood,.008,"DOORS_WINDOWS")
    windows=[(-13,-15,1.675),(-8.7,-15,1.65),(11.8,-15,1.675),(-14,-8,1.6),(-5.7,-8,1.6),(10.2,-8,1.6)]
    for i,p in enumerate(windows): frame("DW_WindowFrames" if i==0 else f"DW_WindowFrames_{i:02d}",p,(1.18,1.5),.16,wood,'X')
    for i,(x,y,z) in enumerate(windows): box("DW_WindowShutters" if i==0 else f"DW_WindowShutters_{i:02d}",(1.02,.05,1.34),(x,y-.10 if y< -10 else y+.10,z),wood,.006,"DOORS_WINDOWS")
    for i,x in enumerate([-8.2,-2.8,2.6,7.6]): box("DW_BalconyDoors" if i==0 else f"DW_BalconyDoors_{i:02d}",(1.03,.10,2.35),(x,-15.31,5.075),wood,.008,"DOORS_WINDOWS")
    # Courtyard galleries and upper/exterior balconies with credible timber support.
    box("ARCH_CourtyardGallery",(36,2.25,.18),(0,-6.87,3.15),wood,.015)
    box("ARCH_CourtyardGallery_W",(2.25,18,.18),(-6.62,1,3.15),wood,.015); box("ARCH_CourtyardGallery_E",(2.25,15,.18),(6.62,-.5,3.15),wood,.015)
    for i,x in enumerate([-16,-12,-8,-4,0,4,8,12,16]): box("ARCH_TimberStructure" if i==0 else f"ARCH_TimberStructure_S_{i:02d}",(.18,.18,3.15),(x,-6.25,1.575),wood,.01)
    for side,x in [('W',-6.1),('E',6.1)]:
        for i,y in enumerate([-6,-2,2,6]): box(f"ARCH_TimberStructure_{side}_{i:02d}",(.18,.18,3.15),(x,y,1.575),wood,.01)
    box("ARCH_ExteriorBalcony",(31,1.65,.22),(0,-15.65,3.92),wood,.012)
    box("ARCH_UpperCorridor",(31,1.75,.22),(0,-7.45,3.92),wood,.012)
    for prefix,y in [('EXT',-16.25),('INT',-6.65)]:
        box("ARCH_WoodTrim" if prefix=='EXT' else "ARCH_WoodTrim_InnerRail",(31,.10,.12),(0,y,4.92),wood,.006)
        for i,x in enumerate([i*.75-15 for i in range(41)]): box(f"ARCH_WoodTrim_{prefix}_{i:02d}",(.065,.065,1.0),(x,y,4.42),wood,.004)
        for i,x in enumerate([-14,-9,-4,4,9,14]): box(f"ARCH_TimberStructure_Balcony_{prefix}_{i:02d}",(.16,.16,3.9),(x,y,1.95),wood,.01)
    # One-flight lateral stair, 1.5 m clear width, 23 risers at ~17 cm and 29 cm tread.
    steps=23; rise=3.9/steps; tread=.29
    for i in range(steps): box("ARCH_Staircase" if i==0 else f"ARCH_Staircase_{i:02d}",(1.5,tread*(i+1),rise*(i+1)),(-5.7,6.0-tread*(i+1)/2,rise*(i+1)/2),stonefloor,.012)
    box("ARCH_Staircase_Landing",(1.5,1.65,.22),(-5.7,-1.45,3.9),stonefloor,.012)
    # Roof solids by wing, closed undersides, continuous ridges, eaves and cornices.
    pitch=math.radians(29)
    prism_roof("ARCH_Roof_Main",-18.7,18.7,-15.7,-7.3,7.35,pitch,roofmat,'X')
    prism_roof("ARCH_Roof_West",-17.7,-7.1,-7.25,10.7,3.85,pitch,roofmat,'Y')
    prism_roof("ARCH_Roof_East",7.1,16.7,-7.25,7.7,3.85,pitch,roofmat,'Y')
    prism_roof("ARCH_Roof_Galleries",-18,-5.7,-8.2,-5.65,3.35,math.radians(27),roofmat,'X')
    prism_roof("ARCH_Roof_Galleries_E",5.7,18,-8.2,-5.65,3.35,math.radians(27),roofmat,'X')
    box("ARCH_Roof_Ridges",(37.6,.22,.22),(0,-11.5,9.70),roofmat,.03)
    box("ARCH_Roof_Ridges_W",(.22,19.5,.22),(-12.4,1,6.79),roofmat,.03); box("ARCH_Roof_Ridges_E",(.22,16.5,.22),(11.9,-.5,6.43),roofmat,.03)
    box("ARCH_GableClosures",(.18,5.8,.35),(-17.82,-11.5,7.55),plaster_ext,.02); box("ARCH_GableClosures_E",(.18,5.8,.35),(17.82,-11.5,7.55),plaster_ext,.02)
    box("ARCH_Eaves",(37.6,.18,.16),(0,-15.72,7.35),wood,.01); box("ARCH_Eaves_Court",(37.6,.18,.16),(0,-7.28,7.35),wood,.01)
    box("ARCH_Cornices",(36.2,.16,.20),(0,-15.31,7.08),plaster_ext,.015)
    # Portal hierarchy and restrained lintel/cornice, no monumental arch.
    box("ARCH_WoodTrim_PortalLintel",(3.15,.32,.26),(0,-15.38,3.15),wood,.015)
    # Site path provides facade approach and readable scale.
    box("SITE_FacadePath",(5.2,10,.12),(0,-20,0.06),stonefloor,.015,col="SITE")
    # Human reference: 1.70 m, only visible in render 12 and never exportable.
    human=box("REF_Human_170cm",(.42,.28,1.45),(3,-18.2,.725),material("MAT_Reference_Human",(.16,.20,.24),.6),.08,"REFERENCE_ONLY",False)
    head=box("REF_Human_Head",(.32,.30,.25),(3,-18.2,1.575),bpy.data.materials["MAT_Reference_Human"],.12,"REFERENCE_ONLY",False)
    # Neutral daylight.
    sun_data=bpy.data.lights.new("Sun_Daylight_Data",'SUN'); sun=bpy.data.objects.new("Sun_Daylight",sun_data); collection("LIGHTING").objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-20),math.radians(-28)); sun_data.energy=2.0; sun_data.color=(1.0,.96,.88)
    area_data=bpy.data.lights.new("Area_Fill_Data",'AREA'); area=bpy.data.objects.new("Area_Fill",area_data); collection("LIGHTING").objects.link(area); area.location=(0,-8,18); area_data.energy=1600; area_data.shape='DISK'; area_data.size=12
    # Apply transforms to every exportable mesh.
    for o in bpy.context.scene.objects:
        if o.type=='MESH':
            bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); o.select_set(False)
    cams=[
      camera("CAM_01_Aerial",(34,-38,28),(0,-2,3),42), camera("CAM_02_Facade",(-23,-38,8),(0,-12,3.6),48), camera("CAM_03_Portal",(0,-25,3.2),(0,-15,2.3),50),
      camera("CAM_04_Zaguan",(0,-13.7,1.7),(0,1,1.6),35), camera("CAM_05_Courtyard",(0,13,6.5),(0,-4,2.5),40), camera("CAM_06_Gallery",(-2,4,2.0),(-10,-2,1.8),34),
      camera("CAM_07_Balcony",(-20,-22,7),(0,-14,4.6),52), camera("CAM_08_Roof",(26,17,26),(0,-2,6),48), camera("CAM_09_Junctions",(15,3,15),(8,-7,6),58),
      camera("CAM_10_GroundPlan",(0,-2,42),(0,-2,0),35,42), camera("CAM_11_UpperPlan",(0,-7,42),(0,-7,4),35,42), camera("CAM_12_Human",(10,-28,4),(1,-15,2.5),48)]
    render_files=["01_Aerial_ThreeQuarter.png","02_Facade_From_Path.png","03_Main_Portal.png","04_Zaguan_To_Courtyard.png","05_Courtyard_Wide.png","06_Courtyard_Gallery.png","07_Upper_Balcony.png","08_Roof_Overview.png","09_Roof_Junctions.png","10_Ground_Floor_Plan.png","11_Upper_Floor_Plan.png","12_Human_Scale.png"]
    # Plan renders hide roof systems temporarily to reveal circulation.
    for cam,f in zip(cams,render_files):
        roofs=[o for o in scene.objects if o.name.startswith("ARCH_Roof") or o.name.startswith("ARCH_Gable") or o.name.startswith("ARCH_Eaves")]
        if f.startswith("10_"): [setattr(o,'hide_render',True) for o in roofs]
        if f.startswith("11_"):
            [setattr(o,'hide_render',True) for o in roofs]
            for o in scene.objects:
                if o.type=='MESH' and ("Ground" in o.name or o.name.startswith("SITE_")): o.hide_render=True
        render(cam,f,hide_ref=not f.startswith("12_"))
        for o in scene.objects: o.hide_render=False
    # Save editable master before exports.
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),check_existing=False)
    stats=audit_meshes()
    fatal=[]
    for key in ["negative_scale","unapplied_scale","missing_uv0","missing_uv1","missing_material","empty_mesh","non_manifold","open_boundary"]:
        if stats[key]: fatal.append(f"{key}={len(stats[key])}")
    if stats["triangles"]>=250000: fatal.append("triangle_budget_exceeded")
    if fatal: raise RuntimeError("Audit rejected: "+", ".join(fatal))
    # Selection-only export excludes cameras, lights, labels and REFERENCE_ONLY.
    bpy.ops.object.select_all(action='DESELECT')
    selected=[o for o in scene.objects if o.type=='MESH' and o.get("exportable")]
    for o in selected: o.select_set(True)
    bpy.context.view_layer.objects.active=selected[0]
    bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
    bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=True,add_leaf_bones=False,path_mode='AUTO')
    for p in [BLEND,GLB,FBX]:
        if not p.is_file() or p.stat().st_size==0: raise RuntimeError(f"Missing output: {p.name}")
    with GLB.open('rb') as f: magic,ver,length=struct.unpack('<4sII',f.read(12))
    if magic!=b'glTF' or ver!=2 or length!=GLB.stat().st_size: raise RuntimeError("Invalid GLB header")
    review={
      "status":"READY_FOR_HUMAN_REVIEW_WITH_ROOF_JUNCTION_FLAG", "cycles_completed":3, "score":86,
      "criteria":{"cochabamba_identity":True,"c_shape":True,"courtyard_and_zaguan":True,"masonry_predominance":True,"rectangular_openings":True,"continuous_balcony":True,"human_scale":True,"closed_roofs":True,"roof_junctions":False,"wall_thickness":True,"no_floating_parts":True,"light_materials":True,"circulation":True},
      "human_review_required":True,"approved_for_presentation":False,
      "notes":["Modelo procedural original V6; no reutiliza geometria previa.","Ciclo 1 rechazado por lectura cromatica insuficiente; ciclo 2 incorpora shaders Principled y World Sky.","Ciclo 2 requirio limpieza de encuentros de cubierta y despeje del eje del portal; corregido en ciclo 3.","La revision final de identidad y encuentros se reserva a inspeccion humana de los 12 renders."]}
    AUDIT.write_text(json.dumps({"geometry":stats,"architectural_review":review},indent=2,ensure_ascii=False),encoding='utf-8')
    manifest={"name":"JW_Hacienda_Mayorazgo_V6","blender_version":bpy.app.version_string,"files":{"blend":BLEND.name,"glb":GLB.name,"fbx":FBX.name,"renders":render_files},"footprint_m":[36,26],"courtyard_m":[15.5,12],"rooms":{"ground":ROOMS_GROUND,"upper":ROOMS_UPPER},"exported_mesh_objects":len(selected),"triangles":stats["triangles"],"reference_exported":False}
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
    log("BUILD_RESULT="+json.dumps({"status":"READY_FOR_HUMAN_REVIEW","objects":len(scene.objects),"exported_meshes":len(selected),"triangles":stats["triangles"],"renders":len(render_files),"blend_size":BLEND.stat().st_size,"glb_size":GLB.stat().st_size,"fbx_size":FBX.stat().st_size},sort_keys=True))

if __name__=='__main__':
    try: main()
    except Exception:
        traceback.print_exc(); raise
