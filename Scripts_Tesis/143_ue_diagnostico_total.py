# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-03
# Que hace: (UE) DIAGNOSTICO PROFUNDO anti-cuelgue/saturacion. Sin cargar texturas (usa Asset Registry):
#   (1) texturas: cantidad, memoria estimada, top 25 mas pesadas, cuantas >1024. (2) luces dinamicas (movable/stationary).
#   (3) conteo de actores por clase (proxy de draw calls). (4) particulas/Niagara. (5) actores con Tick habilitado.
# ------------------------------------------------------------
import unreal, json
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/diag_total.json"
res = {"tex": {}, "luces": [], "clases": {}, "particulas": [], "err": []}
ar = unreal.AssetRegistryHelpers.get_asset_registry()

# (1) TEXTURAS via Asset Registry (sin cargar)
try:
    tex_assets = ar.get_assets_by_class(unreal.TopLevelAssetPath("/Script/Engine","Texture2D"), True)
    total_mb = 0.0; n=0; big=0; sizes=[]
    for a in tex_assets:
        n += 1
        dim = a.get_tag_value("Dimensions")  # ej "1024x1024"
        w=h=0
        if dim:
            try:
                p=str(dim).lower().replace(" ","").split("x"); w=int(p[0]); h=int(p[1])
            except Exception: pass
        if w>1024 or h>1024: big += 1
        # estimacion memoria: w*h*4 bytes *1.33 (mips) -> MB. Aprox (no cuenta compresion ASTC real)
        mb = (w*h*4*1.33)/(1024*1024) if w and h else 0
        total_mb += mb
        if mb>0:
            nm = str(a.package_name).split("/")[-1]
            sizes.append((round(mb,2), "%dx%d"%(w,h), nm))
    sizes.sort(reverse=True)
    res["tex"] = {"count": n, "est_total_MB_uncompressed": round(total_mb), "mayores_1024": big, "top25": sizes[:25]}
except Exception as e:
    res["err"].append("tex:"+str(e)[:100])

# (2) LUCES en el nivel + mobility
eas = unreal.EditorActorSubsystem()
try:
    for a in eas.get_all_level_actors():
        cn = a.get_class().get_name()
        if "Light" in cn and "Light" != cn[-5:][:0]:
            for c in a.get_components_by_class(unreal.LightComponentBase):
                try:
                    mob = str(a.root_component.get_editor_property("mobility")).split(".")[-1] if a.root_component else "?"
                    res["luces"].append([a.get_actor_label(), cn, mob])
                    break
                except Exception: pass
except Exception as e:
    res["err"].append("luz:"+str(e)[:80])

# (3) CONTEO POR CLASE + (4) particulas + (5) tick
try:
    from collections import Counter
    cc = Counter()
    for a in eas.get_all_level_actors():
        cn = a.get_class().get_name()
        cc[cn]+=1
        if "Particle" in cn or "Niagara" in cn or "Emitter" in cn:
            res["particulas"].append(a.get_actor_label())
    res["clases"] = dict(cc.most_common(30))
except Exception as e:
    res["err"].append("clase:"+str(e)[:80])

open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("DIAG TOTAL ok")
