# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace: (BLENDER) Riguea el Condenado (sin piso, 1.75m, brazos abajo) con esqueleto humanoide A-pose, auto-weights + suavizado, y le crea un IDLE DE TORMENTO siniestro (se balancea, cabeza cuelga en agonia, brazos se alzan/caen jalando, tiembla) -> las cadenas de munecas/tobillos se mecen. Render GIF preview + export GLB animado.
# Por que: El usuario pidio que se muevan sus cadenas y sea de miedo.
# ------------------------------------------------------------
import bpy, math, mathutils, os, glob as _g
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/condenado_sinpiso.glb"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/condenado_animado.glb"
FR_DIR = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cond_frames/"
GIF = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/condenado_anim_preview.gif"
os.makedirs(FR_DIR, exist_ok=True)
for _f in _g.glob(FR_DIR + "*.png"): os.remove(_f)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = mesh; mesh.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
H = mesh.dimensions.z
AX = mesh.dimensions.x / 2.0

# ---- armature A-pose (brazos abajo, piernas separadas) ----
armd = bpy.data.armatures.new("CondRig")
arm = bpy.data.objects.new("CondRig", armd); bpy.context.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = armd.edit_bones
def bone(n, h, t, p=None, c=False):
    b = eb.new(n); b.head = mathutils.Vector(h); b.tail = mathutils.Vector(t)
    if p: b.parent = p; b.use_connect = c
    return b
hips  = bone("hips",  (0,0,0.50*H), (0,0,0.57*H))
spine = bone("spine", (0,0,0.57*H), (0,0,0.68*H), hips, True)
chest = bone("chest", (0,0,0.68*H), (0,0,0.80*H), spine, True)
neck  = bone("neck",  (0,0,0.80*H), (0,0,0.85*H), chest, True)
head  = bone("head",  (0,0,0.85*H), (0,0,0.98*H), neck, True)
# brazos hacia abajo (A-pose) y algo afuera
# brazos reales medidos: cuelgan en x ~0.26 (hombro) a ~0.36 (mano), z 0.80H a 0.45H
shL = bone("shoulder.L",(0.08,0,0.80*H),(0.25,0,0.80*H), chest)
uaL = bone("upperarm.L",(0.26,0,0.80*H),(0.30,0,0.64*H), shL, True)
laL = bone("lowerarm.L",(0.30,0,0.64*H),(0.33,0,0.51*H), uaL, True)
haL = bone("hand.L",(0.33,0,0.51*H),(0.36,0,0.45*H), laL, True)
shR = bone("shoulder.R",(-0.08,0,0.80*H),(-0.25,0,0.80*H), chest)
uaR = bone("upperarm.R",(-0.26,0,0.80*H),(-0.30,0,0.64*H), shR, True)
laR = bone("lowerarm.R",(-0.30,0,0.64*H),(-0.33,0,0.51*H), uaR, True)
haR = bone("hand.R",(-0.33,0,0.51*H),(-0.36,0,0.45*H), laR, True)
thL = bone("thigh.L",(0.11,0,0.50*H),(0.13,0,0.27*H), hips)
shnL= bone("shin.L",(0.13,0,0.27*H),(0.15,0,0.05*H), thL, True)
ftL = bone("foot.L",(0.15,0,0.05*H),(0.15,-0.12,0.0), shnL, True)
thR = bone("thigh.R",(-0.11,0,0.50*H),(-0.13,0,0.27*H), hips)
shnR= bone("shin.R",(-0.13,0,0.27*H),(-0.15,0,0.05*H), thR, True)
ftR = bone("foot.R",(-0.15,0,0.05*H),(-0.15,-0.12,0.0), shnR, True)
SEG = [(b.name, b.head.copy(), b.tail.copy()) for b in eb]  # segmentos de hueso para pesado manual
bpy.ops.object.mode_set(mode='OBJECT')

# PESADO MANUAL (nearest-bone): el auto-weight fallaba con los brazos pegados al torso.
def pt_seg(p, a, b):
    ab = b - a; L2 = ab.length_squared
    if L2 < 1e-9: return (p - a).length
    t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
    return (a + ab * t - p).length
for name, h, t in SEG:
    if name not in mesh.vertex_groups: mesh.vertex_groups.new(name=name)
