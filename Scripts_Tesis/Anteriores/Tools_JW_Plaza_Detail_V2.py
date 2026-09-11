# -*- coding: utf-8 -*-
"""
JATUNWASI - PLAZA DETAIL PASS V2
Unreal Engine 5 Editor Python

OBJETIVO
--------
Completar el detallado visual de la plaza actual en:
MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN

Este pase intenta:
1) Mejorar la apariencia del suelo/jardineras mediante materiales existentes.
2) Poblar las 4 jardineras con flores, arbustos y acentos vegetales.
3) Añadir macetas decorativas y vegetación perimetral.
4) Reforzar los bordes de caminos con rocas y plantas bajas.
5) NO tocar bancas, asientos, postes ni faroles existentes.
6) Mantener despejados el anillo central y la circulación principal.
7) Dejar todo lo nuevo agrupado en: JatunWasi/Plaza_Detail_V2
8) NO guardar el nivel automáticamente.

NOTA
----
El script es deliberadamente robusto:
- Reutiliza meshes y materiales YA presentes en el proyecto cuando es posible.
- Si una categoría no se encuentra, la omite en lugar de inventar assets erróneos.
- Está pensado para iteración visual controlada en editor.

Autor lógico del pase:
ChatGPT - continuidad del proyecto JatunWasi Hacienda/Plaza
"""

import unreal
import math
import random

# ============================================================
# CONFIGURACION GENERAL
# ============================================================

LEVEL_EXPECTED_NAME = "MAP_JatunWasi_MCP_V08_HaciendaFix_CLEAN"
ROOT_FOLDER = "JatunWasi/Plaza_Detail_V2"

PLAZA_LABEL = "JW_ENV_Plaza"
PATH_LABEL = "JW_ENV_PathNetwork"
SHRUBS_LABEL = "JW_ENV_Shrubs"
TREES_LABEL = "JW_ENV_Trees"
ROCKS_LABEL = "JW_ENV_Rocks"
GRASS_LABEL = "JW_ENV_Grass"

# Respaldo geométrico si el actor de plaza no devuelve bounds útiles
FALLBACK_CENTER = unreal.Vector(0.0, -1000.0, 12.0)
PLAZA_YAW_DEG = -167.905243
DEFAULT_HALF_SIZE = 1500.0
MIN_HALF_SIZE = 1200.0
MAX_HALF_SIZE = 1900.0

# Z base para nuevos detalles (ajuste simple)
BASE_Z_OFFSET = 2.0

# Protección de circulación / fuente
CENTER_CLEAR_RADIUS = 620.0
MAIN_AXIS_HALF_WIDTH = 220.0
PRESERVED_ACTOR_CLEARANCE = 145.0

# Espaciados mínimos para decoraciones nuevas
TREE_SPACING = 320.0
SHRUB_SPACING = 135.0
FLOWER_SPACING = 95.0
ROCK_SPACING = 180.0
POT_SPACING = 120.0

# Cantidades moderadas (Quest 2 friendly pero visualmente ricas)
TREE_TARGET = 12
SHRUB_TARGET = 20
FLOWER_TARGET = 32
ROCK_TARGET = 12
POT_TARGET = 10
BORDER_PLANT_TARGET = 18

SEED = 260809
random.seed(SEED)

# Etiquetas que NO debemos tocar
PRESERVE_LABEL_WORDS = (
    "bench", "banca", "seat", "asiento",
    "lamp", "lamppost", "farol", "poste", "lightpost"
)

# Palabras de clasificación para meshes
TREE_WORDS = (
    "tree", "arbol", "eucalyptus", "eucal", "pine", "oak",
    "birch", "acacia", "cypress", "willow", "maple"
)
SHRUB_WORDS = (
    "shrub", "bush", "hedge", "topiary", "plant", "foliage"
)
FLOWER_WORDS = (
    "flower", "flor", "rose", "lavender", "petunia", "garden"
)
POT_WORDS = (
    "pot", "planter", "maceta", "urn", "vase"
)
ROCK_WORDS = (
    "rock", "stone", "boulder", "piedra"
)

# Palabras para materiales
SOIL_MATERIAL_WORDS = (
    "soil", "dirt", "ground", "earth", "mud", "garden"
)
STONE_MATERIAL_WORDS = (
    "stone", "cobble", "tile", "paver", "slate", "rock"
)

# ============================================================
# HELPERS
# ============================================================

actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
editor_level_lib = unreal.EditorLevelLibrary
asset_lib = unreal.EditorAssetLibrary

