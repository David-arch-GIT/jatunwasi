import unreal, json, re, traceback
res={"removed":0,"kept":0,"detalle":{}}
try:
    eas=unreal.EditorActorSubsystem()
    groups={}
    for a in eas.get_all_level_actors():
        if a.get_class().get_name()=="PointLight":
            lbl=a.get_actor_label(); g=re.sub(r"[_\d]+$","",lbl)
            groups.setdefault(g,[]).append(a)
    for g,acts in groups.items():
        n=len(acts)
        if n>4:
            acts.sort(key=lambda a:(a.get_actor_location().x, a.get_actor_location().y))
            keep_n=(n+1)//2  # mitad (techo)
            if keep_n<=1: keep_idx={0}
            else: keep_idx=set(round(i*(n-1)/(keep_n-1)) for i in range(keep_n))
            rem=0
            for i,a in enumerate(acts):
                if i in keep_idx: res["kept"]+=1
                else: eas.destroy_actor(a); res["removed"]+=1; rem+=1
            res["detalle"][g]="%d -> %d"%(n, n-rem)
        else:
            res["kept"]+=n
    res["total_despues"]=res["kept"]
except Exception as e:
    res["err"]=traceback.format_exc()
open(r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/thin_lights.json","w").write(json.dumps(res,indent=1,default=str))
