# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace este script: (BLENDER headless) Riguea el duende T-pose (OBJ+textura) con un esqueleto humanoide, lo pesa (auto weights), y le crea un IDLE siniestro (mecerse, respirar, cabeza gira, brazos bajan y ondulan). Exporta GLB animado para UE.
# Por que se necesito: Mixamo fallaba; el usuario pidio que yo lo riguee y anime en Blender.
# Resultado obtenido: (pendiente) duende_animado.glb con esqueleto + idle.
# ------------------------------------------------------------
import bpy, math, mathutils, os
OBJ = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/duende_tpose/30acfa9f397667230ce5db62f1dbeb93.obj"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/duende_animado.glb"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
try: bpy.ops.wm.obj_import(filepath=OBJ)
except Exception: bpy.ops.import_scene.obj(filepath=OBJ)
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = mesh; mesh.select_set(True)
# limpiar + escala 1.6m + origen base + upright (Z-up)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0005); bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.shade_smooth()
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bb = [mesh.matrix_world @ mathutils.Vector(c) for c in mesh.bound_box]
minz = min(v.z for v in bb); cx = sum(v.x for v in bb)/8; cy = sum(v.y for v in bb)/8
mesh.location = (mesh.location.x - cx, mesh.location.y - cy, mesh.location.z - minz)
bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
H = mesh.dimensions.z
f = 1.6 / H if H > 0.01 else 1.0
mesh.scale = (f, f, f); bpy.ops.object.transform_apply(scale=True)
H = mesh.dimensions.z
AX = mesh.dimensions.x / 2.0  # medio arm-span

# ---- armature ----
armd = bpy.data.armatures.new("DuendeRig")
arm = bpy.data.objects.new("DuendeRig", armd)
bpy.context.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = armd.edit_bones
def bone(name, h, t, parent=None, connect=False):
    b = eb.new(name); b.head = mathutils.Vector(h); b.tail = mathutils.Vector(t)
    if parent: b.parent = parent; b.use_connect = connect
    return b
hips  = bone("hips",  (0,0,0.38*H), (0,0,0.47*H))
spine = bone("spine", (0,0,0.47*H), (0,0,0.58*H), hips, True)
chest = bone("chest", (0,0,0.58*H), (0,0,0.63*H), spine, True)
neck  = bone("neck",  (0,0,0.63*H), (0,0,0.66*H), chest, True)
head  = bone("head",  (0,0,0.66*H), (0,0,0.80*H), neck, True)
shL = bone("shoulder.L",(0.05,0,0.62*H),(0.12,0,0.62*H), chest)
uaL = bone("upperarm.L",(0.12,0,0.62*H),(0.45*AX,0,0.62*H), shL, True)
laL = bone("lowerarm.L",(0.45*AX,0,0.62*H),(0.78*AX,0,0.62*H), uaL, True)
haL = bone("hand.L",(0.78*AX,0,0.62*H),(AX,0,0.62*H), laL, True)
shR = bone("shoulder.R",(-0.05,0,0.62*H),(-0.12,0,0.62*H), chest)
uaR = bone("upperarm.R",(-0.12,0,0.62*H),(-0.45*AX,0,0.62*H), shR, True)
laR = bone("lowerarm.R",(-0.45*AX,0,0.62*H),(-0.78*AX,0,0.62*H), uaR, True)
haR = bone("hand.R",(-0.78*AX,0,0.62*H),(-AX,0,0.62*H), laR, True)
thL = bone("thigh.L",(0.10,0,0.38*H),(0.11,0,0.18*H), hips)
shnL= bone("shin.L",(0.11,0,0.18*H),(0.12,0,0.03*H), thL, True)
ftL = bone("foot.L",(0.12,0,0.03*H),(0.12,-0.10,0.0), shnL, True)
thR = bone("thigh.R",(-0.10,0,0.38*H),(-0.11,0,0.18*H), hips)
shnR= bone("shin.R",(-0.11,0,0.18*H),(-0.12,0,0.03*H), thR, True)
ftR = bone("foot.R",(-0.12,0,0.03*H),(-0.12,-0.10,0.0), shnR, True)
bpy.ops.object.mode_set(mode='OBJECT')

# pesar la malla al esqueleto (auto weights)
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

# suavizar pesos (quita el estiramiento feo de piernas/pies) + limitar influencias
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); bpy.context.view_layer.objects.active = mesh
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
try: bpy.ops.object.vertex_group_limit_total(group_select_mode='ALL', limit=4)
except Exception: pass
try: bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.6, repeat=4)
except Exception: pass
bpy.ops.object.mode_set(mode='OBJECT')

