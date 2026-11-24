# 420_blender_relieve_colinas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (BLENDER headless) generar el RELIEVE del bosque como mosaicos de malla de 50 x 50 m
#   (resolucion 2 m) a partir de la mascara de 419:
#   - bloqueado = NavMesh (caminos/plaza/interiores) + estructuras + 3 m alrededor de las PIRCAS de
#     los campos + 14 m alrededor de cada leyenda/aparicion (no se entierran criaturas ni neblina)
#   - distancia a lo bloqueado (transformada de distancia chamfer) -> rampa suave: plano hasta 2 m,
#     colina completa desde 11 m (los caminos nunca se tocan)
#   - altura = rampa * ruido fractal (longitud de onda ~30 m) * 2.2 m, SOLO hacia arriba (nunca
#     hunde el piso -> ningun arbol queda flotando)
#   - UV identicas a la cara superior del cubo del piso (misma textura y alineacion)
#   - solo se emiten celdas con altura > 1 cm (sin z-fighting con el piso plano)
#   Salidas: Saved/Models/relieve/RLV_<i>_<j>.fbx y Saved/ClaudeBackups/relieve_heights.json
import bpy, bmesh, json, math, os
from mathutils import Vector, noise
MASK = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_mask.json"
OUTD = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/relieve"
OUTH = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/relieve_heights.json"
os.makedirs(OUTD, exist_ok=True)
for f in os.listdir(OUTD):
    if f.startswith("RLV_") and f.endswith(".fbx"):
        os.remove(os.path.join(OUTD, f))
