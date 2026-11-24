# 439_ue_convento_amoblar.py
# Proyecto: Jatun Wasi Nawpa Kay (tesis VR Quest 2)
# Fecha: 2026-11-24
# Proposito: ENRIQUECER el convento (la usuaria: "esta pobre ese lugar") con mobiliario de calidad
#   (Megascans fotoescaneados, vasijas de barro, Tripo) organizado como vida conventual real:
#   - REFECTORIO (galeria este x 7625-7975): mesa larga (8 mesas en fila) contra la pared + 4 bancas,
#     vasijas sobre la mesa, mesa de lectura con atril y 2 cirios al fondo.
#   - PORTICO OESTE (x 4700-5000, abierto al exterior): bancas de espera, cantaro, tinaja, arcon.
#   - COCINA (galeria norte y 6290-6620): cocina de barro, lena, tinajas, cantaros, mesa de trabajo con
#     ollas, batan, aparador.
#   - PATIO: 4 canteros de amarilis + pasto alrededor del pozo, 3 bancas mirando al pozo, 8 macetas.
#   Quest: UN actor CONV_MOBILIARIO con un HISM por malla (pocas draw calls), sin sombras, culling,
#   colision solo-consulta en muebles (el rayo de locomocion los respeta), sin efecto en NavMesh,
#   texturas Megascans limitadas a 1024. Respaldo del .umap. Reversible (borrar el actor).
import unreal, json, math, random, shutil, os, traceback
ROOT = r"C:/UnrealProjects/JatunWasiNawpakay"
OUT = ROOT + r"/Saved/ClaudeBackups/convento_amoblar.json"
MS = "/Game/Megascans/3D_Assets/"; PL = "/Game/Megascans/3D_Plants/"
M = {
    "banca": MS + "Old_Wooden_Bench_ucvpfirfa/S_Old_Wooden_Bench_ucvpfirfa_lod3",
    "mesa": MS + "Wooden_Table_veigfjmaw/S_Wooden_Table_veigfjmaw_lod3_Var1",
    "silla": MS + "Woven_Chair_wjglah2s/S_Woven_Chair_wjglah2s_lod3_Var1",
    "estante": MS + "Wooden_Bookshelf_vmjhbix/S_Wooden_Bookshelf_vmjhbix_lod3",
    "arcon": MS + "Wooden_Chest_vignaajva/S_Wooden_Chest_vignaajva_lod3_Var1",
    "libro": MS + "Old_Book_wldocam/S_Old_Book_wldocam_lod3_Var1",
    "libro2": MS + "Book_wldodgk/S_Book_wldodgk_lod3_Var1",
    "cirio": "/Game/JWN/Templo/Kit_Cirio",
    "atril": "/Game/JWN/Convento/TripoClean/atril_de_biblia/StaticMeshes/atril_de_biblia",
    "cocina": "/Game/JWN/TripoClean2/cocina_de_barro_hacienda/StaticMeshes/cocina_de_barro_hacienda",
    "batan": "/Game/JWN/TripoClean2/batan_de_piedra_hacienda/StaticMeshes/batan_de_piedra_hacienda",
    "lena": "/Game/JWN/Props/Furniture/G_Lena/FN_Lena/StaticMeshes/FN_Lena",
    "aparador": "/Game/JWN/Props/Furniture/G_Aparador/FN_Aparador/StaticMeshes/FN_Aparador",
    "tinaja": "/Game/JWN/Props/Vessels/G_V_Tinaja/V_Tinaja/StaticMeshes/V_Tinaja",
    "cantaro": "/Game/JWN/Props/Vessels/G_V_Cantaro/V_Cantaro/StaticMeshes/V_Cantaro",
    "olla": "/Game/JWN/Props/Vessels/G_V_Olla/V_Olla/StaticMeshes/V_Olla",
    "jarron": "/Game/JWN/Props/Vessels/G_V_Jarron/V_Jarron/StaticMeshes/V_Jarron",
    "maceta": "/Game/JWN/Props/Vessels/G_V_Maceta/V_Maceta/StaticMeshes/V_Maceta",
    "pasto": PL + "Grass_Clumps_qmBr2/S_Grass_Clumps_qmBr2_Var2_lod1",
}
for v in (1, 3, 4, 5, 6, 7, 8):
    M["flor%d" % v] = PL + "Amaryllis_sgzkv/S_Amaryllis_sgzkv_Var%d_lod1" % v