def log(msg):
    unreal.log("[JW_PLAZA_V2] {}".format(msg))

def warn(msg):
    unreal.log_warning("[JW_PLAZA_V2] {}".format(msg))

def get_world():
    return editor_level_lib.get_editor_world()

def all_actors():
    return list(actor_subsystem.get_all_level_actors())

def actor_label(actor):
    try:
        return actor.get_actor_label()
    except Exception:
        try:
            return actor.get_name()
        except Exception:
            return "UnknownActor"

def find_actor_exact(label):
    for a in all_actors():
        if actor_label(a) == label:
            return a
    return None

def get_components(actor, cls):
    try:
        return list(actor.get_components_by_class(cls))
    except Exception:
        return []

def get_all_mesh_components(actor):
    comps = []
    comps.extend(get_components(actor, unreal.StaticMeshComponent))
    comps.extend(get_components(actor, unreal.InstancedStaticMeshComponent))
    comps.extend(get_components(actor, unreal.HierarchicalInstancedStaticMeshComponent))
    return comps

def get_static_meshes_from_actor(actor):
    meshes = []
    seen = set()
    for c in get_all_mesh_components(actor):
        try:
            mesh = c.get_editor_property("static_mesh")
            if mesh:
                path = mesh.get_path_name()
                if path not in seen:
                    meshes.append(mesh)
                    seen.add(path)
        except Exception:
            pass
    return meshes

def list_project_material_assets():
    # Puede haber muchos assets; en proyectos medianos esto suele ser tolerable.
    # Buscamos solo Material y MaterialInstanceConstant.
    out = []
    classes = ["Material", "MaterialInstanceConstant"]
    for class_name in classes:
        try:
            assets = asset_registry.get_assets_by_class(class_name, True)
        except Exception:
            assets = []
        out.extend(assets)
    return out

def asset_name(asset_data):
    try:
        return str(asset_data.asset_name)
    except Exception:
        return ""

def asset_path(asset_data):
    try:
        return asset_data.object_path.string
    except Exception:
        try:
            return str(asset_data.object_path)
        except Exception:
            return ""

def load_asset_from_data(asset_data):
    try:
        path = asset_path(asset_data)
        if not path:
            return None
        return asset_lib.load_asset(path)
    except Exception:
        return None

def classify_meshes(meshes):
    groups = {
        "tree": [],
        "shrub": [],
        "flower": [],
        "pot": [],
        "rock": [],
    }

    for mesh in meshes:
        text = (mesh.get_name() + " " + mesh.get_path_name()).lower()

        if any(w in text for w in TREE_WORDS):
            groups["tree"].append(mesh)
        if any(w in text for w in SHRUB_WORDS):
            groups["shrub"].append(mesh)
        if any(w in text for w in FLOWER_WORDS):
            groups["flower"].append(mesh)
        if any(w in text for w in POT_WORDS):
            groups["pot"].append(mesh)
        if any(w in text for w in ROCK_WORDS):
            groups["rock"].append(mesh)

    # Fallback razonables
    if not groups["flower"]:
        for mesh in meshes:
            text = (mesh.get_name() + " " + mesh.get_path_name()).lower()
            if any(w in text for w in ("flower", "plant", "garden", "foliage")):
                if mesh not in groups["flower"]:
                    groups["flower"].append(mesh)

    if not groups["shrub"]:
        for mesh in meshes:
            text = (mesh.get_name() + " " + mesh.get_path_name()).lower()
            if any(w in text for w in ("shrub", "plant", "bush", "hedge", "foliage")):
                if mesh not in groups["shrub"]:
                    groups["shrub"].append(mesh)

    return groups

def classify_materials(material_assets):
    mats = {"soil": [], "stone": []}

    for ad in material_assets:
        text = (asset_name(ad) + " " + asset_path(ad)).lower()
        if any(w in text for w in SOIL_MATERIAL_WORDS):
            mats["soil"].append(ad)
        if any(w in text for w in STONE_MATERIAL_WORDS):
            mats["stone"].append(ad)

    return mats

def pick(arr):
    return random.choice(arr) if arr else None

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def distance2d(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)

def jitter(v, amount):
    return v + random.uniform(-amount, amount)

# ============================================================
# GEOMETRIA / REFERENCIA DE PLAZA
# ============================================================

