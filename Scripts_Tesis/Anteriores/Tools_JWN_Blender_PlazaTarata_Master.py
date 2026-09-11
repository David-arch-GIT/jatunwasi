# -*- coding: utf-8 -*-
"""
JATUN WASI NAWPAKAY
PLAZA TARATA / COCHABAMBA - BLENDER MASTER GENERATOR
Compatible target: Blender 4.x (also uses long-stable bpy APIs)

Purpose
-------
Generate a professional modular colonial plaza kit based on the APPROVED visual design:
- 33m x 31m complete square
- continuous perimeter promenade
- four large chamfered garden quadrants
- central octagonal fountain/monument
- 8 public benches
- 8 complete colonial street lamps
- low ornamental garden fencing
- placement JSON for palms / shade trees / shrubs / flowers
- FBX exports for Unreal Engine
- saved .blend master file

This deliberately uses Blender as the "asset factory" and Unreal as the final real-time scene.
No Codex is required to generate these meshes.

Output folder
-------------
C:\\UnrealProjects\\JatunWasiNawpakay\\External\\BlenderGenerated\\PlazaTarata

Generated files
---------------
JWN_PlazaTarata_Master.blend
SM_PLZT_Hardscape.fbx
SM_PLZT_GardenArchitecture.fbx
SM_PLZT_CentralFountain.fbx
SM_PLZT_Bench.fbx
SM_PLZT_ColonialLamp.fbx
SM_PLZT_GardenFence.fbx
PlazaTarata_layout.json

Unreal convention
-----------------
Blender units are meters.
Export FBX uses scale handling compatible with UE import.
Master local origin = plaza center.
"""

import bpy
import math
import json
import os
from mathutils import Vector

OUT = r"C:\UnrealProjects\JatunWasiNawpakay\External\BlenderGenerated\PlazaTarata"
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# RESET / UNITS
# ---------------------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

for datablocks in (
    bpy.data.meshes, bpy.data.curves, bpy.data.materials
):
    # materials are recreated below; don't purge here because Blender can retain defaults safely
    pass

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
print("JWN_BLENDER_VERSION=" + bpy.app.version_string)
print("JWN_RENDER_ENGINE=" + str(scene.render.engine))
# Blender 5.2 uses BLENDER_EEVEE (not BLENDER_EEVEE_NEXT).
# This generator does not render anything, so no render-engine switch is required.
# Keep the factory-startup engine to avoid version-specific enum failures.
# scene.render.engine = 'BLENDER_EEVEE'

# ---------------------------------------------------------------------------
# COLLECTIONS
# ---------------------------------------------------------------------------
def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)
    return c

COL_HARDSCAPE = collection("PLZT_Hardscape")
COL_GARDENS = collection("PLZT_GardenArchitecture")
COL_FOUNTAIN = collection("PLZT_CentralFountain")
COL_BENCH_MASTER = collection("PLZT_Bench_Master")
COL_LAMP_MASTER = collection("PLZT_Lamp_Master")
COL_FENCE = collection("PLZT_GardenFence")
COL_PREVIEW = collection("PLZT_PreviewInstances")

def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)

