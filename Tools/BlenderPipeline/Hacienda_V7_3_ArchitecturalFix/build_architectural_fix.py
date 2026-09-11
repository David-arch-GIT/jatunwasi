import bpy, bmesh, json, math, os, shutil, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'Hacienda_V7' / 'JW_Hacienda_Mayorazgo_V7.blend'
WORK_BLEND = ROOT / 'JW_Hacienda_Mayorazgo_V7_3_ArchitecturalFix.blend'
FOUNDATION_FBX = ROOT / 'EXP_Foundation_Floors_ArchitecturalFix.fbx'
CONNECTOR_FBX = ROOT / 'SM_HACV7_UpperLandingConnector_ArchitecturalFix.fbx'
APRON_FBX = ROOT / 'SM_HACV7_EntranceApron_ArchitecturalFix.fbx'
UPPER_WALL_FBX = ROOT / 'EXP_ExteriorWalls_Upper_ArchitecturalFix.fbx'
STAIR_FBX = ROOT / 'EXP_Staircase_ArchitecturalFix.fbx'
ROOFTRIM_FBX = ROOT / 'EXP_RoofTrim_ArchitecturalFix.fbx'
LOG = ROOT / 'architectural_fix_build.log'
AUDIT = ROOT / 'architectural_fix_audit.json'

lines=[]
def log(s):
    print(s); lines.append(str(s))

def export_selected(path):
    bpy.ops.export_scene.fbx(filepath=str(path), use_selection=True, object_types={'MESH'},
        axis_forward='-Y', axis_up='Z', global_scale=1.0, apply_unit_scale=False,
        apply_scale_options='FBX_SCALE_NONE', use_mesh_modifiers=True,
        mesh_smooth_type='FACE', use_triangles=True, add_leaf_bones=False,
        path_mode='AUTO')

def duplicate_join(name, sources, collection):
    bpy.ops.object.select_all(action='DESELECT'); copies=[]
    for src in sources:
        cp=src.copy(); cp.data=src.data.copy(); collection.objects.link(cp)
        cp.matrix_world=src.matrix_world.copy(); cp.select_set(True); copies.append(cp)
    bpy.context.view_layer.objects.active=copies[0]
    bpy.ops.object.join()
    obj=bpy.context.object; obj.name=name; obj.data.name=name+'_Mesh'
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    return obj

def box(name, dims, loc, mat, col, bevel=0.0, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Architectural edge finish','BEVEL'); m.width=bevel; m.segments=2
        bpy.context.view_layer.objects.active=o; o.select_set(True); bpy.ops.object.modifier_apply(modifier=m.name)
    return o

def uv2(obj):
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=0.025)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.uv_layers.active.name='UV0'
    dst=obj.data.uv_layers.new(name='UV1')
    for i,v in enumerate(obj.data.uv_layers['UV0'].data): dst.data[i].uv=v.uv

def audit(obj):
    bm=bmesh.new(); bm.from_mesh(obj.data)
    out={'triangles':sum(max(0,len(f.verts)-2) for f in bm.faces),
         'open_boundaries':sum(e.is_boundary for e in bm.edges),
         'non_manifold':sum(not e.is_manifold for e in bm.edges),
         'uv_channels':len(obj.data.uv_layers),
         'materials':[m.name if m else None for m in obj.data.materials]}
    bm.free(); return out

