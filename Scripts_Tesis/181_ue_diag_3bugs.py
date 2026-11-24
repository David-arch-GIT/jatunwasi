# Diag de 3 bugs reportados en visor: cartelas flotando/invisibles, escalera hacienda, entrada templo.
import unreal, json
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
WS=[unreal.ObjectTypeQuery.OBJECT_TYPE_QUERY1]
def floorz(x,y,z0=None):
    import math
    z0 = 3000 if z0 is None else z0
    hrs=unreal.SystemLibrary.line_trace_multi_for_objects(w,unreal.Vector(x,y,z0),unreal.Vector(x,y,z0-4000),WS,True,[],unreal.DrawDebugTrace.NONE,True)
    best=None
    if hrs:
        for hr in hrs:
            t=hr.to_tuple(); z=round(t[5].z); n=(t[9].get_actor_label() if t[9] else "?")
            if "PCG_" in n: continue
            best=(z,n)  # last (lowest)
    return best
R={"cartelas":[], "templo_actores":[], "escalera":[]}
acts=eas.get_all_level_actors()
# A) cartelas
for a in acts:
    cls=a.get_class().get_name()
    if "Cartela" in cls or a.get_actor_label().startswith(("Cart","FN_Cart","Cartela")):
        l=a.get_actor_location()
        vis=None; mz=None
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            try: vis = c.is_visible()
            except Exception:
                try: vis=c.get_editor_property("visible")
                except: vis="?"
            mz=round(c.get_world_location().z)
            break
        g=floorz(l.x,l.y, round(l.z)+200)
        R["cartelas"].append({"lbl":a.get_actor_label(),"z":round(l.z),"panel_vis":vis,
                              "piso_abajo":g, "flota_cm": (round(l.z)-g[0]) if g else None})
# B) templo actores (para ubicar entrada)
import re
trx=re.compile(r"(Templo|Iglesia|TMP|Igle|Church|Presb|Nave|Atrio|Portada|Puerta)", re.I)
for a in acts:
    lbl=a.get_actor_label()
    if trx.search(lbl):
        l=a.get_actor_location()
        R["templo_actores"].append({"lbl":lbl,"cls":a.get_class().get_name(),"loc":[round(l.x),round(l.y),round(l.z)]})
# C) escalera hacienda: perfil
pts={"base":(-7450,-2750),"media":(-7500,-2450),"top_ramp":(-7620,-2320),"bridge":(-7590,-2300),"corredor":(-7150,-1770),"corredor2":(-7400,-1900)}
ns=unreal.NavigationSystemV1
for k,(x,y) in pts.items():
    f=floorz(x,y, 900)
    try:
        r=ns.project_point_to_navigation(w, unreal.Vector(x,y,450), None, None, unreal.Vector(200,200,500))
        nav = None if r is None else round(r.z)
    except: nav="err"
    R["escalera"].append({"pt":k,"xy":[x,y],"piso":f,"nav":nav})
open(out+"/diag_3bugs.json","w").write(json.dumps(R,indent=1))
print("DIAG3", len(R["cartelas"]),"cartelas", len(R["templo_actores"]),"templo")