M = json.load(open(MASK))
X0, Y0, S, NX, NY = M["x0"], M["y0"], M["step"], M["nx"], M["ny"]
GZ = -5.0           # cara superior del piso (cm)
AMP = 220.0         # cm
TILE = 25           # celdas por mosaico (50 m)
LEG_PREFIX = ("Cria_", "Snd_App_", "Trig_Conv_", "Trig_Hac_", "Narr_Conv_", "Narr_Hac_Duende", "Narr_Plz_Duende")
blocked = [[1 if (M["nav"][j][i] or M["struct"][j][i]) else 0 for i in range(NX)] for j in range(NY)]
def stamp(px, py, r):
    i0 = max(0, int((px - r - X0) // S)); i1 = min(NX - 1, int((px + r - X0) // S) + 1)
    j0 = max(0, int((py - r - Y0) // S)); j1 = min(NY - 1, int((py + r - Y0) // S) + 1)
    for j in range(j0, j1 + 1):
        for i in range(i0, i1 + 1):
            if math.hypot(X0 + i * S - px, Y0 + j * S - py) <= r:
                blocked[j][i] = 1
for x, y in M["fences"]:   # v3: solo las pircas necesitan suelo plano; la vegetacion de campos se acomoda encima
    stamp(x, y, 300)
for lb, x, y in M["legend_pts"]:
    if lb.startswith(LEG_PREFIX):
        stamp(x, y, 1400)
# v5 (2026-11-24, pedido de la usuaria: "los relieves afectaron el escenario"): el PUEBLO queda plano.
#   Discos planos alrededor de plaza, templo, convento y hacienda (incluye jardines y bordes que no
#   son NavMesh) -> el relieve vive solo en el bosque de las afueras.
for px, py, pr in ((0, -1000, 3600), (0, 11500, 2600), (6000, 4800, 3200), (-7000, -2300, 3400)):
    stamp(px, py, pr)
# transformada de distancia chamfer (3-4) en celdas -> metros
INF = 10 ** 9
d = [[0 if blocked[j][i] else INF for i in range(NX)] for j in range(NY)]
for j in range(NY):
    for i in range(NX):
        v = d[j][i]
        if i > 0: v = min(v, d[j][i - 1] + 3)
        if j > 0:
            v = min(v, d[j - 1][i] + 3)
            if i > 0: v = min(v, d[j - 1][i - 1] + 4)
            if i < NX - 1: v = min(v, d[j - 1][i + 1] + 4)
        d[j][i] = v
for j in range(NY - 1, -1, -1):
    for i in range(NX - 1, -1, -1):
        v = d[j][i]
        if i < NX - 1: v = min(v, d[j][i + 1] + 3)
        if j < NY - 1:
            v = min(v, d[j + 1][i] + 3)
            if i < NX - 1: v = min(v, d[j + 1][i + 1] + 4)
            if i > 0: v = min(v, d[j + 1][i - 1] + 4)
        d[j][i] = v
def smooth(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
H = [[0.0] * NX for _ in range(NY)]
for j in range(NY):
    for i in range(NX):
        dm = d[j][i] / 3.0 * (S / 100.0)  # metros
        ramp = smooth((dm - 8.0) / 14.0)   # v5: plano hasta 8 m de senderos/estructuras, loma completa desde 22 m
        if ramp <= 0:
            continue
        x = X0 + i * S; y = Y0 + j * S
        n = noise.fractal(Vector((x / 3000.0, y / 3000.0, 0.37)), 1.0, 2.0, 4)
        n2 = noise.noise(Vector((x / 800.0, y / 800.0, 4.1)))
        hn = smooth((0.5 + 0.5 * n - 0.12) / 0.62)
        H[j][i] = round(ramp * (AMP * hn + 35.0 * (0.5 + 0.5 * n2)), 1)
json.dump({"x0": X0, "y0": Y0, "step": S, "nx": NX, "ny": NY, "gz": GZ, "h": H}, open(OUTH, "w"))

def uvof(x, y):
    u = (x - 160.0) / 70000.0 + 0.5
    v = y / 50000.0 + 0.5
    return (u, 1.0 - v)   # V se invierte al pasar a UE
report = {"tiles": [], "tris": 0}
for tj in range(0, NY - 1, TILE):
    for ti in range(0, NX - 1, TILE):
        quads = []
        for j in range(tj, min(tj + TILE, NY - 1)):
            for i in range(ti, min(ti + TILE, NX - 1)):
                if max(H[j][i], H[j][i + 1], H[j + 1][i], H[j + 1][i + 1]) > 1.0:
                    quads.append((i, j))
        if len(quads) < 4:
            continue
        cx = X0 + (ti + TILE / 2) * S; cy = Y0 + (tj + TILE / 2) * S
        bpy.ops.wm.read_factory_settings(use_empty=True)
        me = bpy.data.meshes.new("RLV"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap")
        vmap = {}
        def vert(i, j):
            if (i, j) not in vmap:
                h = H[j][i]
                z = GZ + (h if h > 1.0 else -4.0)
                # v6: el FBX Blender->UE invierte Y (y_ue = -y_blender; comprobado con las puertas 427).
                #      Antes los mosaicos quedaban EN ESPEJO norte-sur (lomas dentro del templo/hacienda).
                vmap[(i, j)] = bm.verts.new(((X0 + i * S - cx) / 100.0, -(Y0 + j * S - cy) / 100.0, z / 100.0))
            return vmap[(i, j)]
        for i, j in quads:
            vs = [vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)]
            f = bm.faces.new(vs)
            for lp, (a, b) in zip(f.loops, ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))):
                lp[uvl].uv = uvof(X0 + a * S, Y0 + b * S)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])   # v6: Y negado -> invertir el orden para que las caras miren arriba
        bm.verts.index_update(); bm.verts.ensure_lookup_table()
        keys = list(vmap.keys())
        bm.to_mesh(me)
        # v4: normales del terreno COMPLETO (diferencias centrales sobre la grilla global) -> sin costura entre mosaicos
        def hg(i, j):
            i = max(0, min(NX - 1, i)); j = max(0, min(NY - 1, j))
            h = H[j][i]; return h if h > 1.0 else -4.0
        vnorm = [None] * len(me.vertices)
        for k, (i, j) in enumerate(keys):
            dx = (hg(i + 1, j) - hg(i - 1, j)) / (2.0 * S); dy = (hg(i, j + 1) - hg(i, j - 1)) / (2.0 * S)
            vnorm[vmap[(i, j)].index] = Vector((-dx, dy, 1.0)).normalized()   # v6: componente Y en espacio Blender (negado)
        bm.free()
        me.normals_split_custom_set_from_vertices(vnorm)
        name = "RLV_%02d_%02d" % (ti // TILE, tj // TILE)
        ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
        for p in me.polygons:
            p.use_smooth = True
        bpy.context.view_layer.objects.active = ob; ob.select_set(True)
        out = os.path.join(OUTD, name + ".fbx")
        bpy.ops.export_scene.fbx(filepath=out, use_selection=True, apply_unit_scale=True, axis_forward='-Y', axis_up='Z',
                                 bake_space_transform=True, mesh_smooth_type='FACE', path_mode='STRIP')
        nt = len(me.polygons)
        report["tiles"].append([name, round(cx), round(cy), nt]); report["tris"] += nt
report["max_h"] = max(max(r) for r in H)
report["cells_with_h"] = sum(1 for r in H for v in r if v > 1.0)
json.dump(report, open(os.path.join(OUTD, "report.json"), "w"))
print("RELIEVE OK", len(report["tiles"]), report["tris"])