SOLID = {"banca", "mesa", "silla", "estante", "arcon", "cirio", "cocina", "batan", "lena", "aparador", "tinaja", "maceta"}
CULL = {"libro": 1200, "libro2": 1200, "olla": 1800, "cantaro": 1800, "jarron": 1800, "pasto": 2200}
res = {"err": None}
try:
    if not os.path.exists(ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_convento_20261124.umap"):
        shutil.copy2(ROOT + "/Content/JWN/MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN.umap", ROOT + "/Saved/ClaudeBackups/MAP_CLEAN_pre_convento_20261124.umap")
    world = unreal.EditorLevelLibrary.get_editor_world()
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        if a.get_actor_label() == "CONV_MOBILIARIO":
            unreal.EditorLevelLibrary.destroy_actor(a)
    IGN = []   # v3: el suelo se mide ignorando el propio mobiliario (antes las vasijas quedaban 75 cm sobre la mesa)
    def floor(x, y):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 250), unreal.Vector(x, y, -60), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, IGN, unreal.DrawDebugTrace.NONE, True)
        t = h.to_tuple() if h else None
        return t[4].z if (t and t[0]) else 10.0
    P = []   # (clave, x, y, dz, yaw, escala)
    # ---- REFECTORIO ----
    for k in range(4):
        P.append(("banca", 7940, 4700 + k * 235, 0, 90, 1.0))
    for k in range(8):
        P.append(("mesa", 7845, 4640 + k * 107, 0, 90, 1.15))
    for k, it in enumerate(("cantaro", "olla", "jarron", "olla", "cantaro", "jarron", "olla")):
        P.append((it, 7845 + random.uniform(-12, 12), 4680 + k * 120, 75, random.uniform(0, 360), 0.8))
    P += [("mesa", 7800, 6020, 0, 0, 1.15), ("atril", 7800, 6020, 75, 180, 0.55), ("libro", 7800, 6020, 98, 0, 1.6),
          ("cirio", 7690, 6040, 0, 0, 1.0), ("cirio", 7910, 6040, 0, 0, 1.0)]
    # ---- PORTICO OESTE (v2: es un portico abierto al exterior, no una sala -> bancas de espera) ----
    P += [("banca", 4960, 4500, 0, 270, 1.0), ("banca", 4960, 4735, 0, 270, 1.0), ("banca", 4960, 5650, 0, 270, 1.0),
          ("banca", 4960, 5885, 0, 270, 1.0), ("cantaro", 4960, 5150, 0, 0, 1.0), ("tinaja", 4955, 5230, 0, 30, 0.9),
          ("arcon", 4960, 6150, 0, 270, 1.1)]
    # ---- COCINA ----
    P += [("cocina", 5330, 6560, 0, 180, 1.8), ("lena", 5560, 6585, 0, 15, 1.2), ("lena", 5615, 6560, 0, 70, 1.0),
          ("tinaja", 5790, 6585, 0, 0, 1.0), ("tinaja", 5870, 6590, 0, 40, 0.9), ("cantaro", 5150, 6590, 0, 0, 1.0),
          ("cantaro", 5205, 6600, 0, 60, 0.9), ("mesa", 6120, 6580, 0, 0, 1.15), ("olla", 6090, 6580, 75, 0, 0.9),
          ("olla", 6150, 6575, 75, 30, 0.8), ("jarron", 6170, 6595, 75, 0, 0.7), ("batan", 6420, 6575, 0, 0, 0.9),
          ("aparador", 6720, 6610, 0, 180, 1.0)]
    # ---- PATIO ----
    random.seed(439)
    PX, PY = 6250, 4849
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        cx, cy = PX + sx * 330, PY + sy * 330
        for k in range(6):
            v = random.choice((1, 3, 4, 5, 7, 8))
            P.append(("flor%d" % v, cx + random.uniform(-80, 80), cy + random.uniform(-80, 80), 0, random.uniform(0, 360), random.uniform(0.85, 1.1)))
        for k in range(4):
            P.append(("pasto", cx + random.uniform(-130, 130), cy + random.uniform(-130, 130), 0, random.uniform(0, 360), random.uniform(0.9, 1.3)))
    # v4: la banca sur bloqueaba el paso directo entrada->pozo; ahora al oeste (antes de la escalera)
    P += [("banca", PX - 560, PY - 330, 0, 90, 1.0), ("banca", PX, PY + 620, 0, 180, 1.0), ("banca", PX + 640, PY, 0, 270, 1.0)]
    for x in (5150, 7475):
        for y in (4200, 4850, 5500, 6100):
            P.append(("maceta", x, y, 0, random.uniform(0, 360), 1.3))
            P.append(("flor6", x, y, 30, random.uniform(0, 360), 0.6))
    # ---- crear HISM ----
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.Actor, unreal.Vector(0, 0, 0))
    IGN.append(actor)
    actor.set_actor_label("CONV_MOBILIARIO"); actor.tags = [unreal.Name("RELLENO"), unreal.Name("RELLENO_CONVENTO")]
    actor.set_folder_path("Convento_Mobiliario")
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
    root = sds.k2_gather_subobject_data_for_instance(actor)[0]
    groups = {}
    for key, x, y, dz, yaw, s in P:
        groups.setdefault(key, []).append((x, y, dz, yaw, s))
    tex_done = set(); counts = {}
    for key, items in groups.items():
        sm = unreal.load_asset(M[key])
        if sm is None:
            res.setdefault("missing", []).append(key); continue
        hh, fail = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
        c = lib.get_object(lib.get_data(hh))
        c.set_static_mesh(sm); c.set_mobility(unreal.ComponentMobility.STATIC)
        c.set_editor_property("cast_shadow", False); c.set_editor_property("can_ever_affect_navigation", key in SOLID)  # v4: muebles recortan el NavMesh
        if key in SOLID:
            if unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).get_simple_collision_count(sm) == 0:
                unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem).add_simple_collisions(sm, unreal.ScriptingCollisionShapeType.BOX)
            c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            c.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_BLOCK)
        else:
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        c.set_editor_property("instance_end_cull_distance", CULL.get(key, 3200))
        tfs = []
        for x, y, dz, yaw, s in items:
            z = floor(x, y) + dz
            tfs.append(unreal.Transform(unreal.Vector(x, y, z), unreal.Rotator(0, 0, yaw), unreal.Vector(s, s, s)))
        c.add_instances(tfs, False, True)
        counts[key] = len(tfs)
        if M[key].startswith("/Game/Megascans"):
            for i in range(len(sm.static_materials)):
                mi = sm.static_materials[i].material_interface
                if mi is None: continue
                texs = [tp.parameter_value for tp in mi.get_editor_property("texture_parameter_values") if tp.parameter_value] if isinstance(mi, unreal.MaterialInstanceConstant) else list(unreal.MaterialEditingLibrary.get_used_textures(mi))
                for t in texs:
                    if t.get_path_name() in tex_done: continue
                    tex_done.add(t.get_path_name())
                    if t.get_editor_property("max_texture_size") == 0 or t.get_editor_property("max_texture_size") > 1024:
                        t.set_editor_property("max_texture_size", 1024)
                        unreal.EditorAssetLibrary.save_loaded_asset(t, False)
    res["counts"] = counts; res["total"] = sum(counts.values()); res["components"] = len(counts); res["tex_1024"] = len(tex_done)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
except Exception:
    res["err"] = traceback.format_exc()[:1500]
open(OUT, "w").write(json.dumps(res))
