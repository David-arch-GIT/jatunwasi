# Inventario para diagnosticar bloqueos: zonas clave + bloqueadores invisibles con colision + pawn.
import unreal, json
OUT=r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/inv_nav.json"
res={"zonas":[], "bloqueadores":[], "escaleras":[], "arcos":[], "pawn":"", "navvols":[]}
eas=unreal.EditorActorSubsystem()
KEYS_ZONA=["Hacienda","Convento","Templo","Iglesia"]
KEYS_ESC=["Escalera","Stair","Grada","Escalinata"]
KEYS_ARCO=["Arco","Arch","Arcada"]
KEYS_BLOCK=["Muro","Blocker","Bloque","Contencion","Colision","Collision","Wall_Invis","InvisWall","Barrera"]
def loc3(a):
    l=a.get_actor_location(); return [round(l.x),round(l.y),round(l.z)]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label()
    cn=a.get_class().get_name()
    low=lbl.lower()
    # zonas (solo 1 muestra por keyword para ubicar)
    for k in KEYS_ZONA:
        if k.lower() in low and len([z for z in res["zonas"] if z["k"]==k])<3:
            res["zonas"].append({"k":k,"label":lbl[:32],"loc":loc3(a)})
    for k in KEYS_ESC:
        if k.lower() in low and len(res["escaleras"])<12:
            res["escaleras"].append({"label":lbl[:32],"loc":loc3(a)}); break
    for k in KEYS_ARCO:
        if k.lower() in low and len(res["arcos"])<20:
            res["arcos"].append({"label":lbl[:32],"loc":loc3(a)}); break
    # bloqueadores: por nombre O primitivas Cube/Plane/Sphere con colision y sin render visible
    isblockname = any(k.lower() in low for k in KEYS_BLOCK)
    prims=a.get_components_by_class(unreal.StaticMeshComponent)
    for c in prims:
        sm=c.get_editor_property("static_mesh")
        smn=sm.get_name() if sm else ""
        if smn in ("Cube","Plane","Sphere","Cylinder") or isblockname:
            try:
                col=c.get_editor_property("collision_enabled")
                hig=c.get_editor_property("hidden_in_game")
            except Exception:
                col="?"; hig="?"
            # solo los que bloquean (tienen colision)
            colstr=str(col)
            if "NO_COLLISION" in colstr:
                continue
            sc=a.get_actor_scale3d()
            if len(res["bloqueadores"])<60:
                res["bloqueadores"].append({"label":lbl[:30],"mesh":smn,"loc":loc3(a),"escala":[round(sc.x,1),round(sc.y,1),round(sc.z,1)],"col":colstr.split(".")[-1].strip(">"),"oculto":bool(hig) if hig!="?" else "?"})
            break
# pawn por defecto del gamemode
try:
    gm=unreal.EditorAssetLibrary.load_asset("/Game/VRTemplate/Blueprints/BP_XRGameMode")
except Exception: gm=None
res["n_bloqueadores"]=len(res["bloqueadores"])
open(OUT,"w").write(json.dumps(res,indent=1))
