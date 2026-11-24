# 524_blender_rehacer_idle_walk.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: (BLENDER 5.2) BUG hallado: en las 3 leyendas el AnimSequence "Idle" es IDENTICO al "Walk"
#   (0,0 grados de diferencia en todos los huesos; la usuaria ve al duende "caminando quieto"). Causa: el
#   script 79 metia la accion Idle (ligada por "slot" al esqueleto B) en el NLA del esqueleto A; en Blender
#   5.x el slot no coincide y el exportador repetia la caminata. Aqui, por personaje: importa *_animado.glb
#   (malla + esqueleto + Walk) y *_idle.glb (Idle), asigna AMBAS acciones al esqueleto A con su propio slot
#   y exporta *_full.glb (respaldo previo *_full_ago.glb) en modo ACTIONS (una animacion por accion). Luego reimporta el resultado y
#   MIDE que Idle y Walk difieran (rotacion de thigh.L). Misma malla de origen que *_full.glb.
#   HALLAZGO: *_idle.glb trae 2 acciones; la 1ra es copia de la caminata, el reposo real es la mas larga (.001).
import bpy, os, math, json
BASE = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/Models/processed/"
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/blender_524.json"
res = {}
def asignar(arm, act):
    ad = arm.animation_data or arm.animation_data_create()
    ad.action = act
    try:
        if act.slots:
            ad.action_slot = act.slots[0]
    except Exception:
        pass
def rango(arm, act, bone="thigh_L", n=12):
    asignar(arm, act)
    f0, f1 = act.frame_range
    vals = []
    for i in range(n + 1):
        bpy.context.scene.frame_set(int(f0 + (f1 - f0) * i / n))
        pb = arm.pose.bones.get(bone) or next((b for b in arm.pose.bones if "thigh" in b.name.lower() and ("l" in b.name.lower().split("thigh")[-1])), None)
        if pb is None: return None
        vals.append(pb.matrix.to_quaternion())
    return [round(math.degrees(vals[0].rotation_difference(q).angle), 1) for q in vals] + ["hueso=" + pb.name]
for name in ["duende", "condenado", "karisiri"]:
    r = {}
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=BASE + name + "_animado.glb")
        armA = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
        walk = armA.animation_data.action
        antes = set(bpy.data.actions)
        bpy.ops.import_scene.gltf(filepath=BASE + name + "_idle.glb")
        armB = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != armA][0]
        nuevas = [a for a in bpy.data.actions if a not in antes]
        # el REPOSO real es la accion mas larga del idle.glb (la otra es una copia de la caminata)
        idle = max(nuevas, key=lambda a: a.frame_range[1] - a.frame_range[0])
        for a in nuevas:
            if a != idle: bpy.data.actions.remove(a)
        # quitar el esqueleto B y sus mallas (la accion idle queda en bpy.data)
        idle.use_fake_user = True; walk.use_fake_user = True
        for o in [armB] + [c for c in bpy.data.objects if c.parent == armB]:
            bpy.data.objects.remove(o, do_unlink=True)
        walk.name = name + "_Walk"; idle.name = name + "_Idle"
        # el slot de idle debe llamarse como el objeto A para que el exportador lo enlace
        try:
            for a in (idle, walk):
                for s in a.slots:
                    s.name_display = armA.name
        except Exception as e:
            r["slot_warn"] = str(e)[:80]
        r["rango_walk_A"] = rango(armA, walk)
        r["rango_idle_A"] = rango(armA, idle)
        asignar(armA, walk)
        bpy.ops.object.select_all(action='DESELECT')
        armA.select_set(True)
        for c in bpy.data.objects:
            if c.parent == armA: c.select_set(True)
        bpy.context.view_layer.objects.active = armA
        import shutil
        if not os.path.exists(BASE + name + "_full_ago.glb"): shutil.copy2(BASE + name + "_full.glb", BASE + name + "_full_ago.glb")
        out = BASE + name + "_full.glb"
        bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True, export_animations=True,
                                  export_skins=True, export_animation_mode='ACTIONS', export_nla_strips=False)
        r["exportado_MB"] = round(os.path.getsize(out) / 1024 / 1024, 1)
        # verificacion: reimportar y comparar
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=out)
        arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
        r["acciones_en_glb"] = [a.name for a in bpy.data.actions]
        acts = {a.name: a for a in bpy.data.actions}
        ai = [a for n, a in acts.items() if "Idle" in n]; aw = [a for n, a in acts.items() if "Walk" in n]
        if ai and aw:
            r["v2_idle"] = rango(arm, ai[0]); r["v2_walk"] = rango(arm, aw[0])
            r["v2_frames"] = [list(ai[0].frame_range), list(aw[0].frame_range)]
    except Exception as e:
        import traceback; r["err"] = traceback.format_exc()[-600:]
    res[name] = r
open(OUT, "w").write(json.dumps(res, indent=1))
