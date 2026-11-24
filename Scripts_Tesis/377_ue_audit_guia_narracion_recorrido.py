# 377_ue_audit_guia_narracion_recorrido.py
# Auditoria en vivo del editor: valida que la GUIA (Adela), la NARRACION por zona
# y el RECORRIDO ordenado esten correctamente colocados y sin errores evidentes.
# Solo LECTURA. Escribe resultado en Saved/ClaudeBackups/audit_guia_narr_recorrido_377.json
import unreal, json, math

eas = unreal.EditorActorSubsystem()
actors = eas.get_all_level_actors()

def loc(a):
    v = a.get_actor_location()
    return [round(v.x,1), round(v.y,1), round(v.z,1)]

def yaw(a):
    return round(a.get_actor_rotation().yaw,1)

def label(a):
    try: return a.get_actor_label()
    except: return "?"

out = {"adela": [], "narracion": [], "recorrido": {}, "errs": [], "resumen": {}}

# ---------- ADELA (guia) ----------
adela_names = []
for a in actors:
    lb = label(a)
    if lb.lower().startswith("guia_adela") or lb.lower().startswith("adela_zona") or lb.lower().startswith("adela_intro") or "adela" in lb.lower():
        comp_mesh = None
        kind = a.get_class().get_name()
        # intentar leer si es skeletal o static
        mesh_info = ""
        try:
            sk = a.get_component_by_class(unreal.SkeletalMeshComponent)
            if sk:
                m = sk.get_skeletal_mesh_asset()
                if m: mesh_info = "SKELETAL:" + m.get_name()
        except: pass
        if not mesh_info:
            try:
                st = a.get_component_by_class(unreal.StaticMeshComponent)
                if st:
                    m = st.get_static_mesh()
                    if m: mesh_info = "STATIC:" + m.get_name()
            except: pass
        adela_names.append(lb)
        out["adela"].append({
            "label": lb, "class": kind, "loc": loc(a),
            "yaw": yaw(a), "mesh": mesh_info,
            "hidden": a.get_editor_property("hidden")
        })

# audio de intro de Adela
for a in actors:
    lb = label(a)
    if "intro" in lb.lower() and "audio" in lb.lower():
        try:
            ac = a.get_component_by_class(unreal.AudioComponent)
            snd = ""
            auto = None
            if ac:
                s = ac.get_sound()
                if s: snd = s.get_name()
                auto = ac.get_editor_property("auto_activate")
            out["adela"].append({"label": lb, "audio": snd, "auto_activate": auto, "loc": loc(a)})
        except Exception as e:
            out["errs"].append("intro_audio:"+str(e))

# ---------- NARRACION por zona (RELATO_*) ----------
for a in actors:
    lb = label(a)
    if lb.startswith("RELATO_") or lb.startswith("RelatoCartela"):
        info = {"label": lb, "loc": loc(a)}
        try:
            ac = a.get_component_by_class(unreal.AudioComponent)
            if ac:
                s = ac.get_sound()
                info["audio"] = s.get_name() if s else None
                info["auto_activate"] = ac.get_editor_property("auto_activate")
                info["spatialize"] = ac.get_editor_property("allow_spatialization")
        except Exception as e:
            info["audio_err"] = str(e)
        # trigger
        try:
            comps = a.get_components_by_class(unreal.PrimitiveComponent)
            trig = []
            for c in comps:
                cn = c.get_name()
                ce = c.get_collision_enabled()
                goe = c.get_editor_property("generate_overlap_events")
                trig.append({"comp": cn, "col": str(ce), "overlap": goe})
            info["trigs"] = trig
        except Exception as e:
            info["trig_err"] = str(e)
        out["narracion"].append(info)

# ---------- RECORRIDO: barreras, triggers, creditos, playerstart ----------
bars, trigs, cred, ps = [], [], [], []
for a in actors:
    tags = [str(t) for t in a.tags]
    lb = label(a)
    if "BarConvento" in tags or "BarHacienda" in tags:
        bars.append({
            "tag": [t for t in tags if t.startswith("Bar")][0],
            "loc": loc(a),
            "hidden": a.get_editor_property("hidden"),
            "col": str(a.get_component_by_class(unreal.StaticMeshComponent).get_collision_enabled()) if a.get_component_by_class(unreal.StaticMeshComponent) else "?"
        })
    if "Creditos" in tags:
        cred.append({"label": lb, "loc": loc(a), "hidden": a.get_editor_property("hidden")})
    if a.get_class().get_name() == "PlayerStart":
        ps.append({"label": lb, "loc": loc(a)})
    if lb.startswith("GestorRecorrido"):
        comps = a.get_components_by_class(unreal.BoxComponent)
        for c in comps:
            trigs.append({"comp": c.get_name(), "overlap": c.get_editor_property("generate_overlap_events")})

out["recorrido"] = {"barreras": bars, "triggers_gestor": trigs, "creditos": cred, "playerstart": ps}

out["resumen"] = {
    "adela_actores": len([x for x in out["adela"] if "mesh" in x]),
    "adela_audio_intro": len([x for x in out["adela"] if "audio" in x]),
    "narracion_puntos": len(out["narracion"]),
    "barreras": len(bars),
    "triggers_gestor": len(trigs),
    "creditos": len(cred),
    "playerstart": len(ps),
}

p = "C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/audit_guia_narr_recorrido_377.json"
with open(p, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("WROTE", p)