# ---------------------------------------------------------------------------
# MATERIALS
# ---------------------------------------------------------------------------
def mat_principled(name, base, roughness=0.55, metallic=0.0, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Alpha"].default_value = alpha
    return m

M_STONE = mat_principled("M_PLZT_Stone_Light", (0.47,0.41,0.32), 0.78)
M_STONE_DARK = mat_principled("M_PLZT_Stone_Dark", (0.22,0.20,0.17), 0.84)
M_BRICK = mat_principled("M_PLZT_Brick_Warm", (0.38,0.16,0.08), 0.78)
M_SOIL = mat_principled("M_PLZT_Soil", (0.12,0.065,0.03), 0.95)
M_IRON = mat_principled("M_PLZT_Iron_Black", (0.015,0.018,0.02), 0.28, 0.72)
M_WOOD = mat_principled("M_PLZT_Wood_Warm", (0.24,0.07,0.025), 0.52)
M_WATER = mat_principled("M_PLZT_Water", (0.03,0.22,0.28), 0.12, 0.0, 0.88)
M_GLASS = mat_principled("M_PLZT_Lamp_Glass", (0.23,0.20,0.12), 0.12, 0.05, 0.65)

# ---------------------------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------------------------
def bevel(obj, width=0.03, segments=3):
    if not hasattr(obj.data, "polygons"):
        return
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'

def cube(name, loc, scale_xyz, mat, col, bevel_w=0.02):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale_xyz
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if bevel_w:
        bevel(o, bevel_w, 3)
    move_to_collection(o, col)
    return o

def cyl(name, loc, radius, depth, mat, col, vertices=32, bevel_w=0.015):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o=bpy.context.object
    o.name=name
    if mat:
        o.data.materials.append(mat)
    if bevel_w:
        bevel(o, bevel_w, 3)
    move_to_collection(o,col)
    return o

def ring_mesh(name, center, outer_r, inner_r, height, mat, col, sides=8):
    verts=[]
    faces=[]
    z0=center[2]-height/2
    z1=center[2]+height/2
    for z in (z0,z1):
        for r in (outer_r, inner_r):
            for i in range(sides):
                a=2*math.pi*i/sides
                verts.append((center[0]+math.cos(a)*r, center[1]+math.sin(a)*r, z))
    # indices: lower outer 0, lower inner s, upper outer 2s, upper inner 3s
    lo=0; li=sides; uo=2*sides; ui=3*sides
    for i in range(sides):
        j=(i+1)%sides
        faces.append((lo+i,lo+j,uo+j,uo+i))     # outer wall
        faces.append((li+j,li+i,ui+i,ui+j))     # inner wall
        faces.append((uo+i,uo+j,ui+j,ui+i))     # top
        faces.append((lo+j,lo+i,li+i,li+j))     # bottom
    mesh=bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    col.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    bevel(o,0.025,3)
    return o

def prism_polygon(name, pts_xy, z0, height, mat, col):
    n=len(pts_xy)
    verts=[(x,y,z0) for x,y in pts_xy]+[(x,y,z0+height) for x,y in pts_xy]
    faces=[]
    faces.append(tuple(range(n-1,-1,-1)))
    faces.append(tuple(range(n,2*n)))
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,n+j,n+i))
    mesh=bpy.data.meshes.new(name+"_Mesh")
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(name,mesh)
    col.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    bevel(o,0.025,3)
    return o

def rect_ring(name, outer_w, outer_h, inner_w, inner_h, z0, height, mat, col):
    # four non-overlapping strips
    t_x=(outer_w-inner_w)/2
    t_y=(outer_h-inner_h)/2
    cube(name+"_N",(0,(inner_h/2+t_y/2),z0+height/2),(outer_w,t_y,height),mat,col,0.01)
    cube(name+"_S",(0,-(inner_h/2+t_y/2),z0+height/2),(outer_w,t_y,height),mat,col,0.01)
    cube(name+"_E",((inner_w/2+t_x/2),0,z0+height/2),(t_x,inner_h,height),mat,col,0.01)
    cube(name+"_W",(-(inner_w/2+t_x/2),0,z0+height/2),(t_x,inner_h,height),mat,col,0.01)

def curve_tube(name, points, radius, mat, col, resolution=3):
    cu=bpy.data.curves.new(name+"_Curve","CURVE")
    cu.dimensions='3D'
    cu.resolution_u=resolution
    cu.bevel_depth=radius
    cu.bevel_resolution=3
    sp=cu.splines.new('BEZIER')
    sp.bezier_points.add(len(points)-1)
    for bp,co in zip(sp.bezier_points,points):
        bp.co=co
        bp.handle_left_type='AUTO'
        bp.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,cu)
    col.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return o

def join_objects(objs, name, col):
    """
    Join a modular master and normalize its pivot to WORLD (0,0,0).

    Critical fix: previous builds inherited the active sub-object origin.
    For the lamp this could be the top finial around Z=3.26 m, so duplicating
    the master at Z=0 shifted the complete lamp below the plaza.
    """
    if not objs:
        return None
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.hide_set(False)
        o.hide_viewport=False
        o.select_set(True)
        bpy.context.view_layer.objects.active=o

    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    o=bpy.context.object
    o.name=name
    move_to_collection(o,col)

    # Preserve world geometry and move pivot to plaza ground origin.
    scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.objects.active=o
    o.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

    o.rotation_euler=(0.0,0.0,0.0)
    o.scale=(1.0,1.0,1.0)
    return o

def duplicate_master(master, name, loc, yaw_deg, col):
    o=master.copy()
    o.data=master.data.copy()
    o.name=name
    o.location=loc
    o.rotation_euler[2]=math.radians(yaw_deg)
    col.objects.link(o)
    return o

