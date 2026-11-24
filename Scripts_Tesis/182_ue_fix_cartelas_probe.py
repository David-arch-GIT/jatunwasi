import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
ns=unreal.NavigationSystemV1
R={"cartelas_visibles":0, "templo_perfil":[]}
# A) FIX cartelas: hacer visibles todos los meshes del BP_Cartela
for a in eas.get_all_level_actors():
    cls=a.get_class().get_name()
    if "Cartela" in cls or a.get_actor_label().startswith("Cartela"):
        ch=False
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            try:
                c.set_visibility(True, True)
                c.set_hidden_in_game(False, True)
                ch=True
            except Exception: pass
        if ch: R["cartelas_visibles"]+=1
# B) perfil de la ENTRADA del templo (de sur/camino hacia la nave)
def stack(x,y,z0=1200,z1=-300):
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,z0),unreal.Vector(x,y,z1),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    r=[]
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=round(t[5].z); n=(t[9].get_actor_label() if t[9] else "?")
            if "PCG_" in n: continue
            r.append([z,n])
    return r
def nav(x,y,z=60):
    rr=ns.project_point_to_navigation(w,unreal.Vector(x,y,z),None,None,unreal.Vector(200,200,500))
    return None if rr is None else round(rr.z)
yy=8000
while yy<=12000:
    st=stack(50,yy)
    top=None
    for z,n in st:
        if top is None or z>top[0]:
            if z<300: top=[z,n]
    R["templo_perfil"].append({"y":yy,"piso":top,"nav":nav(50,yy),"stack":st[:4]})
    yy+=400
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
open(out+"/fix_cartelas.json","w").write(json.dumps(R,indent=1))
print("CART_FIX", R["cartelas_visibles"])
