# Reduce densidad del bosque: sotobosque -40%, arboles -20% (horizonte sigue lleno). remove_instances batch.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/adelgazar.json"
res={"antes":0,"despues":0,"detalle":[]}
eas=unreal.EditorActorSubsystem()
SOTO=["Grass","Fern","Bush","Plant","Flower","Mossy"]   # -40%
ARB=["Maple","Oak","Tropical","Palm","Dead_Tree"]        # -20%
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.InstancedStaticMeshComponent):
        sm=c.get_editor_property("static_mesh")
        if not sm: continue
        mn=sm.get_name()
        try: n=c.get_instance_count()
        except Exception: n=0
        if n<20: continue
        es_soto=any(k in mn for k in SOTO)
        es_arb=any(k in mn for k in ARB)
        if not (es_soto or es_arb): continue
        res["antes"]+=n
        # indices a remover, distribuidos parejo
        if es_soto:
            rem=[i for i in range(n) if i%5<2]   # ~40%
        else:
            rem=[i for i in range(n) if i%5==0]  # ~20%
        try:
            c.remove_instances(rem)
            nn=c.get_instance_count()
            res["despues"]+=nn
            if len(res["detalle"])<25:
                res["detalle"].append({"mesh":mn,"de":n,"a":nn})
        except Exception as e:
            res["despues"]+=n
            res["detalle"].append({"mesh":mn,"err":str(e)[:40]})
res["reduccion_pct"]=round(100*(1-res["despues"]/max(res["antes"],1)),1)
open(OUT,"w").write(json.dumps(res,indent=1))