try:
    ROOT.mkdir(parents=True,exist_ok=True)
    shutil.copy2(SOURCE,WORK_BLEND)
    bpy.ops.wm.open_mainfile(filepath=str(WORK_BLEND))

    # Rebuild only the Foundation/Floors export group. SITE_FacadePath was the
    # obsolete 5.2 x 10 m platform embedded in the production mesh.
    src=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name.startswith('EXP_'): continue
        n=o.name
        selected=n.startswith(('ARCH_Foundation','ARCH_GroundFloors','ARCH_UpperFloors','SITE_')) or 'Courtyard_' in n
        if selected and n!='SITE_FacadePath': src.append(o)
    if not src: raise RuntimeError('No Foundation/Floors source objects found')
    col=bpy.data.collections.new('ARCHFIX_FOUNDATION_EXPORT'); bpy.context.scene.collection.children.link(col)
    foundation=duplicate_join('EXP_Foundation_Floors',src,col)
    bpy.ops.object.select_all(action='DESELECT'); foundation.select_set(True); bpy.context.view_layer.objects.active=foundation
    export_selected(FOUNDATION_FBX)
    foundation_audit=audit(foundation)
    log('Removed embedded source object: SITE_FacadePath')

    # Replace the court-facing solid panel at connector centre X=-5.30 m with
    # two jambs and a closed lintel, producing a 2.00 m architectural doorway.
    wall_src=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name.startswith('EXP_'): continue
        if 'ExteriorWalls' in o.name and '_U' in o.name and o.name!='ARCH_ExteriorWalls_Court_U_04': wall_src.append(o)
    plaster=bpy.data.materials.get('MAT_Lime_Plaster_Exterior')
    wcol=bpy.data.collections.new('ARCHFIX_UPPER_WALL_EXPORT');bpy.context.scene.collection.children.link(wcol)
    # Original panel bounds: X -7.425..-3.575, Y -8.275..-7.725, Z 3.9..7.1.
    wall_src += [
        box('ARCHFIX_ConnectorJamb_Left',(1.125,.55,3.20),(-6.8625,-8.0,5.50),plaster,wcol),
        box('ARCHFIX_ConnectorJamb_Right',(.725,.55,3.20),(-3.9375,-8.0,5.50),plaster,wcol),
        box('ARCHFIX_ConnectorLintel',(2.00,.55,.75),(-5.30,-8.0,6.725),plaster,wcol)]
    upper_wall=duplicate_join('EXP_ExteriorWalls_Upper_V07Fix',wall_src,wcol)
    bpy.ops.object.select_all(action='DESELECT');upper_wall.select_set(True);bpy.context.view_layer.objects.active=upper_wall
    export_selected(UPPER_WALL_FBX);upper_wall_audit=audit(upper_wall)

    # Functional 23-step stair: 150 cm clear width, 29 cm tread, 16.95 cm
    # rise, thin masonry treads on two timber stringers, and one guard only on
    # the exposed edge. This replaces the prior stack of full-height blocks.
    scol=bpy.data.collections.new('ARCHFIX_STAIR_EXPORT');bpy.context.scene.collection.children.link(scol)
    stonefloor=bpy.data.materials.get('MAT_Stone_Floor');woodmat=bpy.data.materials.get('MAT_Dark_Wood')
    stair=[]; tread=.29; rise=3.90/23.0; x0=-5.70
    for i in range(23):
        y=5.855-i*tread; top=(i+1)*rise
        stair.append(box(f'Stair_Tread_{i:02d}',(1.50,.305,.18),(x0,y,top-.09),stonefloor,scol,.006))
    # Upper landing aligns with the existing 4.00 m corridor datum.
    stair.append(box('Stair_UpperLanding',(1.50,1.65,.20),(x0,-1.45,3.90),stonefloor,scol,.008))
    ang=-math.atan2(3.90,23*tread)
    run=math.sqrt((23*tread)**2+3.90**2)
    for x in (-6.25,-5.15):
        stair.append(box('Stair_Stringer',(.14,run,.22),(x,2.665,1.78),woodmat,scol,.008,(ang,0,0)))
    # Exposed-edge posts and continuous handrail; wall side stays clear.
    edge_x=-6.38
    for i in range(0,23,2):
        y=5.855-i*tread; z=(i+1)*rise
        stair.append(box('Stair_GuardPost',(.07,.07,1.02),(edge_x,y,z+.51),woodmat,scol,.006))
    stair.append(box('Stair_Handrail',(.10,run,.10),(edge_x,2.665,2.90),woodmat,scol,.01,(ang,0,0)))
    # Landing guard protects only the open outer edge and leaves connector clear.
    for y in (-2.15,-1.80,-1.45,-1.10,-.75):
        stair.append(box('Landing_GuardPost',(.07,.07,1.02),(edge_x,y,4.51),woodmat,scol,.006))
    stair.append(box('Landing_Handrail',(.10,1.52,.10),(edge_x,-1.45,4.95),woodmat,scol,.01))
    bpy.ops.object.select_all(action='DESELECT')
    for o in stair:o.select_set(True)
    bpy.context.view_layer.objects.active=stair[0];bpy.ops.object.join();stair_obj=bpy.context.object
    stair_obj.name='EXP_Staircase_V07Fix';stair_obj.data.name=stair_obj.name+'_Mesh';bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);uv2(stair_obj)
    bpy.ops.object.select_all(action='DESELECT');stair_obj.select_set(True);bpy.context.view_layer.objects.active=stair_obj
    export_selected(STAIR_FBX);stair_audit=audit(stair_obj)

    # Clean roof finishing system: continuous ridges, gable closures and eaves
    # only. Remove the many short valley-channel and decorative edge fragments
    # that produced floating/intersecting patch geometry in UE.
    rtcol=bpy.data.collections.new('ARCHFIX_ROOFTRIM_EXPORT');bpy.context.scene.collection.children.link(rtcol)
    rooftrim_src=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name.startswith('EXP_'):continue
        n=o.name
        if n.startswith(('ARCH_Roof_Ridges','ARCH_GableClosures','ARCH_Eaves')):
            rooftrim_src.append(o)
    rooftrim=duplicate_join('EXP_RoofTrim_V07Fix',rooftrim_src,rtcol)
    bpy.ops.object.select_all(action='DESELECT');rooftrim.select_set(True);bpy.context.view_layer.objects.active=rooftrim
    export_selected(ROOFTRIM_FBX);rooftrim_audit=audit(rooftrim)

    # Build a closed colonial connector at the original asset coordinates.
    bpy.ops.object.select_all(action='DESELECT')
    ccol=bpy.data.collections.new('ARCHFIX_CONNECTOR_EXPORT'); bpy.context.scene.collection.children.link(ccol)
    wood=bpy.data.materials.get('MAT_Dark_Wood') or bpy.data.materials.new('MAT_Dark_Wood')
    brick=bpy.data.materials.get('MAT_Brick_Floor') or bpy.data.materials.new('MAT_Brick_Floor')
    length=2.1940184878; width=1.70; z0=4.365; slope=math.atan2(4.32-4.41,length)
    parts=[]
    slab=box('Connector_Floor',(width,length,.18),(0,0,z0-.09),brick,ccol,.012,(slope,0,0)); parts.append(slab)
    # Structural frame below the walkable surface.
    for x in (-.62,.62): parts.append(box('Connector_Stringer',(.13,length+.08,.20),(x,0,z0-.25),wood,ccol,.01,(slope,0,0)))
    for y in (-.92,-.46,0,.46,.92): parts.append(box('Connector_Joist',(width+.08,.11,.15),(0,y,z0-.22+math.tan(slope)*y),wood,ccol,.008,(slope,0,0)))
    # Rails stop short of both joins, leaving clean full-width entries.
    rail_len=length-.34; rail_h=1.02
    for side in (-1,1):
        x=side*(width/2-.045)
        parts.append(box('Connector_Handrail',(.10,rail_len,.10),(x,0,z0+rail_h),wood,ccol,.012,(slope,0,0)))
        parts.append(box('Connector_LowerRail',(.075,rail_len,.075),(x,0,z0+.43),wood,ccol,.008,(slope,0,0)))
        for i in range(13):
            y=-rail_len/2+i*rail_len/12
            parts.append(box('Connector_Baluster',(.055,.055,rail_h),(x,y,z0+rail_h/2+math.tan(slope)*y),wood,ccol,.006))
        for y in (-rail_len/2,rail_len/2):
            parts.append(box('Connector_EndPost',(.11,.11,rail_h+.06),(x,y,z0+(rail_h+.06)/2+math.tan(slope)*y),wood,ccol,.01))
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active=slab; bpy.ops.object.join()
    connector=bpy.context.object; connector.name='SM_HACV7_UpperLandingConnector'; connector.data.name=connector.name+'_Mesh'
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True); uv2(connector)
    # UCX floor and side guards are exported with the visible mesh.
    ucx=[]
    ucx.append(box('UCX_SM_HACV7_UpperLandingConnector_00',(width-.06,length,.18),(0,0,z0-.09),brick,ccol,0,(slope,0,0)))
    for side,idx in ((-1,1),(1,2)):
        ucx.append(box(f'UCX_SM_HACV7_UpperLandingConnector_0{idx}',(.08,rail_len,rail_h),(side*(width/2-.045),0,z0+rail_h/2),wood,ccol,0,(slope,0,0)))
    bpy.ops.object.select_all(action='DESELECT'); connector.select_set(True)
    for o in ucx:o.select_set(True)
    bpy.context.view_layer.objects.active=connector; export_selected(CONNECTOR_FBX)
    connector_audit=audit(connector)

    # Closed single-piece entrance apron. Coordinates are metres relative to
    # the existing V07 actor; three overlapping solids are Boolean-unioned so
    # the top is rendered from native Blender cube faces, with no central seam.
    acol=bpy.data.collections.new('ARCHFIX_APRON_EXPORT'); bpy.context.scene.collection.children.link(acol)
    lower=box('Apron_LowerLanding',(4.75,.52,.27),(0,-3.05,-.165),brick,acol)
    dy=3.05; dz=.62; ang=math.atan2(dz,dy); run=math.sqrt(dy*dy+dz*dz)
    # Midpoint of the top plane minus 15 cm along its outward normal.
    slope=box('Apron_ContinuousSlope',(4.75,run+.04,.30),(0,-1.275+math.sin(ang)*.15,.28-math.cos(ang)*.15),brick,acol,0,(ang,0,0))
    upper=box('Apron_PortalLanding',(4.75,9.77,.88),(0,5.125,.15),brick,acol)
    apron=lower
    for operand in (slope,upper):
        bpy.context.view_layer.objects.active=apron
        mod=apron.modifiers.new('Architectural solid union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=operand
        bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(operand,do_unlink=True)
    apron.name='SM_HACV7_EntranceApron_Final_V07Fix';apron.data.name=apron.name+'_Mesh'
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bm=bmesh.new();bm.from_mesh(apron.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(apron.data);bm.free();uv2(apron)
    ucx=apron.copy();ucx.data=apron.data.copy();ucx.name='UCX_SM_HACV7_EntranceApron_Final_V07Fix_00';acol.objects.link(ucx)
    bpy.ops.object.select_all(action='DESELECT');apron.select_set(True);ucx.select_set(True);bpy.context.view_layer.objects.active=apron
    export_selected(APRON_FBX); apron_audit=audit(apron)

    bpy.ops.wm.save_as_mainfile(filepath=str(WORK_BLEND),check_existing=False)
    data={'status':'PASS','source':str(SOURCE),'source_removed':['SITE_FacadePath'],
          'foundation':foundation_audit,'upper_wall':upper_wall_audit,'stair':stair_audit,'rooftrim':rooftrim_audit,'connector':connector_audit,'apron':apron_audit,
          'outputs':[str(FOUNDATION_FBX),str(UPPER_WALL_FBX),str(STAIR_FBX),str(ROOFTRIM_FBX),str(CONNECTOR_FBX),str(APRON_FBX)]}
    AUDIT.write_text(json.dumps(data,indent=2),encoding='utf-8')
    log(json.dumps(data,indent=2))
except Exception:
    log(traceback.format_exc()); raise
finally:
    LOG.write_text('\n'.join(lines),encoding='utf-8')
