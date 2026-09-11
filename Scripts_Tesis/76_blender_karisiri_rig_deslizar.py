# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-27
# Que hace: (BLENDER) Riguea el Karisiri (encapuchado de tunica larga, piernas ocultas) con esqueleto de figura tunicada + huesos de borde (hem) + pies. Pesado MANUAL mezclado (3 huesos, 1/d^2) + suavizado. Animacion de DESLIZAMIENTO siniestro: se mece (pasos bajo la tunica), capucha gira lento buscando, borde se mece, pies arrastran. Render GIF + export GLB.
# Por que: El usuario quiere el Karisiri misterioso y de miedo que camine/se mueva. La tunica tapa las piernas -> glide, no walk visible.
# Aplica lecciones de [[apparitions-state]]: medir/colocar huesos en la malla, pesado manual mezclado, amplitudes moderadas, movimiento de cuerpo entero.
# ------------------------------------------------------------
import bpy, math, mathutils, os, glob as _g
SRC = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/karisiri_opt.glb"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/karisiri_animado.glb"
FR_DIR = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/kar_frames/"
GIF = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/karisiri_anim_preview.gif"
os.makedirs(FR_DIR, exist_ok=True)
for _f in _g.glob(FR_DIR + "*.png"): os.remove(_f)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
bpy.context.view_layer.objects.active = mesh; mesh.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
# escalar a 1.8m, origen a base
co = [v.co for v in mesh.data.vertices]; minz = min(c.z for c in co)
cx = (min(c.x for c in co)+max(c.x for c in co))/2; cy = (min(c.y for c in co)+max(c.y for c in co))/2
mesh.location = (-cx, -cy, -minz); bpy.ops.object.transform_apply(location=True)
Hn = mesh.dimensions.z; f = 1.8/Hn if Hn>0.01 else 1.0
mesh.scale = (f,f,f); bpy.ops.object.transform_apply(scale=True)
H = mesh.dimensions.z

# ---- armature figura tunicada ----
armd = bpy.data.armatures.new("KarRig"); arm = bpy.data.objects.new("KarRig", armd)
bpy.context.collection.objects.link(arm); bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT'); eb = armd.edit_bones
def bone(n,h,t,p=None,c=False):
    b=eb.new(n); b.head=mathutils.Vector(h); b.tail=mathutils.Vector(t)
    if p: b.parent=p; b.use_connect=c
    return b
hips  = bone("hips",  (0,0,0.46*H),(0,0,0.55*H))
spine = bone("spine", (0,0,0.55*H),(0,0,0.65*H), hips, True)
chest = bone("chest", (0,0,0.65*H),(0,0,0.73*H), spine, True)
neck  = bone("neck",  (0,0,0.73*H),(0,0,0.79*H), chest, True)
head  = bone("head",  (0,0,0.79*H),(0,0,0.95*H), neck, True)   # la capucha
shL=bone("shoulder.L",(0.05,0,0.72*H),(0.13,0,0.72*H), chest)
uaL=bone("upperarm.L",(0.13,0,0.72*H),(0.17,0,0.58*H), shL, True)
laL=bone("lowerarm.L",(0.17,0,0.58*H),(0.19,0,0.49*H), uaL, True)
haL=bone("hand.L",(0.19,0,0.49*H),(0.19,0,0.44*H), laL, True)
shR=bone("shoulder.R",(-0.05,0,0.72*H),(-0.13,0,0.72*H), chest)
uaR=bone("upperarm.R",(-0.13,0,0.72*H),(-0.17,0,0.58*H), shR, True)
laR=bone("lowerarm.R",(-0.17,0,0.58*H),(-0.19,0,0.49*H), uaR, True)
haR=bone("hand.R",(-0.19,0,0.49*H),(-0.19,0,0.44*H), laR, True)
# borde de tunica (hem) para mecer la falda
hemL=bone("hem.L",(0.10,0,0.44*H),(0.14,0,0.03*H), hips)
hemR=bone("hem.R",(-0.10,0,0.44*H),(-0.14,0,0.03*H), hips)
hemF=bone("hem.F",(0,0.05,0.44*H),(0,0.12,0.03*H), hips)
hemB=bone("hem.B",(0,-0.05,0.44*H),(0,-0.12,0.03*H), hips)
# piernas OCULTAS bajo la tunica -> dan PASOS reales a los pies que asoman
thL=bone("thigh.L",(0.07,0,0.45*H),(0.07,0,0.25*H), hips)
shnL=bone("shin.L",(0.07,0,0.25*H),(0.07,0,0.06*H), thL, True)
ftL=bone("foot.L",(0.07,0,0.06*H),(0.07,-0.13,0.0), shnL, True)
thR=bone("thigh.R",(-0.07,0,0.45*H),(-0.07,0,0.25*H), hips)
shnR=bone("shin.R",(-0.07,0,0.25*H),(-0.07,0,0.06*H), thR, True)
ftR=bone("foot.R",(-0.07,0,0.06*H),(-0.07,-0.13,0.0), shnR, True)
SEG = [(b.name, b.head.copy(), b.tail.copy()) for b in eb]
bpy.ops.object.mode_set(mode='OBJECT')

