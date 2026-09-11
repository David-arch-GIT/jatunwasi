# Proyecto: JatunWasi Nawpaqay - Tesis de grado
# Fecha de uso: 2026-08-24 15:30
# Que hace este script: Cuenta luces totales y calcula solapamiento por zona.
# Por que se necesito: Medir el impacto real en Quest 2.
# Resultado obtenido: 141 luces, solape 12 en la Hacienda.
# ------------------------------------------------------------

import unreal, json
eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
zones={'Plaza':[],'Caminos':[],'Hacienda':[],'Convento':[],'Templo':[],'Otro':[]}
total=0; shadows=0
def zone_of(l):
    if l.startswith('LP_'): return 'Plaza'
    if l.startswith('LC_'): return 'Caminos'
    if l.startswith('APL_'): return 'Convento' if any(k in l for k in ['Refect','Celdas','ClaustG','Capilla']) else 'Hacienda'
    if l.startswith('LH_') or l.startswith('FILL_Hac') or l.startswith('GAL_'): return 'Hacienda'
    if l.startswith('LCV_') or l.startswith('FILL_Cv'): return 'Convento'
    if l.startswith(('Spot_Retablo','NaveFill_','LT_')): return 'Templo'
    return 'Otro'
for a in eas.get_all_level_actors():
    for c in a.get_components_by_class(unreal.LightComponentBase):
        if c.get_class().get_name() not in ('PointLightComponent','SpotLightComponent'): continue
        total+=1
        if bool(c.get_editor_property('cast_shadows')): shadows+=1
        loc=a.get_actor_location()
        zones[zone_of(a.get_actor_label())].append({'x':loc.x,'y':loc.y,'z':loc.z,'r':c.get_editor_property('attenuation_radius')})
def worst(ls):
    if not ls: return 0
    xs=[l['x'] for l in ls];ys=[l['y'] for l in ls];zs=[l['z'] for l in ls]
    x0,x1=min(xs)-100,max(xs)+100;y0,y1=min(ys)-100,max(ys)+100;z0,z1=min(zs)-100,max(zs)+100
    sx=max(60,(x1-x0)/26);sy=max(60,(y1-y0)/26);sz=max(60,(z1-z0)/10);W=0
    zz=z0
    while zz<=z1:
        yy=y0
        while yy<=y1:
            xx=x0
            while xx<=x1:
                cc=sum(1 for l in ls if (xx-l['x'])**2+(yy-l['y'])**2+(zz-l['z'])**2<=l['r']*l['r'])
                if cc>W: W=cc
                xx+=sx
            yy+=sy
        zz+=sz
    return W
out={'total_dynamic_lights':total,'shadows_on':shadows,
     'counts':{z:len(v) for z,v in zones.items()},
     'overlap':{z:worst(v) for z,v in zones.items()}}
open(r'C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/p1t.json','w').write(json.dumps(out,indent=1))
