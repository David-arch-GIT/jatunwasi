# PLAN AL 100% — Jatun Wasi Ñawpa Kay
*(Hoja de ruta para cerrar el proyecto y la defensa)*

## 🎯 La historia que cuenta el proyecto (lo que el docente debe ver)
Un **museo virtual inmersivo** de un pueblo colonial del valle de Cochabamba, con:
1. Un **recorrido guiado y ordenado** (no te pierdes).
2. Una **guía con IA (Adela Zamudio)** que te recibe, te narra y te responde.
3. **Contenido informativo interactivo** en cada pieza (cartelas con texto + audio).
4. **Leyendas y ambiente** (apariciones, sonido, noche).
5. Que **corre en Meta Quest** (standalone).

---

## ✅ YA HECHO (lo más pesado ya está)
- **Mundo completo**: Plaza, Templo, Convento, Hacienda + caminos + bosque + horizonte + iluminación nocturna.
- **Optimización Quest**: corre en el visor (draw calls, LODs, culling, texturas 2K).
- **Recorrido ORDENADO**: barreras invisibles + `BP_GestorRecorrido` (Templo → Convento → Hacienda) — *hecho hoy*.
- **Final**: Adela se despide + créditos en el patio de la Hacienda — *hecho hoy*.
- **19 cartelas interactivas**: apuntar con el control → la cartela salta a tu cara + suena su audio — *hecho hoy (falta probar en visor)*.
- **Guía Adela**: modelo animado, natural, listo para Quest.
- **Minimapa** en la esquina de la cámara.
- **Leyendas/apariciones**, **ambiente sonoro** por zona, **splash de arranque**, **cartel de controles**, **anti-cuelgues**.

---

## 🔲 FALTA (para el 100%) — en orden

### FASE 1 — Guardar + probar lo de hoy (1 solo paquete)
- **Ctrl+S (Save All)**.
- Empaquetar UNA vez → probar en Quest: ¿barreras bloquean? ¿cartelas saltan + suenan? ¿recorrido en orden? ¿final con créditos?
- Ajustes si hace falta (cono de apuntado / texto de cartela). *Trivial.*

### FASE 2 — Narración al entrar a cada zona (Adela te cuenta al llegar)
- Las voces ya están grabadas. Falta **1 cable** en `BP_NarrationPoint` (más fácil que las cartelas).
- *Claude deja todo listo por MCP; tú cableas 1 vez.*

### FASE 3 — Adela INTERACTIVA (la "magia" con IA — Convai)
- Instalar el plugin Convai + pegar el "cerebro" de Adela (ya está escrito en `GUIA_Adela_Convai.md`).
- Le hablas → te responde sobre el pueblo.
- *Plan B si Convai pesa mucho en Quest: Adela narra + las cartelas responden = ya cumple "interacción con IA/usuario".*

### FASE 4 — Pulido final
- Verificar en el visor: minimapa, audio, textos, que Adela se vea bien en las 3 zonas.
- Captura/video para la defensa.

---

## 🧩 Quién hace qué
- **Claude (por MCP, sin que cables):** colocar/ajustar actores, materiales, audios, posiciones, auditorías, dejar todo listo.
- **Tú (cableado en el editor, guiado paso a paso):** lo que toca grafos de Blueprint (MCP no puede): narración (1 cable), Convai.
- **Juntos:** verificar antes de cada paquete (como hoy — así no empaquetas en vano).

---

## 💪 Mensaje
El docente dijo ~20%, pero con el mundo completo + optimizado + recorrido + cartelas + guía + leyendas, estás **muy por encima de eso**. Lo que queda es **integrar y probar**, no inventar de cero. Vamos fase por fase.
