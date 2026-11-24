# 426_blender_puertas_procesar.py  (v2 2026-11-24)
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (BLENDER headless) GATE de las 3 puertas Tripo (templo/convento/hacienda, ~70k tris,
#   bloques macizos de hasta 1 m de grosor). Para cada una:
#   1) CAPA VISIBLE DESDE EL FRENTE (rayos hacia -Y por cara; v1 usaba un umbral de profundidad y
#      perdia las hojas, que estan hundidas respecto del marco) + corte trasero limpio (426c)
#   2) escala UNIFORME al vano real medido en el mapa (424/425): templo 4.00x4.85 (portada sobre la
#      fachada), hacienda 2.50x2.75 (dentro del vano), convento 2 vanos 1.20x2.60 (hoja + montante)
#   3) marco y hojas separados con cortes de plano (arco del templo = 16 planos tangentes)
#   4) relieve aplanado por pieza a medidas reales + SOLIDIFY con borde cerrado
#   5) decimate por pieza (presupuesto Quest), ORIGEN DE CADA HOJA EN SU BISAGRA (cara trasera)
#   6) FBX por pieza + textura base (bytes originales) + render de verificacion con hojas abiertas
#   Presupuesto (tras solidify ~x2): templo ~37k, hacienda ~25k, convento ~15k por vano.
#   Coordenadas Blender: cara exterior del muro en y=0, frente de la puerta hacia -Y, interior +Y.
import bpy, bmesh, json, math, os, traceback
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
SRC = r"C:/Users/Mi PC/Desktop/puertas tripoia/"
OUTD = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/puertas/"
os.makedirs(OUTD, exist_ok=True)
for f in os.listdir(OUTD):
    if f.endswith(".fbx") or f.startswith("check_"):
        os.remove(OUTD + f)
REP = {}

def load(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=SRC + "puerta " + name + ".glb")
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in ms: o.select_set(True)
    bpy.context.view_layer.objects.active = ms[0]
    if len(ms) > 1: bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for im in bpy.data.images:
        if "basecolor" in im.name.lower() and im.packed_file:
            ext = ".png" if im.packed_file.data[:4] == b"\x89PNG" else ".jpg"
            open(OUTD + "T_Puerta_%s_BC%s" % (name.capitalize(), ext), "wb").write(im.packed_file.data)
    mat = ob.data.materials[0] if ob.data.materials else None
    ob.hide_render = True
    return ob, mat

def visible_shell(ob, y_cut):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0003)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    d = Vector((0, -1, 0)); kill = []
    for f in bm.faces:
        c = f.calc_center_median()
        probes = [c] + [c + (v.co - c) * 0.7 for v in f.verts]
        if all(tree.ray_cast(p + Vector((0, -0.02, 0)), d)[0] is not None for p in probes):
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    g = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=g, dist=1e-6, plane_co=Vector((0, y_cut, 0)), plane_no=Vector((0, 1, 0)))
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().y > y_cut], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    return bm

def cut(bm, planes):
    for co, no in planes:
        g = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=g, dist=1e-6, plane_co=Vector(co), plane_no=Vector(no))

def subset(bm, keep):
    b2 = bm.copy()
    bmesh.ops.delete(b2, geom=[f for f in b2.faces if not keep(f.calc_center_median())], context='FACES')
    bmesh.ops.delete(b2, geom=[v for v in b2.verts if not v.link_faces], context='VERTS')
    return b2

def make_part(bm, name, mat, target_tris, thickness, F, yref, mirror=False):
    for v in bm.verts:
        v.co.y = yref + (v.co.y - yref) * F
        if mirror: v.co.x = -v.co.x
    if mirror: bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    if mat: me.materials.append(mat)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    me.calc_loop_triangles(); n = len(me.loop_triangles)
    if n > target_tris:
        m = ob.modifiers.new("dec", 'DECIMATE'); m.decimate_type = 'COLLAPSE'; m.ratio = target_tris / float(n)
        bpy.ops.object.modifier_apply(modifier="dec")
    sd = ob.modifiers.new("sol", 'SOLIDIFY'); sd.thickness = thickness; sd.offset = -1.0; sd.use_rim = True; sd.use_even_offset = False
    bpy.ops.object.modifier_apply(modifier="sol")
    for p in me.polygons: p.use_smooth = True
    return ob

def move(ob, dx, dy, dz):
    for v in ob.data.vertices: v.co += Vector((dx, dy, dz))

def bounds(ob):
    vs = [v.co for v in ob.data.vertices]
    return Vector([min(v[i] for v in vs) for i in range(3)]), Vector([max(v[i] for v in vs) for i in range(3)])