# ---------------------------------------------------------------------------
# MASTER PLAN DIMENSIONS
# ---------------------------------------------------------------------------
PLAZA_W=33.0
PLAZA_H=31.0
PERIMETER_W=2.7
MAIN_W=4.0
SECONDARY_W=3.2
CENTER_CIVIC_R=5.60
FOUNTAIN_OUTER_R=2.65

PAV_Z=0.00
PAV_H=0.10
SOIL_Z=0.08
SOIL_H=0.08

# ---------------------------------------------------------------------------
# HARDSCAPE
# ---------------------------------------------------------------------------
# continuous outer promenade, not one giant overlapping slab
rect_ring(
    "PLZT_Perimeter",
    PLAZA_W, PLAZA_H,
    PLAZA_W-2*PERIMETER_W, PLAZA_H-2*PERIMETER_W,
    PAV_Z, PAV_H, M_STONE, COL_HARDSCAPE
)

inner_w=PLAZA_W-2*PERIMETER_W
inner_h=PLAZA_H-2*PERIMETER_W

# cardinal walks terminating at the central civic octagon/ring
cube("PLZT_Axis_West",(-((CENTER_CIVIC_R+(inner_w/2))/2),0,PAV_Z+PAV_H/2),
     (inner_w/2-CENTER_CIVIC_R,MAIN_W,PAV_H),M_STONE_DARK,COL_HARDSCAPE,0.01)
cube("PLZT_Axis_East",(((CENTER_CIVIC_R+(inner_w/2))/2),0,PAV_Z+PAV_H/2),
     (inner_w/2-CENTER_CIVIC_R,MAIN_W,PAV_H),M_STONE_DARK,COL_HARDSCAPE,0.01)
cube("PLZT_Axis_North",(0,((CENTER_CIVIC_R+(inner_h/2))/2),PAV_Z+PAV_H/2),
     (MAIN_W,inner_h/2-CENTER_CIVIC_R,PAV_H),M_STONE_DARK,COL_HARDSCAPE,0.01)
cube("PLZT_Axis_South",(0,-((CENTER_CIVIC_R+(inner_h/2))/2),PAV_Z+PAV_H/2),
     (MAIN_W,inner_h/2-CENTER_CIVIC_R,PAV_H),M_STONE_DARK,COL_HARDSCAPE,0.01)

# central civic paving disc/octagon
civic = cyl("PLZT_Central_Civic_Paving",(0,0,PAV_Z+PAV_H/2),CENTER_CIVIC_R,PAV_H,M_STONE,COL_HARDSCAPE,vertices=8,bevel_w=0.01)

# decorative border ring
ring_mesh("PLZT_Central_Border",(0,0,PAV_Z+0.07),CENTER_CIVIC_R, CENTER_CIVIC_R-0.28,0.12,M_BRICK,COL_HARDSCAPE,8)

# diagonal approach bands toward center, short and controlled
diag_start=5.65
diag_end=10.0
for sx,sy,ang in [(1,1,45),(-1,1,135),(-1,-1,225),(1,-1,315)]:
    mid=(diag_start+diag_end)/2
    length=diag_end-diag_start
    x=sx*mid/math.sqrt(2)
    y=sy*mid/math.sqrt(2)
    o=cube(f"PLZT_Diagonal_{sx}_{sy}",(x,y,PAV_Z+PAV_H/2),
           (length,2.4,PAV_H),M_STONE,COL_HARDSCAPE,0.01)
    o.rotation_euler[2]=math.radians(ang)

# ---------------------------------------------------------------------------
# FOUR GARDENS WITH CHAMFERED INNER CORNERS
# ---------------------------------------------------------------------------
x_outer=inner_w/2-0.45
y_outer=inner_h/2-0.45
x_inner=3.60
y_inner=3.60
ch=2.10

garden_polys = {
    "NW":[(-x_outer,y_inner+ch),(-x_outer,y_outer),(-x_inner,y_outer),(-x_inner,y_inner+ch),(-x_inner-ch,y_inner)],
    "NE":[(x_inner+ch,y_inner),(x_inner,y_inner+ch),(x_inner,y_outer),(x_outer,y_outer),(x_outer,y_inner+ch)],
    "SW":[(-x_outer,-y_inner-ch),(-x_inner-ch,-y_inner),(-x_inner,-y_inner-ch),(-x_inner,-y_outer),(-x_outer,-y_outer)],
    "SE":[(x_inner+ch,-y_inner),(x_outer,-y_inner-ch),(x_outer,-y_outer),(x_inner,-y_outer),(x_inner,-y_inner-ch)],
}

