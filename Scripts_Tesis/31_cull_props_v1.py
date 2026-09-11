# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 17:24
# Que hace este script: Aplica cull a props StaticMeshActor y verifica luces.
# Por que se necesito: Culling por objeto sin volumen.
# Resultado obtenido: 0 props sueltos; 111 luces identicas.
# ------------------------------------------------------------

import unreal, json, traceback
out={'err':None}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    LIGHTPROP=['farol','apl_','aplique','vela','candelabr','cirio','lampara','lantern','lamp','gal_','_glow','emis','brasa','fogon']
    ARCH=['exp_','hackit','hacv','wall','muro','roof','techo','floor','piso','foundation','column','columna',
          'arch','arco','stair','escalera','ceiling','balcony','corridor','galer','timber','cornice','trim',
          'plinth','apron','landing','ground','skysphere','terrain','island','cliff','circulation','hardscape',
          'foundation','shell','railing','baranda','balaustr','pillar','pilar','bridge','wall_','_wall']
    def interior(x,y):
        if -9300<x<-4600 and -3400<y<-350: return True   # Hacienda
        if 4300<x<10000 and 3000<y<7000: return True      # Convento
        if -1700<x<1700 and 9400<y<14300: return True     # Templo
        return False
    cull_in=0; cull_ex=0; skip_light=0; skip_arch=0; skip_big=0
    for a in eas.get_all_level_actors():
        if a.get_class().get_name() not in ('StaticMeshActor',): continue
        nm=a.get_actor_label().lower()
        if any(k in nm for k in LIGHTPROP): skip_light+=1; continue
        if any(k in nm for k in ARCH): skip_arch+=1; continue
        smc=a.get_component_by_class(unreal.StaticMeshComponent)
        if not smc: continue
        # skip big meshes (architecture-scale)
        big=False
        try:
            b=a.get_actor_bounds(False); e=b[1]
            if max(e.x,e.y,e.z)>800: big=True
        except: pass
        if big: skip_big+=1; continue
        loc=a.get_actor_location()
        d=2500.0 if interior(loc.x,loc.y) else 5000.0
        try:
            smc.set_editor_property('desired_max_draw_distance',d)
            if d==2500.0: cull_in+=1
            else: cull_ex+=1
        except: pass
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    out['cull_interior_2500']=cull_in; out['cull_exterior_5000']=cull_ex
    out['skipped_lightprops']=skip_light; out['skipped_architecture']=skip_arch; out['skipped_big']=skip_big
    # ---- verify lights vs baseline ----
    base=json.load(open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/baseline_lights.json'))
    cur=[]
    for a in eas.get_all_level_actors():
        for c in a.get_components_by_class(unreal.LightComponentBase):
            cls=c.get_class().get_name()
            if cls not in ('PointLightComponent','SpotLightComponent','DirectionalLightComponent','SkyLightComponent'): continue
            loc=a.get_actor_location(); rec={'n':a.get_actor_label(),'cls':cls,'x':round(loc.x),'y':round(loc.y),'z':round(loc.z)}
            try: rec['cd']=round(c.get_editor_property('intensity'),2)
            except: pass
            try: rec['r']=round(c.get_editor_property('attenuation_radius'))
            except: pass
            try: rec['K']=round(c.get_editor_property('temperature')) if c.get_editor_property('use_temperature') else 0
            except: pass
            cur.append(rec)
    cur.sort(key=lambda r:r['n']); base.sort(key=lambda r:r['n'])
    out['lights_before']=len(base); out['lights_after']=len(cur)
    out['lights_identical']= (json.dumps(base,sort_keys=True)==json.dumps(cur,sort_keys=True))
    if not out['lights_identical']:
        diffs=[]
        bd={r['n']:r for r in base}; cd={r['n']:r for r in cur}
        for k in set(bd)|set(cd):
            if bd.get(k)!=cd.get(k): diffs.append(k)
        out['changed_lights']=diffs[:20]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_props.json','w').write(json.dumps(out,indent=1))
except Exception as e:
    out['err']=str(e); out['tb']=traceback.format_exc()[-700:]
    open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/cull_props.json','w').write(json.dumps(out,indent=1))
