# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-09-02
# Que hace: (UE) Investiga los 2 huecos de colision: (A) escalera->2do piso (landing vs corredor superior vs top escalera)
#   y (B) entrada principal (piso hacienda vs camino/sendero cerca del PlayerStart). Reporta bounds + colision.
# ------------------------------------------------------------
import unreal, json, math
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/huecos.json"
res = {"escalera_2p": {}, "entrada": {}, "cerca_playerstart": [], "err": []}
eas = unreal.EditorActorSubsystem()
def binfo(a):
    o, e = a.get_actor_bounds(False)
    ce = "-"
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        try: ce = str(c.get_collision_enabled()).split(".")[-1]
        except Exception: pass
    return {"loc":[round(a.get_actor_location().x),round(a.get_actor_location().y),round(a.get_actor_location().z)],
            "z":[round(o.z-e.z),round(o.z+e.z)], "x":[round(o.x-e.x),round(o.x+e.x)],
            "y":[round(o.y-e.y),round(o.y+e.y)], "col":ce}
TARGETS_ESC = ["HACV7_EXP_Staircase","COL_HACV7_StairLanding","COL_HACV7_UpperCorridor"]
TARGETS_ENT = ["HACV7_EXP_Foundation_Floors"]
PS = (-6200,-2500)
for a in eas.get_all_level_actors():
    l = a.get_actor_label()
    try:
        if l in TARGETS_ESC:
            res["escalera_2p"][l] = binfo(a)
        if l in TARGETS_ENT:
            res["entrada"][l] = binfo(a)
        # actores cerca del PlayerStart (entrada) para hallar el camino/sendero
        loc = a.get_actor_location()
        if math.hypot(loc.x-PS[0], loc.y-PS[1]) < 900 and a.get_class().get_name() in ("StaticMeshActor","Actor"):
            low = l.lower()
            if any(k in low for k in ["camino","sendero","path","piso","floor","suelo","ground","hac"]):
                res["cerca_playerstart"].append({"label":l, **binfo(a)})
    except Exception as e:
        res["err"].append(l+":"+str(e)[:40])
open(OUT,"w").write(json.dumps(res, indent=1))
unreal.log("HUECOS ok")