for tag,pts in garden_polys.items():
    prism_polygon("PLZT_GardenSoil_"+tag,pts,SOIL_Z,SOIL_H,M_SOIL,COL_GARDENS)
    # curb as continuous curve following polygon
    p3=[(x,y,PAV_Z+PAV_H+0.10) for x,y in pts]+[(pts[0][0],pts[0][1],PAV_Z+PAV_H+0.10)]
    curb=curve_tube("PLZT_GardenCurb_"+tag,p3,0.10,M_BRICK,COL_GARDENS)
    curb.data.bevel_resolution=2

# ---------------------------------------------------------------------------
# CENTRAL OCTAGONAL FOUNTAIN / MONUMENT
# ---------------------------------------------------------------------------
fparts=[]
fparts.append(cyl("Fountain_Foundation",(0,0,PAV_H+0.18),2.65,0.36,M_STONE_DARK,COL_FOUNTAIN,8,0.03))
fparts.append(ring_mesh("Fountain_BasinWall",(0,0,PAV_H+0.48),2.45,1.92,0.55,M_STONE,COL_FOUNTAIN,8))
fparts.append(cyl("Fountain_Water",(0,0,PAV_H+0.54),1.87,0.045,M_WATER,COL_FOUNTAIN,48,0.0))
fparts.append(cyl("Fountain_Pedestal_Base",(0,0,PAV_H+0.82),1.05,0.50,M_STONE_DARK,COL_FOUNTAIN,8,0.025))
fparts.append(cyl("Fountain_Pedestal_Mid",(0,0,PAV_H+1.27),0.76,0.55,M_STONE,COL_FOUNTAIN,8,0.025))
fparts.append(cyl("Fountain_Pedestal_Top",(0,0,PAV_H+1.68),0.52,0.30,M_STONE_DARK,COL_FOUNTAIN,8,0.02))
# decorative obelisk/column to give vertical civic hierarchy
fparts.append(cyl("Fountain_Column",(0,0,PAV_H+2.10),0.27,0.75,M_STONE,COL_FOUNTAIN,12,0.018))
fparts.append(cyl("Fountain_Cap",(0,0,PAV_H+2.52),0.43,0.14,M_STONE_DARK,COL_FOUNTAIN,8,0.015))

# statue anchor empty
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,PAV_H+2.75))
anchor=bpy.context.object
anchor.name="PLZT_StatueAnchor"
move_to_collection(anchor,COL_FOUNTAIN)

# ---------------------------------------------------------------------------
# BENCH MASTER
# ---------------------------------------------------------------------------
bench_objs=[]
# seat slats
for i in range(6):
    y=-0.31 + i*0.125
    bench_objs.append(cube(f"Bench_SeatSlat_{i}",(0,y,0.55),(1.90,0.105,0.075),M_WOOD,COL_BENCH_MASTER,0.025))
# back slats
for i in range(5):
    z=0.80+i*0.125
    o=cube(f"Bench_BackSlat_{i}",(0,0.32,z),(1.90,0.075,0.085),M_WOOD,COL_BENCH_MASTER,0.025)
    o.rotation_euler[0]=math.radians(-8)
    bench_objs.append(o)
# iron side frames / legs
for sx in (-0.82,0.82):
    bench_objs.append(cyl("Bench_Leg", (sx,-0.18,0.27),0.055,0.54,M_IRON,COL_BENCH_MASTER,16,0.01))
    bench_objs.append(cyl("Bench_Leg", (sx,0.18,0.27),0.055,0.54,M_IRON,COL_BENCH_MASTER,16,0.01))
    curve_tube("Bench_SideFrame",
               [(sx,-0.27,0.48),(sx,0.05,0.58),(sx,0.28,0.91),(sx,0.28,1.28)],
               0.035,M_IRON,COL_BENCH_MASTER)
    # arm
    curve_tube("Bench_Arm",
               [(sx,-0.22,0.72),(sx,-0.02,0.80),(sx,0.25,0.80)],
               0.03,M_IRON,COL_BENCH_MASTER)
bench_master=join_objects(list(COL_BENCH_MASTER.objects),"SM_PLZT_Bench",COL_BENCH_MASTER)
bench_master.hide_viewport=True
bench_master.hide_render=True