def plaza_center_and_halfsize():
    plaza = find_actor_exact(PLAZA_LABEL)
    center = FALLBACK_CENTER
    half_size = DEFAULT_HALF_SIZE

    if plaza:
        try:
            origin, extent = plaza.get_actor_bounds(False)
            if extent.x > 100.0 and extent.y > 100.0:
                center = origin
                half_size = clamp(min(abs(extent.x), abs(extent.y)), MIN_HALF_SIZE, MAX_HALF_SIZE)
                log("Bounds de plaza detectados. Centro={} HalfSize={:.1f}".format(center, half_size))
            else:
                warn("Bounds de plaza no útiles; usando respaldo.")
        except Exception as exc:
            warn("No se pudieron leer bounds de plaza: {}".format(exc))
    else:
        warn("No se encontró actor JW_ENV_Plaza; usando centro de respaldo.")

    return center, half_size

CENTER, HALF = plaza_center_and_halfsize()
YAW_RAD = math.radians(PLAZA_YAW_DEG)
COS_Y = math.cos(YAW_RAD)
SIN_Y = math.sin(YAW_RAD)

def local_to_world(x, y, z=0.0):
    wx = CENTER.x + x * COS_Y - y * SIN_Y
    wy = CENTER.y + x * SIN_Y + y * COS_Y
    wz = CENTER.z + z
    return unreal.Vector(wx, wy, wz)

def world_to_local(v):
    dx = v.x - CENTER.x
    dy = v.y - CENTER.y
    lx = dx * COS_Y + dy * SIN_Y
    ly = -dx * SIN_Y + dy * COS_Y
    return lx, ly

def is_on_main_axis(local_x, local_y):
    return abs(local_x) < MAIN_AXIS_HALF_WIDTH or abs(local_y) < MAIN_AXIS_HALF_WIDTH

# ============================================================
# PROTECCIONES
# ============================================================

def get_preserved_locations():
    locs = []
    for a in all_actors():
        label = actor_label(a).lower()
        if any(w in label for w in PRESERVE_LABEL_WORDS):
            try:
                locs.append(a.get_actor_location())
            except Exception:
                pass
    return locs

PRESERVED_LOCS = get_preserved_locations()
SPAWNED_LOCS = []

def can_spawn(world_pos, local_x, local_y, spacing, allow_main_axis=False):
    # Fuente/anillo central despejado
    if math.sqrt(local_x * local_x + local_y * local_y) < CENTER_CLEAR_RADIUS:
        return False

    # Ejes principales despejados salvo plantas muy bordeadas
    if (not allow_main_axis) and is_on_main_axis(local_x, local_y):
        return False

    # No invadir faroles/bancas/asientos
    for p in PRESERVED_LOCS:
        if distance2d(world_pos, p) < PRESERVED_ACTOR_CLEARANCE:
            return False

    # Separación entre nuevos
    for p in SPAWNED_LOCS:
        if distance2d(world_pos, p) < spacing:
            return False

    return True

# ============================================================
# RECOLECCION DE MESHES / MATERIALES
# ============================================================

def collect_scene_meshes():
    meshes = []
    seen = set()

    preferred = [TREES_LABEL, SHRUBS_LABEL, ROCKS_LABEL, GRASS_LABEL, PLAZA_LABEL, PATH_LABEL]
    ordered_actors = []

    all_scene = all_actors()

    for wanted in preferred:
        for a in all_scene:
            if actor_label(a) == wanted and a not in ordered_actors:
                ordered_actors.append(a)

    for a in all_scene:
        if a not in ordered_actors:
            ordered_actors.append(a)

    for a in ordered_actors:
        for mesh in get_static_meshes_from_actor(a):
            try:
                path = mesh.get_path_name()
            except Exception:
                path = str(mesh)
            if path not in seen:
                seen.add(path)
                meshes.append(mesh)

    return meshes

SCENE_MESHES = collect_scene_meshes()
MESH_GROUPS = classify_meshes(SCENE_MESHES)

MATERIAL_ASSETS = list_project_material_assets()
MATERIAL_GROUPS = classify_materials(MATERIAL_ASSETS)

# ============================================================
# MATERIALES
# ============================================================

def choose_material(group_name):
    ad = pick(MATERIAL_GROUPS.get(group_name, []))
    return load_asset_from_data(ad) if ad else None

def looks_like_bed_component(component):
    try:
        owner_name = actor_label(component.get_owner()).lower()
    except Exception:
        owner_name = ""
    try:
        comp_name = component.get_name().lower()
    except Exception:
        comp_name = ""
    txt = owner_name + " " + comp_name

    keywords = (
        "bed", "garden", "jardin", "planter", "soil", "ground",
        "plaza", "base", "fill"
    )
    return any(k in txt for k in keywords)

