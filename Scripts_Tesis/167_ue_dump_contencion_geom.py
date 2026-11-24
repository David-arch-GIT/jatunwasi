# Proyecto: JatunWasi Nawpaqay - Tesis
# Fecha: 2026-11-08  Que hace: vuelca la geometria (AABB en XY) de todas las barreras de
#   contencion + volumenes de NavMesh + footprints de escenarios + PlayerStart, para
#   armar un mapa cenital y detectar HUECOS por donde el jugador podria fugarse al bosque.
# Resultado: Saved/ClaudeBackups/contencion_geom.json
import unreal, json, re
out="C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups"
R={"walls":[],"nav":[],"scen":[],"playerstart":None}
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
wall_re=re.compile(r"(COL_PathWall|COL_PlazaWall|COL_Conv|COL_HACV7|HACV7_EXP_ExteriorWalls|TMP_Wall|GardenFence|COL_Puente|COL_Baile)", re.I)
scen_re=re.compile(r"(EXP_|PLZT_|PLZBF|Templo|Iglesia|Convento|Conv_|Hacienda|HAC_)", re.I)
def aabb(a):
    o,e=a.get_actor_bounds(False)
    return [round(o.x-e.x),round(o.y-e.y),round(o.x+e.x),round(o.y+e.y)]
for a in eas.get_all_level_actors():
    lbl=a.get_actor_label(); cls=a.get_class().get_name()
    if cls=="PlayerStart":
        l=a.get_actor_location(); R["playerstart"]=[round(l.x),round(l.y)]
    if cls=="NavMeshBoundsVolume":
        R["nav"].append({"l":lbl,"b":aabb(a)})
    elif wall_re.search(lbl):
        try:
            rot=a.get_actor_rotation()
            R["walls"].append({"l":lbl,"b":aabb(a),"yaw":round(rot.yaw,1)})
        except Exception: pass
open(out+"/contencion_geom.json","w").write(json.dumps(R))
print("GEOM_DONE", len(R["walls"]), "walls", len(R["nav"]), "nav")