# ---------------------------------------------------------------------------
# COLONIAL DOUBLE-HEAD STREET LAMP MASTER
# ---------------------------------------------------------------------------
lamp_objs=[]
lamp_objs.append(cyl("Lamp_Base0",(0,0,0.10),0.30,0.20,M_IRON,COL_LAMP_MASTER,24,0.02))
lamp_objs.append(cyl("Lamp_Base1",(0,0,0.32),0.22,0.28,M_IRON,COL_LAMP_MASTER,24,0.02))
lamp_objs.append(cyl("Lamp_Base2",(0,0,0.55),0.14,0.18,M_IRON,COL_LAMP_MASTER,24,0.015))
lamp_objs.append(cyl("Lamp_Shaft",(0,0,1.85),0.075,2.45,M_IRON,COL_LAMP_MASTER,20,0.008))
lamp_objs.append(cyl("Lamp_Collar",(0,0,3.02),0.13,0.12,M_IRON,COL_LAMP_MASTER,20,0.01))
# curved arms
for sx in (-1,1):
    arm=curve_tube(f"Lamp_Arm_{sx}",
                   [(0,0,3.07),(0.28*sx,0,3.18),(0.53*sx,0,3.35),(0.68*sx,0,3.27)],
                   0.035,M_IRON,COL_LAMP_MASTER)
    # lantern body as tapered-looking assembly
    lamp_objs.append(cyl(f"Lantern_Top_{sx}",(0.68*sx,0,3.29),0.16,0.10,M_IRON,COL_LAMP_MASTER,8,0.01))
    glass=cyl(f"Lantern_Glass_{sx}",(0.68*sx,0,3.08),0.18,0.34,M_GLASS,COL_LAMP_MASTER,8,0.008)
    lamp_objs.append(glass)
    lamp_objs.append(cyl(f"Lantern_Bottom_{sx}",(0.68*sx,0,2.88),0.13,0.08,M_IRON,COL_LAMP_MASTER,8,0.01))
    lamp_objs.append(cyl(f"Lantern_Finial_{sx}",(0.68*sx,0,2.78),0.04,0.14,M_IRON,COL_LAMP_MASTER,12,0.005))
# top finial
lamp_objs.append(cyl("Lamp_TopFinial",(0,0,3.26),0.055,0.20,M_IRON,COL_LAMP_MASTER,12,0.006))
lamp_master=join_objects(list(COL_LAMP_MASTER.objects),"SM_PLZT_ColonialLamp",COL_LAMP_MASTER)
lamp_master.hide_viewport=True
lamp_master.hide_render=True

# ---------------------------------------------------------------------------
# LOW GARDEN FENCE MASTER MODULE (1 m)
# ---------------------------------------------------------------------------
fence_objs=[]
# rails
fence_objs.append(cube("Fence_Rail_Low",(0,0,0.23),(1.0,0.035,0.035),M_IRON,COL_FENCE,0.008))
fence_objs.append(cube("Fence_Rail_High",(0,0,0.62),(1.0,0.035,0.035),M_IRON,COL_FENCE,0.008))
for x in (-0.5,-0.25,0,0.25,0.5):
    fence_objs.append(cyl("Fence_Picket",(x,0,0.42),0.018,0.82,M_IRON,COL_FENCE,10,0.004))
fence_master=join_objects(fence_objs,"SM_PLZT_GardenFence_1m",COL_FENCE)
fence_master.hide_viewport=True
fence_master.hide_render=True

# ---------------------------------------------------------------------------
# PREVIEW INSTANCES + LAYOUT JSON
# ---------------------------------------------------------------------------
layout = {
    "plaza_size_m":[PLAZA_W,PLAZA_H],
    "origin_note":"Place master origin at Unreal plaza center; approved working center previously measured near world (0,-1000,local plaza Z).",
    "benches":[],
    "lamps":[],
    "palms":[],
    "shade_trees":[],
    "flower_clusters":[],
    "shrub_clusters":[],
}