def looks_like_path_component(component):
    try:
        owner_name = actor_label(component.get_owner()).lower()
    except Exception:
        owner_name = ""
    try:
        comp_name = component.get_name().lower()
    except Exception:
        comp_name = ""
    txt = owner_name + " " + comp_name
    keywords = ("path", "road", "cobble", "stone", "walk", "paver")
    return any(k in txt for k in keywords)

def apply_material_if_possible(component, material):
    if not component or not material:
        return False
    try:
        num = component.get_num_materials()
    except Exception:
        num = 0

    changed = False
    for i in range(num):
        try:
            component.set_material(i, material)
            changed = True
        except Exception:
            pass
    return changed

def improve_plaza_materials():
    """
    Intenta aplicar materiales de suelo/jardín y piedra a componentes relevantes.
    Es conservador: solo aplica sobre actores/componentes de plaza/camino.
    """
    changed = 0
    soil_mat = choose_material("soil")
    stone_mat = choose_material("stone")

    plaza = find_actor_exact(PLAZA_LABEL)
    path_actor = find_actor_exact(PATH_LABEL)

    if plaza:
        for c in get_all_mesh_components(plaza):
            try:
                name_l = c.get_name().lower()
            except Exception:
                name_l = ""
            mesh_name = ""
            try:
                mesh = c.get_editor_property("static_mesh")
                if mesh:
                    mesh_name = mesh.get_name().lower()
            except Exception:
                pass
            text = name_l + " " + mesh_name

            # Jardineras/planters -> suelo
            if soil_mat and any(k in text for k in ("bed", "garden", "soil", "ground", "planter", "fill")):
                if apply_material_if_possible(c, soil_mat):
                    changed += 1
            # Piedra/camino -> stone
            elif stone_mat and any(k in text for k in ("path", "walk", "stone", "cobble", "tile", "paver", "plaza")):
                if apply_material_if_possible(c, stone_mat):
                    changed += 1

    if path_actor and stone_mat:
        for c in get_all_mesh_components(path_actor):
            if apply_material_if_possible(c, stone_mat):
                changed += 1

    return changed

# ============================================================
# SPAWN
# ============================================================

def spawn_static_mesh_actor(mesh, world_pos, rot_yaw, scale_vec, label):
    if not mesh:
        return None

    actor = actor_subsystem.spawn_actor_from_class(
        unreal.StaticMeshActor,
        world_pos,
        unreal.Rotator(0.0, rot_yaw, 0.0)
    )
    if not actor:
        return None

    actor.set_actor_label(label)
    try:
        actor.set_folder_path(ROOT_FOLDER)
    except Exception:
        pass

    # Asignar mesh
    try:
        comp = actor.static_mesh_component
        comp.set_static_mesh(mesh)
        comp.set_mobility(unreal.ComponentMobility.STATIC)
        # sombras/collision se quedan por defecto para no romper lógica existente
    except Exception:
        try:
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp:
                comp.set_static_mesh(mesh)
        except Exception as exc:
            warn("No se pudo asignar mesh a {}: {}".format(label, exc))
            actor_subsystem.destroy_actor(actor)
            return None

    try:
        actor.set_actor_scale3d(scale_vec)
    except Exception:
        pass

    SPAWNED_LOCS.append(world_pos)
    return actor

def spawn_kind(mesh_group, local_points, target, kind, spacing, scale_fn, z_offset=BASE_Z_OFFSET, allow_main_axis=False):
    if not mesh_group:
        warn("No hay meshes para '{}'".format(kind))
        return 0

    created = 0
    idx = 1

    for lx, ly in local_points:
        if created >= target:
            break

        world_pos = local_to_world(lx, ly, z_offset)

        if not can_spawn(world_pos, lx, ly, spacing, allow_main_axis=allow_main_axis):
            continue

        mesh = pick(mesh_group)
        if not mesh:
            continue

        yaw = random.uniform(-180.0, 180.0)
        sx, sy, sz = scale_fn()
        actor = spawn_static_mesh_actor(
            mesh=mesh,
            world_pos=world_pos,
            rot_yaw=yaw,
            scale_vec=unreal.Vector(sx, sy, sz),
            label="JW_PDV2_{0}_{1:02d}".format(kind.upper(), idx)
        )
        if actor:
            created += 1
            idx += 1

    return created

# ============================================================
# PATRONES DE UBICACION
# ============================================================