for v in mesh.data.vertices:
    p = v.co
    ds = sorted(((pt_seg(p, h, t), name) for name, h, t in SEG), key=lambda x: x[0])
    near = ds[:3]                          # 3 huesos mas cercanos
    ws = [(1.0/(d*d + 1e-5), name) for d, name in near]  # caida inversa al cuadrado -> mezcla suave
    tot = sum(w for w, _ in ws)
    for w, name in ws:
        mesh.vertex_groups[name].add([v.index], w/tot, 'REPLACE')
# modificador armature + emparentar
mesh.parent = arm
md = mesh.modifiers.new("Armature", 'ARMATURE'); md.object = arm
# suavizar un poco las uniones (sin despegar los miembros)
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); bpy.context.view_layer.objects.active = mesh
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
try: bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.7, repeat=14)
except: pass
bpy.ops.object.mode_set(mode='OBJECT')

# ---- IDLE DE TORMENTO ----
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
sc = bpy.context.scene
pb = arm.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
r = math.radians
arm.rotation_mode = 'XYZ'
allb = ["hips","spine","chest","neck","head","upperarm.L","upperarm.R","lowerarm.L","lowerarm.R",
        "thigh.L","thigh.R","shin.L","shin.R","foot.L","foot.R"]
# CAMINAR ARRASTRADO de encadenado: piernas dan pasos lentos, encorvado CONSTANTE (torso sin exagerar),
# brazos cuelgan con leve columpio (mecen cadenas), cabeza gacha. Amplitudes moderadas -> poca deformacion.
N = 48
sc.frame_start = 1; sc.frame_end = N
HCH, HSP, HNK, HHD = r(13), r(8), r(9), r(7)  # encorvado constante (cuello/cabeza gachos)

def walk(f, ph):
    a = 2*math.pi*ph
    s = math.sin(a); so = math.sin(a+math.pi)
    # PIERNAS: pasos arrastrados (zancada corta), rodilla dobla al levantar, pie rueda
    pb["thigh.L"].rotation_euler = (r(15)*s, 0, 0)
    pb["thigh.R"].rotation_euler = (r(15)*so, 0, 0)
    liftL = max(0.0, math.sin(a - math.pi*0.5)); liftR = max(0.0, math.sin(a + math.pi*0.5))
    pb["shin.L"].rotation_euler = (-r(7) - r(22)*liftL, 0, 0)
    pb["shin.R"].rotation_euler = (-r(7) - r(22)*liftR, 0, 0)
    pb["foot.L"].rotation_euler = (-r(12)*s, 0, 0)
    pb["foot.R"].rotation_euler = (-r(12)*so, 0, 0)
    # BRAZOS: cuelgan, columpio suave en Z opuesto a piernas -> mecen las cadenas
    pb["upperarm.L"].rotation_euler = (0, 0, -r(11)*s)
    pb["upperarm.R"].rotation_euler = (0, 0,  r(11)*so)
    pb["lowerarm.L"].rotation_euler = (0, 0, -r(8))
    pb["lowerarm.R"].rotation_euler = (0, 0,  r(8))
    # TORSO: encorvado CONSTANTE, solo leve balanceo (NADA exagerado)
    pb["hips"].rotation_euler  = (r(3), 0, r(2)*s)
    pb["spine"].rotation_euler = (HSP, 0, -r(1.5)*s)
    pb["chest"].rotation_euler = (HCH, 0, r(1.5)*s)
    pb["neck"].rotation_euler  = (HNK, 0, r(2)*s)
    pb["head"].rotation_euler  = (HHD, 0, 0)
    # bob leve + SIN lurch de cuerpo entero
    arm.location = (0, 0, 0.018*abs(math.sin(a)))
    arm.rotation_euler = (0, 0, 0)
    for n in allb: pb[n].keyframe_insert("rotation_euler", frame=f)
    arm.keyframe_insert("location", frame=f); arm.keyframe_insert("rotation_euler", frame=f)

for f in range(1, N+1):
    walk(f, (f-1)/float(N))
bpy.ops.object.mode_set(mode='OBJECT')

# ---- render GIF preview + export ----
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); bpy.context.collection.objects.link(cam)
cam.location = (2.7, -2.9, 1.05)
dv = mathutils.Vector((0,0,0.85)) - cam.location
cam.rotation_euler = dv.to_track_quat('-Z','Y').to_euler()
sc.camera = cam
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun",'SUN')); bpy.context.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler=(math.radians(55),0,math.radians(25))
if sc.world is None: sc.world = bpy.data.worlds.new("W")
sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.02,0.02,0.03,1)
sc.render.resolution_x=360; sc.render.resolution_y=500; sc.render.fps=30
try: sc.render.engine='BLENDER_EEVEE_NEXT'
except: pass
sc.render.image_settings.file_format='PNG'
sc.render.filepath = FR_DIR + "f_"
sc.frame_step = 2
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.render.render(animation=True)

