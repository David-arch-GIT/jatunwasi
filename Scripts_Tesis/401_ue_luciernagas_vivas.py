# 401_ue_luciernagas_vivas.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: luciernagas "vivas" fuera del camino. Todo el movimiento y el brillo viven en el
#   material (GPU): cada instancia usa PerInstanceRandom para tener su propio recorrido
#   (bucles de Lissajous que no se repiten, velocidad propia) y destellos suaves con pausas
#   irregulares. Unlit aditivo, sin luces reales, sin sombras, sin colision.
#   Malla SM_ForestRock_04 (36 vertices) escalada ~3 cm. Actor RELLENO_Luciernagas (tag RELLENO).
# Uso: DRY = True/False.
import unreal, json, math, random, traceback
try:
    DRY
except NameError:
    DRY = True
OUT = r"C:/UnrealProjects/JatunWasiNawpakay/Saved/ClaudeBackups/luciernagas.json"
world = unreal.EditorLevelLibrary.get_editor_world()
res = {"dry": DRY, "err": None}
MAT = "/Game/JWN/FX/M_Luciernaga"
MESH = "/Game/StylescapeHD/Foliage/Forest/SM_ForestRock_04"
N_TARGET = 450

def ci(name):
    c = unreal.CustomInput()
    c.set_editor_property("input_name", name)
    return c

def make_material():
    mel = unreal.MaterialEditingLibrary
    if unreal.EditorAssetLibrary.does_asset_exist(MAT):
        unreal.EditorAssetLibrary.delete_asset(MAT)
    m = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Luciernaga", "/Game/JWN/FX", unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
    m.set_editor_property("two_sided", True)
    m.set_editor_property("used_with_instanced_static_meshes", True)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 0)
    r = mel.create_material_expression(m, unreal.MaterialExpressionPerInstanceRandom, -900, 200)
    wpo = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 300)
    wpo.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    wpo.set_editor_property("code",
        "float s = 0.65 + R * 0.7; float tt = T * s; float a = R * 61.7; float b = R * 23.3;"
        "return float3(sin(tt*0.37+a)*55.0 + sin(tt*0.91+b)*22.0,"
        " cos(tt*0.29+b)*55.0 + sin(tt*0.73+a)*22.0,"
        " sin(tt*0.53+a*0.5)*30.0 + sin(tt*1.31+b)*10.0);")
    wpo.set_editor_property("inputs", [ci("T"), ci("R")])
    mel.connect_material_expressions(t, "", wpo, "T"); mel.connect_material_expressions(r, "", wpo, "R")
    mel.connect_material_property(wpo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    br = mel.create_material_expression(m, unreal.MaterialExpressionCustom, -500, -150)
    br.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    br.set_editor_property("code",
        "float t = T * (0.8 + R * 0.7) + R * 97.0;"
        "float p = pow(saturate(sin(t)), 12.0);"
        "float q = pow(saturate(sin(t * 0.37 + R * 13.0) * 0.5 + 0.6), 2.0);"
        "return 0.05 + p * q * 1.2;")
    br.set_editor_property("inputs", [ci("T"), ci("R")])
    mel.connect_material_expressions(t, "", br, "T"); mel.connect_material_expressions(r, "", br, "R")
    col = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, -500, -350)
    col.set_editor_property("constant", unreal.LinearColor(0.65, 1.0, 0.2, 1.0))
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, -250)
    mel.connect_material_expressions(col, "", mul, "A"); mel.connect_material_expressions(br, "", mul, "B")
    mul2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -100, -250)
    mul2.set_editor_property("const_b", 14.0)
    mel.connect_material_expressions(mul, "", mul2, "A")
    mel.connect_material_property(mul2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    unreal.EditorAssetLibrary.save_asset(MAT, False)
    return m

def nav_dist(x, y, ext):
    q = unreal.NavigationSystemV1.project_point_to_navigation(world, unreal.Vector(x, y, 100), None, None, unreal.Vector(ext, ext, 600))
    loc = q[0] if isinstance(q, tuple) else q
    return None if loc is None else math.hypot(loc.x - x, loc.y - y)

def ground_z(x, y):
    h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 3000), unreal.Vector(x, y, -3000),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    t = h.to_tuple() if isinstance(h, unreal.HitResult) else None
    return t[4].z if (t and t[0]) else None

try:
    # vegetacion (las luciernagas se juntan cerca de arbustos/arboles)
    veg = {}
    big = []
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        isms = a.get_components_by_class(unreal.InstancedStaticMeshComponent)
        for c in isms:
            sm = c.get_editor_property("static_mesh"); n = sm.get_name() if sm else ""
            if any(k in n for k in ("Bush", "Plant", "Tree", "Maple", "Oak", "Fern", "Grass")) and a.get_actor_label() != "RELLENO_Horizonte":
                for i in range(c.get_instance_count()):
                    p = c.get_instance_transform(i, True).translation
                    veg.setdefault((int(p.x // 400), int(p.y // 400)), 0)
                    veg[(int(p.x // 400), int(p.y // 400))] += 1
        if not isms and a.get_components_by_class(unreal.StaticMeshComponent):
            o, e = a.get_actor_bounds(False)
            if (e.x > 250 or e.y > 250) and e.x < 8000 and e.y < 8000 and e.z > 60:
                big.append((o.x - e.x - 200, o.x + e.x + 200, o.y - e.y - 200, o.y + e.y + 200))
    random.seed(401)
    pts = []
    tries = 0
    while len(pts) < N_TARGET and tries < 20000:
        tries += 1
        x = random.uniform(-12000, 12000); y = random.uniform(-6000, 16000)
        d = nav_dist(x, y, 2500)
        if d is None or d < 300:
            continue
        if any(b[0] < x < b[1] and b[2] < y < b[3] for b in big):
            continue
        dens = veg.get((int(x // 400), int(y // 400)), 0)
        p_ok = 0.85 if dens >= 2 else (0.45 if dens == 1 else 0.15)
        if random.random() > p_ok:
            continue
        z = ground_z(x, y)
        if z is None:
            continue
        pts.append((x, y, z + random.uniform(40, 210), random.uniform(0.06, 0.09)))
    res["count"] = len(pts); res["tries"] = tries
    if not DRY:
        mat = make_material()
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
        actor.set_actor_label("RELLENO_Luciernagas")
        actor.tags = [unreal.Name("RELLENO")]
        sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
        root = sds.k2_gather_subobject_data_for_instance(actor)[0]
        h, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root,
            new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
        comp = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h))
        comp.set_static_mesh(unreal.load_asset(MESH))
        for i in range(comp.get_num_materials()):
            comp.set_material(i, mat)
        comp.set_mobility(unreal.ComponentMobility.STATIC)
        comp.set_editor_property("cast_shadow", False)
        comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        comp.set_editor_property("can_ever_affect_navigation", False)
        comp.set_editor_property("instance_start_cull_distance", 2400)
        comp.set_editor_property("instance_end_cull_distance", 3000)
        comp.set_editor_property("bounds_scale", 4.0)
        comp.add_instances([unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, 0), unreal.Vector(s, s, s))
                            for (x, y, z, s) in pts], False, True)
        res["made"] = comp.get_instance_count()
        res["materials"] = [comp.get_material(i).get_name() for i in range(comp.get_num_materials())]
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:900]
open(OUT, "w").write(json.dumps(res, indent=1))

