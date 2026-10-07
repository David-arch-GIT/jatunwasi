import unreal, json, traceback
res={}
try:
    eas=unreal.EditorActorSubsystem()
    mobmap={}
    try:
        mobmap={int(unreal.ComponentMobility.STATIC):"Static",int(unreal.ComponentMobility.STATIONARY):"Stationary",int(unreal.ComponentMobility.MOVABLE):"Movable"}
    except: pass
    agg={}
    examples=[]
    for a in eas.get_all_level_actors():
        cn=a.get_class().get_name()
        if cn not in ("PointLight","SpotLight","RectLight","DirectionalLight"): continue
        comp=None
        for prop in ["light_component","point_light_component","spot_light_component"]:
            try:
                c=a.get_editor_property(prop)
                if c: comp=c; break
            except: pass
        if comp is None:
            for c in a.get_components_by_class(unreal.LightComponentBase):
                comp=c; break
        key=cn
        agg.setdefault(key,{"total":0,"mob":{},"shadow":0,"att_sum":0,"int_sum":0})
        agg[key]["total"]+=1
        if comp:
            try:
                mob=int(comp.get_editor_property("mobility")); mn=mobmap.get(mob,str(mob))
                agg[key]["mob"][mn]=agg[key]["mob"].get(mn,0)+1
            except Exception as e:
                agg[key]["mob"]["err"]=str(e)[:30]
            try:
                if comp.get_editor_property("cast_shadows"): agg[key]["shadow"]+=1
            except: pass
            try: agg[key]["att_sum"]+=float(comp.get_editor_property("attenuation_radius"))
            except: pass
            try: agg[key]["int_sum"]+=float(comp.get_editor_property("intensity"))
            except: pass
            if len(examples)<3 and cn=="PointLight":
                examples.append({"lbl":a.get_actor_label(),"class_comp":comp.get_class().get_name()})
    for k in agg:
        t=agg[k]["total"]
        if t: agg[k]["att_prom"]=round(agg[k]["att_sum"]/t,0); agg[k]["int_prom"]=round(agg[k]["int_sum"]/t,1)
        agg[k].pop("att_sum",None); agg[k].pop("int_sum",None)
    res["luces"]=agg; res["ej"]=examples
except Exception as e:
    res["err"]=traceback.format_exc()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/light_audit.json","w").write(json.dumps(res,indent=1,default=str))
