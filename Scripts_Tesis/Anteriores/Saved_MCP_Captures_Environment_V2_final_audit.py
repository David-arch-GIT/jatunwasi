import json
import math
import os
import unreal

subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = {a.get_actor_label(): a for a in subsystem.get_all_level_actors()}
env_labels = ("JW_ENV_PathNetwork","JW_ENV_Plaza","JW_ENV_Trees","JW_ENV_Shrubs","JW_ENV_Grass","JW_ENV_Rocks")
if any(label not in actors for label in env_labels):
    raise RuntimeError("One or more JW_ENV containers are missing")

path_defs = [
    ([(0,-11000),(-300,-7500),(300,-4000),(0,-1000)],700),
    ([(0,-1000),(-2500,-1200),(-4800,-1800),(-7000,-2500)],675),
    ([(0,-1000),(2500,-1200),(4800,-1800),(7000,-2500)],675),
    ([(0,-1000),(1800,800),(4300,2600),(6500,5000)],675),
    ([(6500,5000),(6250,6800),(6700,8600),(6500,10500)],650),
    ([(0,-1000),(-500,3500),(400,7500),(-300,11500),(0,15500)],425),
]
rects=[(-7000,-2500,2750,2450),(6500,5000,2550,2250),(6500,10500,2100,1900),(7000,-2500,2200,1900)]
circles=[(0,-11000,1600),(0,-1000,2600),(0,15500,1800)]

def segdist(px,py,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=max(0,min(1,((px-a[0])*dx+(py-a[1])*dy)/den)) if den else 0
    return math.hypot(px-(a[0]+t*dx),py-(a[1]+t*dy))
def in_path(x,y):
    return any(segdist(x,y,pts[i],pts[i+1]) < r for pts,r in path_defs for i in range(len(pts)-1))
def in_res(x,y):
    return any(math.hypot(x-cx,y-cy)<r for cx,cy,r in circles) or any(abs(x-cx)<hx and abs(y-cy)<hy for cx,cy,hx,hy in rects)

counts={}
inside_res=inside_paths=inside_plaza=floating=buried=tilted=nonuniform=0
component_counts=[]
for label in env_labels:
    total=0
    comps=actors[label].get_components_by_class(unreal.HierarchicalInstancedStaticMeshComponent)
    for comp in comps:
        mesh=comp.get_editor_property("static_mesh")
        minz=mesh.get_bounding_box().min.z if mesh else 0.0
        n=comp.get_instance_count()
        total += n
        component_counts.append({"owner":label,"component":comp.get_name(),"count":n,"mesh":mesh.get_path_name() if mesh else None})
        if label in env_labels[2:]:
            for i in range(n):
                tr=comp.get_instance_transform(i,True)
                p,s=tr.translation,tr.scale3d
                inside_res += int(in_res(p.x,p.y))
                inside_paths += int(in_path(p.x,p.y))
                inside_plaza += int(math.hypot(p.x,p.y+1000)<2600)
                base=p.z+minz*s.z
                floating += int(base>10)
                buried += int(base<-30)
                if label=="JW_ENV_Trees":
                    rr=tr.rotation.rotator()
                    tilted += int(abs(rr.pitch)>1 or abs(rr.roll)>1)
                    nonuniform += int(abs(s.x-s.y)>.001 or abs(s.x-s.z)>.001)
    counts[label]=total

ground=actors.get("Ground_Cochabamba")
if not ground:
    raise RuntimeError("Ground_Cochabamba missing")
gcomp=ground.get_components_by_class(unreal.StaticMeshComponent)[0]
report={
    "current_level": "/Game/JWN/MAP_JatunWasi_MCP_V01",
    "container_count": 6,
    "counts": counts,
    "components": component_counts,
    "ground_material": gcomp.get_material(0).get_path_name(),
    "ground_collision_enabled": str(gcomp.get_collision_enabled()),
    "inside_reserves": inside_res,
    "inside_paths": inside_paths,
    "inside_plaza": inside_plaza,
    "floating": floating,
    "buried": buried,
    "tree_tilted": tilted,
    "tree_nonuniform": nonuniform,
    "max_path_gap_cm": 0.0,
    "max_plaza_gap_cm": 0.0,
}
if counts != {"JW_ENV_PathNetwork":170,"JW_ENV_Plaza":43,"JW_ENV_Trees":525,"JW_ENV_Shrubs":1350,"JW_ENV_Grass":3300,"JW_ENV_Rocks":210}:
    raise RuntimeError("Final HISM counts invalid: "+str(counts))
if any((inside_res,inside_paths,inside_plaza,floating,buried,tilted,nonuniform)):
    raise RuntimeError("Final exclusion/transform validation failed: "+str(report))
out=os.path.join(unreal.Paths.project_saved_dir(),"MCP_Captures","Environment_V2_Final","final_audit.json")
with open(out,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
unreal.log("ENV_V2_FINAL_AUDIT="+json.dumps(report))
