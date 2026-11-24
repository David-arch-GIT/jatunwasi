# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-11-08
# Que hace: AUDITORIA de rendimiento (solo lectura) del estado ACTUAL del mapa,
#   para decidir optimizaciones anti-cuelgue y para transmitir sin perder calidad.
#   Mide: luces por clase/movilidad/sombra, secciones de malla (proxy de draw calls),
#   triangulos aprox, actores con material translucido (overdraw), blend del domo del
#   cielo (M_Mountains), instancias ISM/HISM, pool de texturas.
# Por que: sin visor conectado, esto da la foto real de costes para optimizar con criterio.
# Resultado: Saved/ClaudeBackups/mega_audit.json
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
R={}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    acts=eas.get_all_level_actors()
    R["total_actores"]=len(acts)
    # --- Luces ---
    lights={}
    for a in acts:
        for comp in a.get_components_by_class(unreal.LightComponent):
            cls=comp.get_class().get_name()
            d=lights.setdefault(cls,{"total":0,"shadow":0,"movable":0,"static":0,"stationary":0})
            d["total"]+=1
            try:
                if comp.get_editor_property("cast_shadows"): d["shadow"]+=1
            except: pass
            try:
                mob=str(a.root_component.mobility) if a.root_component else ""
                if "Movable" in mob: d["movable"]+=1
                elif "Static" in mob and "Stationary" not in mob: d["static"]+=1
                elif "Stationary" in mob: d["stationary"]+=1
            except: pass
    R["luces"]=lights
    # --- Mallas: secciones (proxy de draw calls) + triangulos ---
    secciones=0; tris=0; smc_count=0; ism_inst=0; ism_comp=0
    transl_actores={}; dome_blend=None
    for a in acts:
        for comp in a.get_components_by_class(unreal.StaticMeshComponent):
            sm=comp.get_editor_property("static_mesh")
            if not sm: continue
            smc_count+=1
            try:
                nsec=sm.get_num_sections(0); secciones+=nsec
            except: nsec=1
            try: tris+=sm.get_num_triangles(0)
            except: pass
            # instancias si es ISM/HISM
            if isinstance(comp,unreal.InstancedStaticMeshComponent):
                ism_comp+=1
                try: ism_inst+=comp.get_instance_count()
                except: pass
            # materiales translucidos
            for i in range(comp.get_num_materials()):
                mi=comp.get_material(i)
                if not mi: continue
                try:
                    bm=mi.get_base_material() if hasattr(mi,'get_base_material') else mi
                    blend=str(bm.get_editor_property("blend_mode"))
                except: blend=""
                if "TRANSLUCENT" in blend.upper():
                    nm=mi.get_name()
                    transl_actores[nm]=transl_actores.get(nm,0)+1
            if a.get_actor_label()=="ENV_HorizonMtn":
                try:
                    m0=comp.get_material(0)
                    bm=m0.get_base_material() if hasattr(m0,'get_base_material') else m0
                    dome_blend=str(bm.get_editor_property("blend_mode"))
                except Exception as e: dome_blend="err:"+str(e)[:40]
    R["malla_secciones_proxy_drawcalls"]=secciones
    R["malla_triangulos_aprox"]=tris
    R["static_mesh_components"]=smc_count
    R["ism_hism_componentes"]=ism_comp
    R["ism_hism_instancias"]=ism_inst
    R["materiales_translucidos_en_uso"]=transl_actores
    R["domo_cielo_blend"]=dome_blend
    # --- pool de texturas (cvar) ---
    try:
        R["r.Streaming.PoolSize"]=unreal.SystemLibrary.get_console_variable_int_value("r.Streaming.PoolSize")
    except: pass
except Exception as e:
    R["err"]=str(e); R["tb"]=traceback.format_exc()[-500:]
open(out+"/mega_audit.json","w").write(json.dumps(R,indent=1))
print("MEGA_AUDIT_DONE", json.dumps({k:R[k] for k in R if k not in ("materiales_translucidos_en_uso",)}))