def tree_points():
    r = HALF + 540.0
    pts = [
        (-r, -0.78*r), (-r, -0.45*r), (-r, 0.45*r), (-r, 0.78*r),
        ( r, -0.78*r), ( r, -0.45*r), ( r, 0.45*r), ( r, 0.78*r),
        (-0.78*r, -r), (-0.45*r, -r), (0.45*r, -r), (0.78*r, -r),
        (-0.78*r,  r), (-0.45*r,  r), (0.45*r,  r), (0.78*r,  r),
    ]
    random.shuffle(pts)
    out = []
    for x, y in pts:
        out.append((jitter(x, 100.0), jitter(y, 100.0)))
    return out

def garden_quadrant_flower_points():
    """
    Distribución dentro de las 4 jardineras.
    Mantiene despejados los ejes y no invade el centro.
    """
    pts = []

    cx = HALF * 0.52
    cy = HALF * 0.52
    spread_x = HALF * 0.28
    spread_y = HALF * 0.28

    centers = [
        (-cx, -cy),
        (-cx,  cy),
        ( cx, -cy),
        ( cx,  cy),
    ]

    for qx, qy in centers:
        for ix in (-0.7, -0.35, 0.0, 0.35, 0.7):
            for iy in (-0.7, -0.35, 0.0, 0.35, 0.7):
                px = qx + ix * spread_x + random.uniform(-35.0, 35.0)
                py = qy + iy * spread_y + random.uniform(-35.0, 35.0)
                pts.append((px, py))

    random.shuffle(pts)
    return pts

def shrub_accent_points():
    pts = []

    # Acentos en esquinas interiores cercanas a los 4 jardines.
    inner = HALF * 0.56
    off = HALF * 0.18
    pts.extend([
        (-inner, -inner), (-inner, inner), (inner, -inner), (inner, inner),
        (-inner-off, -inner), (-inner-off, inner), (inner+off, -inner), (inner+off, inner),
        (-inner, -inner-off), (inner, -inner-off), (-inner, inner+off), (inner, inner+off),
    ])

    # Bordes exteriores de la plataforma
    edge = HALF * 0.94
    values = (-0.66, -0.33, 0.33, 0.66)
    for t in values:
        pts.extend([
            (-edge, t * HALF),
            ( edge, t * HALF),
            (t * HALF, -edge),
            (t * HALF,  edge),
        ])

    random.shuffle(pts)
    out = []
    for x, y in pts:
        out.append((jitter(x, 40.0), jitter(y, 40.0)))
    return out

def pot_points():
    p = HALF * 0.93
    q = HALF * 0.62
    pts = [
        (-p, -p), (-p, p), (p, -p), (p, p),
        (-q, -HALF*0.96), (q, -HALF*0.96),
        (-q, HALF*0.96), (q, HALF*0.96),
        (-HALF*0.96, -q), (-HALF*0.96, q),
        (HALF*0.96, -q), (HALF*0.96, q),
    ]
    random.shuffle(pts)
    out = []
    for x, y in pts:
        out.append((jitter(x, 18.0), jitter(y, 18.0)))
    return out

def rock_points():
    r1 = HALF + 620.0
    r2 = HALF + 900.0
    pts = [
        (-r1, -0.88*HALF), (-r2, -0.25*HALF), (-r1, 0.72*HALF),
        ( r1, -0.77*HALF), ( r2, 0.16*HALF), ( r1, 0.82*HALF),
        (-0.82*HALF, -r1), (-0.18*HALF, -r2), (0.72*HALF, -r1),
        (-0.74*HALF,  r1), (0.18*HALF,  r2), (0.85*HALF,  r1),
    ]
    random.shuffle(pts)
    out = []
    for x, y in pts:
        out.append((jitter(x, 85.0), jitter(y, 85.0)))
    return out

def border_plant_points():
    """
    Plantas bajas bordeando caminos, sin colocarlas sobre el eje central.
    """
    pts = []
    edge = HALF + 130.0
    vals = (-0.82, -0.58, -0.22, 0.22, 0.58, 0.82)
    for t in vals:
        pts.extend([
            (-edge, t*HALF),
            ( edge, t*HALF),
            (t*HALF, -edge),
            (t*HALF,  edge),
        ])
    random.shuffle(pts)
    out = []
    for x, y in pts:
        out.append((jitter(x, 35.0), jitter(y, 35.0)))
    return out

# ============================================================
# ESCALAS
# ============================================================

def scale_tree():
    s = random.uniform(0.90, 1.10)
    return s, s, s