# positions are deliberate, tangent to garden edges and facing center/promenade
# APPROVED BENCH MASTERPLAN
# Benches are placed ONLY on the perimeter promenade, never inside garden soil.
# Master bench front points toward local -Y.
bench_layout = [
    (-14.45,  6.20,  90), (-6.20,  13.45,   0),   # NW: west + north promenade, faces garden
    ( 14.45,  6.20, -90), ( 6.20,  13.45,   0),   # NE: east + north promenade
    (-14.45, -6.20,  90), (-6.20, -13.45, 180),   # SW: west + south promenade
    ( 14.45, -6.20, -90), ( 6.20, -13.45, 180),   # SE: east + south promenade
]
for i,(x,y,yaw) in enumerate(bench_layout):
    b=duplicate_master(bench_master,f"PLZT_Bench_{i}",(x,y,PAV_H),yaw,COL_PREVIEW)
    b.hide_viewport=False; b.hide_render=False
    layout["benches"].append({"location_m":[x,y,PAV_H],"yaw_deg":yaw})

# 8 complete lamps, positioned on hard promenade not inside soil
# APPROVED COMPLETE-LAMP MASTERPLAN
# Lamps sit on hard promenade and frame the four cardinal approaches.
lamp_layout = [
    (-14.20, -10.80,   0), (-14.20,  10.80,   0),   # west side of perimeter promenade
    ( 14.20, -10.80, 180), ( 14.20,  10.80, 180),   # east side
    (-10.80,  13.20,  90), ( 10.80,  13.20,  90),   # north side
    (-10.80, -13.20, -90), ( 10.80, -13.20, -90),   # south side
]
for i,(x,y,yaw) in enumerate(lamp_layout):
    l=duplicate_master(lamp_master,f"PLZT_Lamp_{i}",(x,y,PAV_H),yaw,COL_PREVIEW)
    l.hide_viewport=False; l.hide_render=False
    layout["lamps"].append({"location_m":[x,y,PAV_H],"yaw_deg":yaw})

# vegetation markers: 2 palms and 2 shade-tree candidates per garden
veg_sets = {
    "NW":{"palms":[(-10.5,7.5),(-6.3,11.0)],"trees":[(-11.2,11.0),(-6.5,6.4)]},
    "NE":{"palms":[(10.5,7.5),(6.3,11.0)],"trees":[(11.2,11.0),(6.5,6.4)]},
    "SW":{"palms":[(-10.5,-7.5),(-6.3,-11.0)],"trees":[(-11.2,-11.0),(-6.5,-6.4)]},
    "SE":{"palms":[(10.5,-7.5),(6.3,-11.0)],"trees":[(11.2,-11.0),(6.5,-6.4)]},
}
for tag,v in veg_sets.items():
    for j,(x,y) in enumerate(v["palms"]):
        layout["palms"].append({"garden":tag,"location_m":[x,y,0.15],"yaw_deg":(j*37 + len(layout["palms"])*11)%360,"scale":round(0.94+0.02*(len(layout["palms"])%5),2)})
    for j,(x,y) in enumerate(v["trees"]):
        layout["shade_trees"].append({"garden":tag,"location_m":[x,y,0.15],"yaw_deg":(j*61 + len(layout["shade_trees"])*13)%360,"scale":round(0.92+0.03*(len(layout["shade_trees"])%4),2)})

# controlled shrub/flower placement
for tag,pts in garden_polys.items():
    cx=sum(p[0] for p in pts)/len(pts)
    cy=sum(p[1] for p in pts)/len(pts)
    offsets=[(-1.4,-0.9),(1.1,-0.7),(-0.8,1.0),(1.4,0.9)]
    for ox,oy in offsets:
        layout["shrub_clusters"].append({"garden":tag,"location_m":[cx+ox,cy+oy,0.16],"scale":1.0})
    foffs=[(-2.0,-1.5),(-0.7,-1.6),(0.7,-1.5),(2.0,-1.2),(-1.7,1.4),(0,1.5),(1.8,1.2)]
    for ox,oy in foffs:
        layout["flower_clusters"].append({"garden":tag,"location_m":[cx+ox,cy+oy,0.16],"scale":0.9})

# ---------------------------------------------------------------------------
# PRE-SAVE SPATIAL QA FOR THE APPROVED BLENDER MASTER
# ---------------------------------------------------------------------------
def world_min_z(obj):
    if obj.type != 'MESH':
        return obj.location.z
    return min((obj.matrix_world @ v.co).z for v in obj.data.vertices)

def point_in_poly(x, y, poly):
    inside=False
    j=len(poly)-1
    for i in range(len(poly)):
        xi,yi=poly[i]
        xj,yj=poly[j]
        denom=(yj-yi) if abs(yj-yi)>1e-12 else 1e-12
        if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/denom + xi):
            inside=not inside
        j=i
    return inside