# ---- pesado MANUAL mezclado (3 huesos, 1/d^2) ----
def pt_seg(p,a,b):
    ab=b-a; L2=ab.length_squared
    if L2<1e-9: return (p-a).length
    t=max(0.0,min(1.0,(p-a).dot(ab)/L2)); return (a+ab*t-p).length
for name,h,t in SEG:
    if name not in mesh.vertex_groups: mesh.vertex_groups.new(name=name)
for v in mesh.data.vertices:
    p=v.co
    ds=sorted(((pt_seg(p,h,t),name) for name,h,t in SEG), key=lambda x:x[0])[:3]
    ws=[(1.0/(d*d+1e-5),name) for d,name in ds]; tot=sum(w for w,_ in ws)
    for w,name in ws: mesh.vertex_groups[name].add([v.index], w/tot, 'REPLACE')
mesh.parent=arm; md=mesh.modifiers.new("Armature",'ARMATURE'); md.object=arm
bpy.ops.object.select_all(action='DESELECT'); mesh.select_set(True); bpy.context.view_layer.objects.active=mesh
bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
try: bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.65, repeat=12)
except: pass
bpy.ops.object.mode_set(mode='OBJECT')

# ---- DESLIZAMIENTO siniestro ----
bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='POSE')
sc=bpy.context.scene; pb=arm.pose.bones
for b in pb: b.rotation_mode='XYZ'
arm.rotation_mode='XYZ'; r=math.radians
N=60; sc.frame_start=1; sc.frame_end=N
allb=["hips","spine","chest","neck","head","upperarm.L","upperarm.R","lowerarm.L","lowerarm.R",
      "hand.L","hand.R","hem.L","hem.R","hem.F","hem.B","thigh.L","thigh.R","shin.L","shin.R","foot.L","foot.R"]
def glide(fr, ph):
    a=2*math.pi*ph
    s=math.sin(a); so=math.sin(a+math.pi)   # ciclo de paso: pierna izq luego der
    turn=math.sin(math.pi*ph)               # 1 giro lento de capucha por vuelta
    # PIERNAS (ocultas) dan pasos CORTOS y suaves -> pies avanzan/retroceden, sin tambalear
    pb["thigh.L"].rotation_euler = (r(10)*s, 0, 0)
    pb["thigh.R"].rotation_euler = (r(10)*so, 0, 0)
    liftL=max(0.0,math.sin(a-math.pi*0.5)); liftR=max(0.0,math.sin(a+math.pi*0.5))
    pb["shin.L"].rotation_euler = (-r(3)-r(12)*liftL, 0, 0)
    pb["shin.R"].rotation_euler = (-r(3)-r(12)*liftR, 0, 0)
    pb["foot.L"].rotation_euler = (-r(6)*s, 0, 0)
    pb["foot.R"].rotation_euler = (-r(6)*so, 0, 0)
    # CAPUCHA: QUIETA (no mueve la cabeza), solo inclinada al frente constante
    pb["neck"].rotation_euler = (r(5), 0, 0)
    pb["head"].rotation_euler = (r(4), 0, 0)
    # cuerpo: encorvado leve CONSTANTE, SIN mecido lateral (estable)
    pb["hips"].rotation_euler  = (r(2), 0, 0)
    pb["spine"].rotation_euler = (r(4), 0, 0)
    pb["chest"].rotation_euler = (r(4), 0, 0)
    # BRAZOS: columpio adelante-atras alternado, LENTO (1 por vuelta) para que no se vea brusco;
    #         hombro suavizado -> se dobla parejo, sin chunk rigido.
    sw = math.sin(2*math.pi*ph); swo = math.sin(2*math.pi*ph + math.pi)
    pb["upperarm.L"].rotation_euler = (r(4)*sw, 0, 0)      # MUY leve (la tunica casi no se mueve)
    pb["upperarm.R"].rotation_euler = (r(4)*swo, 0, 0)
    pb["lowerarm.L"].rotation_euler = (r(7) + r(3)*sw, 0, 0)
    pb["lowerarm.R"].rotation_euler = (r(7) + r(3)*swo, 0, 0)
    pb["hand.L"].rotation_euler = (0, 0, 0)
    pb["hand.R"].rotation_euler = (0, 0, 0)
    # borde de tunica se mece muy suave
    pb["hem.L"].rotation_euler = (0,0,-r(2.5)*s)
    pb["hem.R"].rotation_euler = (0,0, r(2.5)*s)
    pb["hem.F"].rotation_euler = (r(3)*s,0,0)
    pb["hem.B"].rotation_euler = (-r(3)*s,0,0)
    # bob muy leve (casi sin rebote)
    arm.location=(0, 0, 0.007*abs(math.sin(a)))
    arm.rotation_euler=(0,0,0)
    for n in allb: pb[n].keyframe_insert("rotation_euler", frame=fr)
    arm.keyframe_insert("location", frame=fr); arm.keyframe_insert("rotation_euler", frame=fr)
