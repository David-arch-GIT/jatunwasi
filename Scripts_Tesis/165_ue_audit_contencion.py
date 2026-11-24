# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08
# Que hace: AUDITORIA de contencion (0 fuga al bosque). Mide:
#  - NavMeshBoundsVolume(s) y limites del RecastNavMesh (donde puede caer el teletransporte)
#  - Actores que BLOQUEAN al Pawn (barreras de caminar): cercas/muros/invisible walls,
#    agrupados por nombre, con su caja envolvente combinada.
#  - PlayerStart (donde aparece el jugador).
# Resultado: Saved/ClaudeBackups/contencion.json
import unreal, json, traceback
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
R={"navvol":[],"recast":[],"playerstart":[],"barreras_por_nombre":{},"barreras_total":0,"otros_bloqueantes_muestra":[]}
def box(a):
    o,e=a.get_actor_bounds(False)
    return {"c":[round(o.x),round(o.y),round(o.z)],"ext":[round(e.x),round(e.y),round(e.z)]}
try:
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    acts=eas.get_all_level_actors()
    import re
    key_bar=re.compile(r"(COL|Muro|Cerca|Wall|Fence|Invisible|Barrera|Blocking|Contenc)", re.I)
    for a in acts:
        cls=a.get_class().get_name()
        lbl=a.get_actor_label()
        if cls=="NavMeshBoundsVolume":
            R["navvol"].append({"lbl":lbl,**box(a)})
        elif cls in ("RecastNavMesh","NavMeshBoundsVolume"):
            pass
        elif "RecastNavMesh" in cls:
            R["recast"].append({"lbl":lbl,**box(a)})
        elif cls=="PlayerStart":
            l=a.get_actor_location(); R["playerstart"].append({"lbl":lbl,"loc":[round(l.x),round(l.y),round(l.z)]})
        # barreras por nombre
        if key_bar.search(lbl):
            # confirmar que bloquea Pawn
            blocks=False
            for c in a.get_components_by_class(unreal.PrimitiveComponent):
                try:
                    if c.get_collision_enabled() in (unreal.CollisionEnabled.QUERY_AND_PHYSICS, unreal.CollisionEnabled.QUERY_ONLY):
                        if c.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN)==unreal.CollisionResponse.ECR_BLOCK:
                            blocks=True; break
                except Exception: pass
            pref=re.sub(r"[_\-]?\d+$","",lbl)
            d=R["barreras_por_nombre"].setdefault(pref,{"n":0,"bloquea_pawn":0})
            d["n"]+=1
            if blocks: d["bloquea_pawn"]+=1
            R["barreras_total"]+=1
    # recast nav mesh (clase puede variar)
    for a in acts:
        if "NavMesh" in a.get_class().get_name() and a.get_class().get_name()!="NavMeshBoundsVolume":
            try: R["recast"].append({"lbl":a.get_actor_label(),"cls":a.get_class().get_name(),**box(a)})
            except Exception: pass
    open(out+"/contencion.json","w").write(json.dumps(R,indent=1))
    print("CONTENCION_DONE")
except Exception as e:
    R["fatal"]=str(e); R["tb"]=traceback.format_exc()[-400:]
    open(out+"/contencion.json","w").write(json.dumps(R,indent=1)); print("ERR")