# ---- CICLO DE CAMINATA (walk cycle) ----
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
sc = bpy.context.scene
pb = arm.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
r = math.radians
CYC = 38          # frames por ciclo (mas lento = mas pesado/deliberado)
NCYC = 1
sc.frame_start = 1; sc.frame_end = CYC * NCYC
DOWN = r(66)  # bajar brazos (por eje X local, ambos mismo signo); codo doblado -> manos adelante
WALK_BONES = ["thigh.L","thigh.R","shin.L","shin.R","foot.L","foot.R","upperarm.L","upperarm.R",
              "lowerarm.L","lowerarm.R","chest","spine","hips","head","neck"]

def walk_pose(f, ph):
    s  = math.sin(2*math.pi*ph)          # pierna izq: + adelante
    so = math.sin(2*math.pi*ph + math.pi)  # pierna der: opuesta
    # muslos: zancada mas larga y deliberada
    pb["thigh.L"].rotation_euler = (r(23)*s, 0, 0)
    pb["thigh.R"].rotation_euler = (r(23)*so, 0, 0)
    # rodillas doblan al levantar el pie (fase de balanceo)
    liftL = max(0.0, math.sin(2*math.pi*ph - math.pi*0.5))
    liftR = max(0.0, math.sin(2*math.pi*ph + math.pi*0.5))
    pb["shin.L"].rotation_euler = (-r(6) - r(28)*liftL, 0, 0)
    pb["shin.R"].rotation_euler = (-r(6) - r(28)*liftR, 0, 0)
    # pies ruedan (talon-punta) en vez de ir tiesos
    pb["foot.L"].rotation_euler = (-r(16)*s,  0, 0)
    pb["foot.R"].rotation_euler = (-r(16)*so, 0, 0)
    # brazos SUELTOS: hombro columpia amplio, codo se flexiona con el vaiven (relajado)
    pb["upperarm.L"].rotation_euler = (-DOWN - r(28)*s,  0, 0)
    pb["upperarm.R"].rotation_euler = (-DOWN - r(28)*so, 0, 0)
    pb["lowerarm.L"].rotation_euler = (r(28) + r(20)*s,  0, 0)
    pb["lowerarm.R"].rotation_euler = (r(28) + r(20)*so, 0, 0)
    # torso levemente adelante; SIN bamboleo lateral de cadera (eso se veia amanerado)
    pb["chest"].rotation_euler = (r(9), 0, 0)
    pb["spine"].rotation_euler = (r(5), 0, 0)
    pb["hips"].rotation_euler = (r(4), 0, 0)      # pelvis firme adelante, sin sashay
    pb["neck"].rotation_euler = (r(2), 0, 0)      # sube la cabeza (contra-encorva)
    pb["head"].rotation_euler = (r(4), 0, 0)      # mirada al frente
    # bob leve (menos rebote)
    arm.location = (0, 0, 0.02*abs(math.sin(2*math.pi*ph)))
    for name in WALK_BONES:
        pb[name].keyframe_insert("rotation_euler", frame=f)
    arm.keyframe_insert("location", frame=f)

for f in range(1, CYC*NCYC + 1):
    walk_pose(f, ((f - 1) % CYC) / float(CYC))
bpy.ops.object.mode_set(mode='OBJECT')

# ---- render de PREVIEW (video MP4) para validar ----
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); bpy.context.collection.objects.link(cam)
cam.location = (2.7, -2.4, 1.05)
dv = mathutils.Vector((0, 0, 0.8)) - cam.location
cam.rotation_euler = dv.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", 'SUN')); bpy.context.collection.objects.link(sun)
sun.data.energy = 4.0; sun.rotation_euler = (math.radians(55), 0, math.radians(25))
sc.render.resolution_x = 360; sc.render.resolution_y = 460; sc.render.fps = 30
try: sc.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    try: sc.render.engine = 'BLENDER_EEVEE'
    except Exception: pass
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new("W") if not sc.world else sc.world
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.03, 0.05, 1)
sc.render.image_settings.file_format = 'PNG'
FR_DIR = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/duende_frames/"
os.makedirs(FR_DIR, exist_ok=True)
import glob as _g
for _f in _g.glob(FR_DIR + "*.png"): os.remove(_f)
sc.render.filepath = FR_DIR + "f_"
sc.frame_step = 1  # todos los frames (fluido)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.render.render(animation=True)