def scale_shrub():
    s = random.uniform(0.72, 1.00)
    return s * random.uniform(0.92, 1.08), s * random.uniform(0.92, 1.08), s

def scale_flower():
    s = random.uniform(0.65, 0.95)
    return s * random.uniform(0.95, 1.05), s * random.uniform(0.95, 1.05), s

def scale_rock():
    s = random.uniform(0.78, 1.10)
    return s * random.uniform(0.85, 1.15), s * random.uniform(0.85, 1.15), s * random.uniform(0.75, 1.0)

def scale_pot():
    s = random.uniform(0.85, 1.05)
    return s, s, s

# ============================================================
# MAIN
# ============================================================

def run():
    world = get_world()
    world_name = world.get_name() if world else "UnknownWorld"

    log("====================================================")
    log("INICIO - PLAZA DETAIL PASS V2")
    log("Nivel actual: {}".format(world_name))
    if world_name != LEVEL_EXPECTED_NAME:
        warn("El nivel abierto no coincide exactamente con {}. Continúo de todas formas.".format(LEVEL_EXPECTED_NAME))

    log("Centro usado: {}".format(CENTER))
    log("Half size usado: {:.1f}".format(HALF))
    log("Actores preservados detectados: {}".format(len(PRESERVED_LOCS)))

    log("Meshes detectados en escena: {}".format(len(SCENE_MESHES)))
    log("  Trees  = {}".format(len(MESH_GROUPS["tree"])))
    log("  Shrubs = {}".format(len(MESH_GROUPS["shrub"])))
    log("  Flowers= {}".format(len(MESH_GROUPS["flower"])))
    log("  Pots   = {}".format(len(MESH_GROUPS["pot"])))
    log("  Rocks  = {}".format(len(MESH_GROUPS["rock"])))

    log("Materiales detectados:")
    log("  Soil   = {}".format(len(MATERIAL_GROUPS["soil"])))
    log("  Stone  = {}".format(len(MATERIAL_GROUPS["stone"])))

    material_changes = improve_plaza_materials()

    created = {}
    created["trees"] = spawn_kind(
        MESH_GROUPS["tree"], tree_points(), TREE_TARGET,
        kind="tree", spacing=TREE_SPACING, scale_fn=scale_tree,
        z_offset=0.0, allow_main_axis=False
    )

    created["shrubs"] = spawn_kind(
        MESH_GROUPS["shrub"], shrub_accent_points(), SHRUB_TARGET,
        kind="shrub", spacing=SHRUB_SPACING, scale_fn=scale_shrub,
        z_offset=0.0, allow_main_axis=False
    )

    created["flowers"] = spawn_kind(
        MESH_GROUPS["flower"], garden_quadrant_flower_points(), FLOWER_TARGET,
        kind="flower", spacing=FLOWER_SPACING, scale_fn=scale_flower,
        z_offset=0.0, allow_main_axis=False
    )

    # Plantas bajas para bordes de caminos
    border_source = MESH_GROUPS["flower"] if MESH_GROUPS["flower"] else MESH_GROUPS["shrub"]
    created["border_plants"] = spawn_kind(
        border_source, border_plant_points(), BORDER_PLANT_TARGET,
        kind="borderplant", spacing=FLOWER_SPACING, scale_fn=scale_flower,
        z_offset=0.0, allow_main_axis=False
    )

    created["pots"] = spawn_kind(
        MESH_GROUPS["pot"], pot_points(), POT_TARGET,
        kind="pot", spacing=POT_SPACING, scale_fn=scale_pot,
        z_offset=0.0, allow_main_axis=False
    )

    created["rocks"] = spawn_kind(
        MESH_GROUPS["rock"], rock_points(), ROCK_TARGET,
        kind="rock", spacing=ROCK_SPACING, scale_fn=scale_rock,
        z_offset=0.0, allow_main_axis=False
    )

    log("----------------------------------------------------")
    log("RESULTADO")
    log("Material slots modificados (si hubo coincidencias) = {}".format(material_changes))
    total_new = 0
    for k, v in created.items():
        log("  {} = {}".format(k, v))
        total_new += v
    log("Total nuevos actores = {}".format(total_new))
    log("Carpeta destino = {}".format(ROOT_FOLDER))
    log("Bancas/postes/faroles NO fueron transformados.")
    log("Centro y ejes de circulación preservados.")
    log("El nivel NO fue guardado automáticamente.")
    log("FIN - PLAZA DETAIL PASS V2")
    log("====================================================")

run()