def point_segment_distance(px,py,ax,ay,bx,by):
    vx,vy=bx-ax,by-ay
    wx,wy=px-ax,py-ay
    vv=vx*vx+vy*vy
    if vv <= 1e-12:
        return math.hypot(px-ax,py-ay)
    t=max(0.0,min(1.0,(wx*vx+wy*vy)/vv))
    qx,qy=ax+t*vx,ay+t*vy
    return math.hypot(px-qx,py-qy)

def min_poly_distance_from_origin(poly):
    d=1e9
    for i in range(len(poly)):
        ax,ay=poly[i]
        bx,by=poly[(i+1)%len(poly)]
        d=min(d,point_segment_distance(0,0,ax,ay,bx,by))
    return d

def on_perimeter_promenade(x,y):
    outer = abs(x) <= PLAZA_W/2 and abs(y) <= PLAZA_H/2
    inner = abs(x) < inner_w/2 and abs(y) < inner_h/2
    return outer and not inner

qa_errors=[]

# Blender can defer matrix_world updates immediately after changing object.location.
# Force the dependency graph to update before any support/contact QA.
bpy.context.view_layer.update()

def furniture_world_min_z(obj):
    # Bench/lamp preview instances use scale=1 and yaw-only rotation, so Z is
    # independent of XY rotation. This avoids stale matrix_world false negatives.
    if obj.type != 'MESH' or not obj.data.vertices:
        return obj.location.z
    return obj.location.z + min(v.co.z for v in obj.data.vertices)

# Furniture must sit exactly on finished paving, never below it.
for o in COL_PREVIEW.objects:
    if o.name.startswith("PLZT_Lamp_") or o.name.startswith("PLZT_Bench_"):
        mz=furniture_world_min_z(o)
        if mz < PAV_H-0.015:
            qa_errors.append(f"{o.name} penetrates below finished paving: minZ={mz:.4f}m")

# Explicit support diagnostics so a failure is immediately understandable.
_bench_preview = next((o for o in COL_PREVIEW.objects if o.name == "PLZT_Bench_0"), None)
_lamp_preview = next((o for o in COL_PREVIEW.objects if o.name == "PLZT_Lamp_0"), None)
if _bench_preview:
    print("V6_DIAG_BENCH0_LOCATION_Z={:.4f}".format(_bench_preview.location.z))
    print("V6_DIAG_BENCH0_MIN_Z={:.4f}".format(furniture_world_min_z(_bench_preview)))
if _lamp_preview:
    print("V6_DIAG_LAMP0_LOCATION_Z={:.4f}".format(_lamp_preview.location.z))
    print("V6_DIAG_LAMP0_MIN_Z={:.4f}".format(furniture_world_min_z(_lamp_preview)))

# Garden/civic clearance: the fountain/civic ring cannot collide with garden borders.
required_garden_center_clearance = CENTER_CIVIC_R + 0.70
for tag,poly in garden_polys.items():
    d=min_poly_distance_from_origin(poly)
    if d < required_garden_center_clearance:
        qa_errors.append(
            f"Garden {tag} too close to central civic ring: {d:.3f}m < {required_garden_center_clearance:.3f}m"
        )

# Benches: on perimeter promenade, outside gardens, off principal axes, ordered symmetrically.
for i,(x,y,yaw) in enumerate(bench_layout):
    if not on_perimeter_promenade(x,y):
        qa_errors.append(f"PLZT_Bench_{i} is not on perimeter promenade")
    for tag,poly in garden_polys.items():
        if point_in_poly(x,y,poly):
            qa_errors.append(f"PLZT_Bench_{i} located inside garden {tag}")
    if abs(y) <= MAIN_W/2 and abs(x) < inner_w/2:
        qa_errors.append(f"PLZT_Bench_{i} invades east-west main axis")
    if abs(x) <= MAIN_W/2 and abs(y) < inner_h/2:
        qa_errors.append(f"PLZT_Bench_{i} invades north-south main axis")

# Lamps: only on SIDE zones of perimeter promenade, never in gardens or cardinal path center.
for i,(x,y,yaw) in enumerate(lamp_layout):
    if not on_perimeter_promenade(x,y):
        qa_errors.append(f"PLZT_Lamp_{i} is not on perimeter promenade")
    for tag,poly in garden_polys.items():
        if point_in_poly(x,y,poly):
            qa_errors.append(f"PLZT_Lamp_{i} located inside garden {tag}")
    if abs(y) <= MAIN_W/2 and abs(x) < inner_w/2:
        qa_errors.append(f"PLZT_Lamp_{i} invades east-west main axis")
    if abs(x) <= MAIN_W/2 and abs(y) < inner_h/2:
        qa_errors.append(f"PLZT_Lamp_{i} invades north-south main axis")