# ---- armar GIF animado (encoder LZW propio, paleta 3-3-2) ----
import numpy as np, glob
def lzw(indices, mcs=8):
    clear = 1 << mcs; end = clear + 1; cs = mcs + 1
    out = bytearray(); buf = 0; nb = 0
    def emit(code):
        nonlocal buf, nb
        buf |= code << nb; nb += cs
        while nb >= 8:
            out.append(buf & 0xFF); buf >>= 8; nb -= 8
    emit(clear); nxt = end + 1
    for idx in indices:
        emit(int(idx)); nxt += 1
        if nxt >= 511:
            emit(clear); nxt = end + 1
    emit(end)
    if nb > 0: out.append(buf & 0xFF)
    return out
def subblocks(data):
    o = bytearray(); i = 0
    while i < len(data):
        c = data[i:i+255]; o.append(len(c)); o += c; i += 255
    o.append(0); return o
files = sorted(glob.glob(FR_DIR + "f_*.png"))
GIF = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/duende_anim_preview.gif"
W = sc.render.resolution_x; Hh = sc.render.resolution_y
g = bytearray(b"GIF89a")
g += bytes([W & 0xFF, W >> 8, Hh & 0xFF, Hh >> 8, 0xF7, 0, 0])
for i in range(256):  # paleta 3-3-2
    g += bytes([((i >> 5) & 7) * 36, ((i >> 2) & 7) * 36, (i & 3) * 85])
g += bytes([0x21, 0xFF, 0x0B]) + b"NETSCAPE2.0" + bytes([0x03, 0x01, 0, 0, 0])  # loop
for fp in files:
    im = bpy.data.images.load(fp)
    w, h = im.size
    a = np.array(im.pixels[:]).reshape(h, w, 4)[::-1]  # flip vertical
    rgb = np.clip(a[:, :, :3] * 255, 0, 255).astype(np.uint8)
    idx = (((rgb[:, :, 0] >> 5) << 5) | ((rgb[:, :, 1] >> 5) << 2) | (rgb[:, :, 2] >> 6)).astype(np.uint8).flatten()
    g += bytes([0x21, 0xF9, 0x04, 0x00, 7, 0, 0x00])  # 7/100s por frame (~14fps)
    g += bytes([0x2C, 0, 0, 0, 0, w & 0xFF, w >> 8, h & 0xFF, h >> 8, 0x00])
    g += bytes([0x08]) + subblocks(lzw(idx, 8))
    bpy.data.images.remove(im)
g += bytes([0x3B])
open(GIF, "wb").write(g)
print("GIF OK", os.path.exists(GIF), len(files), "frames")

# exportar GLB (malla + esqueleto + animacion + textura)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True,
                          export_skins=True, export_apply=False)
print("RIG ANIM OK glb", round(os.path.getsize(OUT)/1024.0, 0), "kb")

# ---- REPOSO (idle) GLB separado: parado, brazos abajo quietos, respiracion leve ----
arm.animation_data_clear()
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
IB = WALK_BONES
Ni = 90; sc.frame_start = 1; sc.frame_end = Ni
for fri in range(1, Ni+1):
    br = math.sin(2*math.pi*(fri-1)/float(Ni))
    for n in IB: pb[n].rotation_euler = (0,0,0)
    pb["upperarm.L"].rotation_euler = (-DOWN,0,0); pb["upperarm.R"].rotation_euler = (-DOWN,0,0)
    pb["lowerarm.L"].rotation_euler = (r(28),0,0); pb["lowerarm.R"].rotation_euler = (r(28),0,0)
    pb["shin.L"].rotation_euler = (-r(6),0,0); pb["shin.R"].rotation_euler = (-r(6),0,0)
    pb["chest"].rotation_euler = (r(9)+r(1.2)*br, 0, r(1.5)*br)   # respiracion + mecido muy leve
    pb["spine"].rotation_euler = (r(5)+r(1)*br, 0, -r(1)*br)
    pb["hips"].rotation_euler = (r(4),0,0)
    pb["neck"].rotation_euler = (r(2),0,0); pb["head"].rotation_euler = (r(4), 0, r(3)*br)
    for n in IB: pb[n].keyframe_insert("rotation_euler", frame=fri)
    arm.location = (0,0,0.006*abs(br)); arm.keyframe_insert("location", frame=fri)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.select_all(action='SELECT')
IDLE = OUT.replace("_animado","_idle")
bpy.ops.export_scene.gltf(filepath=IDLE, export_format='GLB', export_animations=True, export_skins=True, export_apply=False)
print("IDLE OK", os.path.exists(IDLE))