def export(ob):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=OUTD + ob.name + ".fbx", use_selection=True, apply_unit_scale=True, axis_forward='-Y', axis_up='Z',
                             bake_space_transform=True, mesh_smooth_type='FACE', path_mode='STRIP')
    ob.data.calc_loop_triangles(); mn, mx = bounds(ob)
    return {"tris": len(ob.data.loop_triangles), "min": [round(v, 3) for v in mn], "max": [round(v, 3) for v in mx]}

def render_check(parts, fname):
    # parts: (obj, pivot, angulo) -> hojas abiertas hacia el interior (+Y)
    scn = bpy.context.scene
    for ob, piv, ang in parts:
        ob.matrix_world = Matrix.Translation(Vector(piv)) @ Matrix.Rotation(math.radians(ang), 4, 'Z') @ Matrix.Translation(-Vector(piv))
    allv = [ob.matrix_world @ v.co for ob, _, _ in parts for v in ob.data.vertices]
    mn = Vector([min(v[i] for v in allv) for i in range(3)]); mx = Vector([max(v[i] for v in allv) for i in range(3)])
    c = (mn + mx) / 2; sz = max(mx - mn)
    scn.render.engine = 'BLENDER_WORKBENCH'; scn.display.shading.light = 'STUDIO'; scn.display.shading.color_type = 'TEXTURE'
    scn.render.resolution_x = 900; scn.render.resolution_y = 900
    scn.world = bpy.data.worlds.new("W"); scn.world.color = (0.1, 0.1, 0.1)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scn.collection.objects.link(cam); scn.camera = cam
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = sz * 1.15; cam.data.clip_end = 500
    rot = (math.radians(72), 0, math.radians(-28)); cam.rotation_euler = rot
    fwd = Matrix.Rotation(rot[2], 3, 'Z') @ Matrix.Rotation(rot[0], 3, 'X') @ Vector((0, 0, -1))
    cam.location = c - fwd * 60
    scn.render.filepath = OUTD + fname; bpy.ops.render.render(write_still=True)
    for ob, _, _ in parts: ob.matrix_world = Matrix.Identity(4)
    bpy.data.objects.remove(cam)

# ---------------- TEMPLO: portada montada sobre la fachada ----------------
def templo():
    r = {}; ob, mat = load("templo")
    XL, ZS, YC = 24.6, 65.3, -1.0
    s = 4.78 / (ZS + XL)                           # cumbre del arco de las hojas a 4.78 m (vano 4.85)
    bm = visible_shell(ob, YC)
    for v in bm.verts: v.co *= s
    xl, zs, yc = XL * s, ZS * s, YC * s
    half = max(abs(v.co.x) for v in bm.verts); target = 2.02; a0 = 26.0 * s   # jamba exterior cubre el vano de 4.00 m
    for v in bm.verts:
        ax = abs(v.co.x)
        if ax > a0:
            v.co.x += math.copysign((target - half) * min(1.0, (ax - a0) / (half - a0)), v.co.x)
    planes = [((xl, 0, 0), (1, 0, 0)), ((-xl, 0, 0), (1, 0, 0)), ((0, 0, 0), (1, 0, 0))]
    for k in range(1, 16):
        th = math.radians(k * 180.0 / 16); n = Vector((math.cos(th), 0, math.sin(th)))
        planes.append((tuple(Vector((0, 0, zs)) + n * xl), tuple(n)))
    cut(bm, planes)
    def inside(c):
        if abs(c.x) > xl + 1e-5: return False
        return c.z <= zs or (c.x ** 2 + (c.z - zs) ** 2) ** 0.5 <= xl + 1e-4
    L = subset(bm, lambda c: inside(c) and c.x < 0); R = subset(bm, lambda c: inside(c) and c.x >= 0)
    Fr = subset(bm, lambda c: not inside(c)); bm.free()
    oF = make_part(Fr, "SM_PuertaTemplo_Marco", mat, 7000, 0.06, 0.6, yc)
    oL = make_part(L, "SM_PuertaTemplo_HojaIzq", mat, 5000, 0.05, 0.35, yc)
    oR = make_part(R, "SM_PuertaTemplo_HojaDer", mat, 5000, 0.05, 0.35, yc)
    dy = -(yc + 0.06)                              # espalda del marco = cara del muro (y=0)
    for o in (oF, oL, oR): move(o, 0, dy, 0)
    py = yc + 0.05 + dy                            # eje de bisagra: cara trasera de las hojas
    render_check([(oF, (0, 0, 0), 0), (oL, (-xl, py, 0), 60), (oR, (xl, py, 0), -60)], "check_templo.png")
    r.update({"hinge_x": round(xl, 4), "pivot_y": round(py, 4), "scale": round(s, 5)})
    move(oL, xl, -py, 0); move(oR, -xl, -py, 0)
    for o, k in ((oF, "marco"), (oL, "hojaL"), (oR, "hojaR")): r[k] = export(o)
    return r