for fr in range(1,N+1): glide(fr,(fr-1)/float(N))
bpy.ops.object.mode_set(mode='OBJECT')

# ---- render GIF + export ----
cam=bpy.data.objects.new("Cam",bpy.data.cameras.new("Cam")); bpy.context.collection.objects.link(cam)
cam.location=(2.3,-3.2,1.15)
dv=mathutils.Vector((0,0,0.95))-cam.location; cam.rotation_euler=dv.to_track_quat('-Z','Y').to_euler()
sc.camera=cam
sun=bpy.data.objects.new("Sun",bpy.data.lights.new("Sun",'SUN')); bpy.context.collection.objects.link(sun)
sun.data.energy=3.2; sun.rotation_euler=(math.radians(55),0,math.radians(25))
if sc.world is None: sc.world=bpy.data.worlds.new("W")
sc.world.use_nodes=True; sc.world.node_tree.nodes["Background"].inputs[0].default_value=(0.02,0.02,0.03,1)
sc.render.resolution_x=360; sc.render.resolution_y=520; sc.render.fps=30
try: sc.render.engine='BLENDER_EEVEE_NEXT'
except: pass
sc.render.image_settings.file_format='PNG'; sc.render.filepath=FR_DIR+"f_"; sc.frame_step=2
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.render.render(animation=True)
import numpy as np
def lzw(idxs,mcs=8):
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
files=sorted(_g.glob(FR_DIR+"f_*.png")); W=sc.render.resolution_x; Hh=sc.render.resolution_y
g=bytearray(b"GIF89a"); g+=bytes([W&0xFF,W>>8,Hh&0xFF,Hh>>8,0xF7,0,0])
for i in range(256): g+=bytes([((i>>5)&7)*36,((i>>2)&7)*36,(i&3)*85])
g+=bytes([0x21,0xFF,0x0B])+b"NETSCAPE2.0"+bytes([0x03,0x01,0,0,0])
for fp in files:
    im=bpy.data.images.load(fp); w,h=im.size
    aa=np.array(im.pixels[:]).reshape(h,w,4)[::-1]; rgb=np.clip(aa[:,:,:3]*255,0,255).astype(np.uint8)
    idx=(((rgb[:,:,0]>>5)<<5)|((rgb[:,:,1]>>5)<<2)|(rgb[:,:,2]>>6)).astype(np.uint8).flatten()
    g+=bytes([0x21,0xF9,0x04,0x00,7,0,0x00]); g+=bytes([0x2C,0,0,0,0,w&0xFF,w>>8,h&0xFF,h>>8,0x00])
    g+=bytes([0x08])+sub(lzw(idx,8)); bpy.data.images.remove(im)
g+=bytes([0x3B]); open(GIF,"wb").write(g)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True, export_skins=True, export_apply=False)
print("KAR OK gif",os.path.exists(GIF),"frames",len(files),"glb",round(os.path.getsize(OUT)/1024/1024,1),"MB")

# ---- REPOSO (idle) como GLB separado: parado, respiracion muy leve, sin pasos ----
arm.animation_data_clear()
bpy.context.view_layer.objects.active=arm; bpy.ops.object.mode_set(mode='POSE')
Ni=90; sc.frame_start=1; sc.frame_end=Ni
for fri in range(1,Ni+1):
    br=math.sin(2*math.pi*(fri-1)/float(Ni))     # respiracion lenta
    for n in allb: pb[n].rotation_euler=(0,0,0)
    pb["lowerarm.L"].rotation_euler=(r(7),0,0); pb["lowerarm.R"].rotation_euler=(r(7),0,0)
    pb["hips"].rotation_euler=(r(2),0,0)
    pb["spine"].rotation_euler=(r(4)+r(1.2)*br,0,0); pb["chest"].rotation_euler=(r(4)+r(1.2)*br,0,0)
    pb["neck"].rotation_euler=(r(5),0,0); pb["head"].rotation_euler=(r(4),0,0)
    for n in allb: pb[n].keyframe_insert("rotation_euler",frame=fri)
    arm.location=(0,0,0.004*br); arm.keyframe_insert("location",frame=fri)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.object.select_all(action='SELECT')
IDLE=OUT.replace("_animado","_idle")
bpy.ops.export_scene.gltf(filepath=IDLE, export_format='GLB', export_animations=True, export_skins=True, export_apply=False)
print("IDLE OK", os.path.exists(IDLE))