# Bench/lamp separation.
for bi,(bx,by,_) in enumerate(bench_layout):
    for li,(lx,ly,_) in enumerate(lamp_layout):
        if math.hypot(bx-lx,by-ly) < 2.0:
            qa_errors.append(f"PLZT_Bench_{bi} too close to PLZT_Lamp_{li}")

# Fountain/civic proportions.
central_clear_ring = CENTER_CIVIC_R - FOUNTAIN_OUTER_R
if central_clear_ring < 2.80:
    qa_errors.append(f"Central clear ring too narrow: {central_clear_ring:.3f}m")

if qa_errors:
    raise RuntimeError("APPROVED_MASTER_QA_FAILED | " + " | ".join(qa_errors))

with open(os.path.join(OUT,"PlazaTarata_layout.json"),"w",encoding="utf-8") as f:
    json.dump(layout,f,indent=2,ensure_ascii=False)

# ---------------------------------------------------------------------------
# EXPORT HELPERS
# ---------------------------------------------------------------------------
def export_collection_fbx(col, filename, include_hidden=True):
    bpy.ops.object.select_all(action='DESELECT')
    objs=list(col.objects)
    for o in objs:
        o.hide_set(False)
        o.hide_viewport=False
        o.select_set(True)
    if not objs:
        return
    bpy.context.view_layer.objects.active=objs[0]
    # Apply modifiers by exporting evaluated result. FBX exporter handles them;
    # use_selection limits export to this logical asset.
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(OUT,filename),
        use_selection=True,
        object_types={'MESH','EMPTY'},
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_space_transform=False,
        add_leaf_bones=False,
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        path_mode='AUTO',
    )
    bpy.ops.object.select_all(action='DESELECT')

# Hide preview instances before asset master exports
for o in COL_PREVIEW.objects:
    o.hide_viewport=True
    o.hide_render=True

export_collection_fbx(COL_HARDSCAPE,"SM_PLZT_Hardscape.fbx")
export_collection_fbx(COL_GARDENS,"SM_PLZT_GardenArchitecture.fbx")
export_collection_fbx(COL_FOUNTAIN,"SM_PLZT_CentralFountain.fbx")
export_collection_fbx(COL_BENCH_MASTER,"SM_PLZT_Bench.fbx")
export_collection_fbx(COL_LAMP_MASTER,"SM_PLZT_ColonialLamp.fbx")
export_collection_fbx(COL_FENCE,"SM_PLZT_GardenFence.fbx")

# Restore preview for saved .blend
for o in COL_PREVIEW.objects:
    o.hide_viewport=False
    o.hide_render=False
bench_master.hide_viewport=True; bench_master.hide_render=True
lamp_master.hide_viewport=True; lamp_master.hide_render=True
fence_master.hide_viewport=True; fence_master.hide_render=True

# Save master blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,"JWN_PlazaTarata_Master.blend"))

print("JWN_PLAZA_BLENDER_BUILD=SUCCESS_V6_ARCHITECTURAL_QA")
print("OUTPUT="+OUT)
print("BENCHES=8")
print("LAMPS=8")
print("PALM_MARKERS=8")
print("SHADE_TREE_MARKERS=8")
print("FOUNTAIN=1")
print("PERIMETER_PROMENADE=COMPLETE")
print("FURNITURE_PIVOTS=GROUND_NORMALIZED")
print("BENCHES_INSIDE_GARDENS=0")
print("BENCHES_ON_MAIN_AXES=0")
print("LAMPS_ON_MAIN_AXES=0")
print("CENTRAL_CLEAR_RING_M=2.95")
print("LAMPS_BELOW_PLAZA=0")
print("QA_MATRIX_REFRESH=YES")
print("FURNITURE_SUPPORT_TEST=PASS")
print("BENCHES_ON_PERIMETER_PROMENADE=8")
print("LAMPS_ON_PERIMETER_SIDES=8")
print("GARDEN_CIVIC_CLEARANCE_MIN_M>=6.30")
print("FOUNTAIN_TOUCHES_GARDEN_BORDERS=0")
