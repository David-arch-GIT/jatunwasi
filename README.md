# JatunWasi Ñawpaqay — Proyecto de Tesis (VR)

Experiencia VR de patrimonio cultural: la Tarata colonial (Cochabamba, Bolivia).
Unreal Engine **5.7** · Meta **Quest 2** (standalone).

## Versionado

El proyecto se versiona por números: **Versión 1, Versión 2, Versión 3...**
Cada versión es un *commit* con su *tag* (`v1`, `v2`, `v3`...).

Para ver el historial de versiones:
```
git log --oneline --decorate
git tag
```

Para volver a una versión anterior (sin perder nada, crea una rama):
```
git checkout -b revisar-v1 v1
```

## Qué contiene el repositorio

- `Content/JWN/` — **todo el trabajo propio**: mapas, blueprints, materiales, santos, audio.
- `Config/` — configuración del proyecto (calidad Quest, anti-cuelgue, etc.).
- `Scripts_Tesis/` — scripts Python de automatización usados en el desarrollo.
- `Plugins/` — plugin de automatización (MCPUnreal).
- `JatunWasiNawpakay.uproject` — el proyecto.

## Qué NO contiene (y por qué)

Para que el repo sea manejable, **no** se versionan:
- **Artefactos de build** (`Binaries/`, `Intermediate/`, `Saved/`, `DerivedDataCache/`) — Unreal los regenera solos.
- **APKs** y `.zip` de instaladores.
- **Packs de terceros gigantes** (`StylescapeHD` 4.3 GB, `Megascans` 3 GB, y plantillas VR).
  Están respaldados en sus `.zip` / marketplace. **Si clonas el repo en una PC nueva, hay que reimportar esos packs** para que el proyecto abra sin referencias faltantes.

> La copia de trabajo en esta PC ya tiene todo (packs incluidos); el repositorio guarda el historial de **tu** trabajo.