# GIF (encoder LZW propio, paleta 3-3-2)
import numpy as np
def lzw(idxs, mcs=8):
    clear=1<<mcs; end=clear+1; cs=mcs+1; out=bytearray(); buf=0; nb=0
    def emit(c):
        nonlocal buf,nb
        buf|=c<<nb; nb+=cs
        while nb>=8: out.append(buf&0xFF); buf>>=8; nb-=8
    emit(clear); nxt=end+1
    for i in idxs:
        emit(int(i)); nxt+=1
        if nxt>=511: emit(clear); nxt=end+1
    emit(end)
    if nb>0: out.append(buf&0xFF)
    return out
def sub(d):
    o=bytearray(); i=0
    while i<len(d): c=d[i:i+255]; o.append(len(c)); o+=c; i+=255
    o.append(0); return o
files=sorted(_g.glob(FR_DIR+"f_*.png"))
W=sc.render.resolution_x; Hh=sc.render.resolution_y
g=bytearray(b"GIF89a"); g+=bytes([W&0xFF,W>>8,Hh&0xFF,Hh>>8,0xF7,0,0])
for i in range(256): g+=bytes([((i>>5)&7)*36,((i>>2)&7)*36,(i&3)*85])
g+=bytes([0x21,0xFF,0x0B])+b"NETSCAPE2.0"+bytes([0x03,0x01,0,0,0])
for fp in files:
    im=bpy.data.images.load(fp); w,h=im.size
    aa=np.array(im.pixels[:]).reshape(h,w,4)[::-1]
    rgb=np.clip(aa[:,:,:3]*255,0,255).astype(np.uint8)
    idx=(((rgb[:,:,0]>>5)<<5)|((rgb[:,:,1]>>5)<<2)|(rgb[:,:,2]>>6)).astype(np.uint8).flatten()
    g+=bytes([0x21,0xF9,0x04,0x00,8,0,0x00])
    g+=bytes([0x2C,0,0,0,0,w&0xFF,w>>8,h&0xFF,h>>8,0x00])
    g+=bytes([0x08])+sub(lzw(idx,8)); bpy.data.images.remove(im)
g+=bytes([0x3B]); open(GIF,"wb").write(g)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_skins=True, export_apply=False)
print("COND OK gif", os.path.exists(GIF), "frames", len(files), "glb", round(os.path.getsize(OUT)/1024/1024,1),"MB")

# ---- REPOSO (idle) GLB separado: encorvado quieto, cadenas apenas mecen, temblor leve ----
arm.animation_data_clear()
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='POSE')
Ni = 100; sc.frame_start = 1; sc.frame_end = Ni
for fri in range(1, Ni+1):
    a = 2*math.pi*(fri-1)/float(Ni); br = math.sin(a); trem = math.sin(a*11)
    for n in allb: pb[n].rotation_euler = (0,0,0)
    pb["chest"].rotation_euler = (r(13),0,0); pb["spine"].rotation_euler = (r(8),0,0)
    pb["neck"].rotation_euler = (r(9),0,0); pb["head"].rotation_euler = (r(7)+r(1.5)*trem,0,0)  # cabeza baja temblando
    pb["hips"].rotation_euler = (r(3),0,r(1.5)*br)
    pb["shin.L"].rotation_euler = (-r(6),0,0); pb["shin.R"].rotation_euler = (-r(6),0,0)
    pb["upperarm.L"].rotation_euler = (0,0,-r(3)*br); pb["upperarm.R"].rotation_euler = (0,0,r(3)*br)  # cadenas mecen apenas
    pb["lowerarm.L"].rotation_euler = (0,0,-r(6)); pb["lowerarm.R"].rotation_euler = (0,0,r(6))
    for n in allb: pb[n].keyframe_insert("rotation_euler", frame=fri)
    arm.location = (0,0,0.005*abs(br)); arm.keyframe_insert("location", frame=fri)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.select_all(action='SELECT')
IDLE = OUT.replace("_animado","_idle")
bpy.ops.export_scene.gltf(filepath=IDLE, export_format='GLB', export_animations=True, export_skins=True, export_apply=False)
print("IDLE OK", os.path.exists(IDLE))