# ---------------- HACIENDA: dentro del vano 2.50 x 2.75 ----------------
def hacienda():
    r = {}; ob, mat = load("hacienda")
    YC = -1.0; s = 2.74 / 97.775
    bm = visible_shell(ob, YC)
    for v in bm.verts: v.co *= s
    xl, zt, yc = 41.2 * s, 94.9 * s, YC * s
    cut(bm, [((xl, 0, 0), (1, 0, 0)), ((-xl, 0, 0), (1, 0, 0)), ((0, 0, 0), (1, 0, 0)), ((0, 0, zt), (0, 0, 1))])
    inside = lambda c: abs(c.x) <= xl + 1e-5 and c.z <= zt + 1e-5
    L = subset(bm, lambda c: inside(c) and c.x < 0); R = subset(bm, lambda c: inside(c) and c.x >= 0)
    Fr = subset(bm, lambda c: not inside(c)); bm.free()
    oF = make_part(Fr, "SM_PuertaHacienda_Marco", mat, 2500, 0.04, 0.8, yc)
    oL = make_part(L, "SM_PuertaHacienda_HojaIzq", mat, 4000, 0.04, 0.38, yc)
    oR = make_part(R, "SM_PuertaHacienda_HojaDer", mat, 4000, 0.04, 0.38, yc)
    dy = 0.03 - bounds(oF)[0].y                    # frente del marco 3 cm dentro del vano
    for o in (oF, oL, oR): move(o, 0, dy, 0)
    py = yc + 0.04 + dy
    render_check([(oF, (0, 0, 0), 0), (oL, (-xl, py, 0), 60), (oR, (xl, py, 0), -60)], "check_hacienda.png")
    r.update({"hinge_x": round(xl, 4), "pivot_y": round(py, 4), "scale": round(s, 5)})
    move(oL, xl, -py, 0); move(oR, -xl, -py, 0)
    for o, k in ((oF, "marco"), (oL, "hojaL"), (oR, "hojaR")): r[k] = export(o)
    return r

# ---------------- CONVENTO: 2 vanos 1.20 x 2.60 -> hoja 1.18 + montante fijo ----------------
def convento():
    r = {}; ob, mat = load("convento")
    YC = -2.5; W = 1.18; s = W / 58.188
    bm = visible_shell(ob, YC)
    for v in bm.verts: v.co *= s
    yc = YC * s
    leaf_h = max(v.co.z for v in bm.verts)
    za = 56.0 * s; zb = za + (2.60 - leaf_h - 0.005)
    tb = bm.copy(); cut(tb, [((0, 0, za), (0, 0, 1)), ((0, 0, zb), (0, 0, 1)), ((0, 0, 0), (1, 0, 0))])
    half = subset(tb, lambda c: c.x >= 0 and za <= c.z <= zb); tb.free()
    mir = half.copy()
    for v in mir.verts: v.co.x = -v.co.x
    bmesh.ops.reverse_faces(mir, faces=mir.faces[:])
    tmp = bpy.data.meshes.new("tmp"); mir.to_mesh(tmp); mir.free(); half.from_mesh(tmp)
    for v in half.verts: v.co.z += (leaf_h + 0.005) - za
    leaf2 = bm.copy()
    oT = make_part(half, "SM_PuertaConvento_Montante", mat, 2000, 0.04, 0.6, yc)
    oL = make_part(bm, "SM_PuertaConvento_HojaIzq", mat, 4500, 0.04, 0.6, yc)
    oR = make_part(leaf2, "SM_PuertaConvento_HojaDer", mat, 4500, 0.04, 0.6, yc, mirror=True)
    dy = 0.05 - bounds(oL)[0].y                    # frente de la hoja 5 cm dentro del vano (muro 52 cm)
    for o in (oT, oL, oR): move(o, 0, dy, 0)
    py = yc + 0.04 + dy; hx = W / 2
    render_check([(oT, (0, 0, 0), 0), (oL, (-hx, py, 0), 60)], "check_convento.png")
    r.update({"hinge_x": hx, "pivot_y": round(py, 4), "leaf_h": round(leaf_h, 3), "scale": round(s, 5)})
    move(oL, hx, -py, 0); move(oR, -hx, -py, 0)
    for o, k in ((oT, "montante"), (oL, "hojaL"), (oR, "hojaR")): r[k] = export(o)
    return r

for nm, fn in (("templo", templo), ("hacienda", hacienda), ("convento", convento)):
    try:
        REP[nm] = fn()
    except Exception:
        REP[nm] = {"error": traceback.format_exc()[-900:]}
json.dump(REP, open(OUTD + "report.json", "w"), indent=1)
print("PUERTAS GATE OK")
