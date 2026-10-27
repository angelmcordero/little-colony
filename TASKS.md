# Little Colony — SDD Task Tracker & Specification Plan

> **Core Design Statement:** *"Do not control the world. Understand it."*  
> **Master Specification:** [`Little_Colony_Game_Design_Document.docx`](./Little_Colony_Game_Design_Document.docx)

---

## Metodología de Trabajo (SDD Ligero por Fases)

Para cada fase del proyecto seguiremos estrictamente este flujo de 5 pasos:

1. **Especificación (Mini-Spec):** Revisar los requisitos y criterios de aceptación de la fase en este documento.
2. **Rama (Branching):** Crear la rama dedicada desde `main` (`git checkout -b feat/nombre-fase`).
3. **Implementación:** Programar únicamente las tareas (`T#.#`) listadas en la fase.
4. **Verificación (Testing):** Ejecutar un script automatizado que valide todos los Criterios de Aceptación sin romper las fases previas.
5. **Cierre y Versionamiento:** Marcar las casillas como `[x]` en `TASKS.md`, hacer commit semántico (`feat(...)`) y fusionar (`git merge`) a `main`.

---

## Resumen de Progreso General

| Fase | Rama Asociada | Descripción | Harmony Meta | Estado |
| :--- | :--- | :--- | :---: | :---: |
| **Fase 0** | `main` | Mapa base $20\times20$, Jugador, Colisiones y Pathfinding BFS | 42% | `[x]` Completada |
| **Fase 1** | `main` (`6fe978d`) | MVP Hito 1: Timo (Constructor), Roca física, Puente y Debug UI | 42% $\rightarrow$ 62% | `[x]` Completada |
| **Fase 2** | `feat/nilo-and-seeds` | Nilo (Explorador), Cruce al Este y Descubrimiento de Semillas | 62% $\rightarrow$ 70% | `[ ]` Pendiente |
| **Fase 3** | `feat/mara-and-farming` | Granja, Almacén y Mara (Granjera: siembra, cosecha y acopio) | 70% $\rightarrow$ 81% | `[ ]` Pendiente |
| **Fase 4** | `feat/eda-and-distribution` | Casas y Eda (Cuidadora: recolección en almacén y reparto) | 81% $\rightarrow$ 91% | `[ ]` Pendiente |
| **Fase 5** | `feat/observation-and-ending` | Sistema de Observación, Panel de Personaje, Senderos y Final Estable | 91% (STABLE) | `[ ]` Pendiente |

---

## Desglose Detallado de Fases y Tareas

### Fase 0 y Fase 1: Base y Hito 1 — Timo y el Puente (MVP)
* **Rama:** `main` (Consolidado en commit `6fe978d`)
* **Mini-Spec (GDD Sec. 5, 6, 8, 11.1, 15, 20, 21.2, 23):**
  * Mundo $20\times20$ con río divisorio, 6 árboles como fuente de madera, puente con 3 estados (`broken`, `repairing`, `repaired`) y roca móvil en `(9, 10)`.
  * Timo opera autónomamente con FSM (`INSPECTING`, `GATHERING_WOOD`, `GOING_TO_REPAIR`, `SUSPENDED`, `REPAIRING`, `DONE`).
  * Requiere 3 maderas (`BRIDGE_REPAIR_WOOD_REQUIRED = 3`), las consume al iniciar la obra y tarda 4 segundos (`BRIDGE_REPAIR_TIME_MS = 4000`).
  * Harmony inicia en `42%`, sube `+8%` (`50%`) al despejar la roca y `+12%` (`62%`) al reparar el puente.
* **Checklist de Tareas:**
  * `[x]` **T1.1:** Definir constantes de terreno, colores y parámetros del GDD en `settings.py`.
  * `[x]` **T1.2:** Implementar matriz del mundo, árboles, estados del puente y validación física de roca (`is_legal_rock_pos`) en `world.py`.
  * `[x]` **T1.3:** Implementar algoritmo BFS de búsqueda de caminos en `pathfinding.py`.
  * `[x]` **T1.4:** Implementar `Player` y `Agent` (Timo) con FSM, inventario, suspensión por bloqueo y tiempos de obra en `entities.py`.
  * `[x]` **T1.5:** Implementar cálculo de Harmony, empuje de roca con `E`, reset con `R`, HUD minimalista y Debug Overlay con `F3` en `main.py`.
  * `[x]` **T1.6:** Verificar los 6 criterios de aceptación mediante prueba automatizada.

---

### Fase 2: Zona Este, Semillas y Nilo (El Explorador)
* **Rama:** `feat/nilo-and-seeds`
* **Mini-Spec (GDD Sec. 4.8, 5, 8.2, 9, 11.1):**
  * **Propósito oculto de Nilo:** Explorar el territorio accesible y descubrir recursos útiles.
  * **Recurso en el Este:** Parche de semillas (`TILE_SEED_PATCH`) ubicado en la región este (p. ej. `(16, 14)`), inicialmente con estado `seeds_discovered = False`.
  * **Comportamiento de Nilo:**
    * Mientras el puente no esté reparado (`bridge_state != "repaired"`), Nilo patrulla puntos de interés en la ribera oeste y se acerca periódicamente al puente roto intentando cruzar sin éxito.
    * Cuando el puente pasa a `repaired`, Nilo cruza el puente hacia la región este y explora hasta alcanzar el parche de semillas.
    * Al llegar al parche de semillas, marca `world.seeds_discovered = True` y pasa a un estado de patrullaje/rutina entre ambas regiones.
  * **Impacto en Harmony:** Cuando `world.seeds_discovered == True`, el Harmony suma `+8%` (pasando de `62%` a `70%`).
* **Checklist de Tareas:**
  * `[ ]` **T2.1:** Añadir constantes en `settings.py` (`TILE_SEED_PATCH`, `COLOR_SEED_PATCH_HIDDEN`, `COLOR_SEED_PATCH_DISCOVERED`, `COLOR_NILO`, `SEED_PATCH_POS`).
  * `[ ]` **T2.2:** Añadir el parche de semillas y la propiedad `seeds_discovered` en `world.py`, y su renderizado visual en `main.py`.
  * `[ ]` **T2.3:** Implementar la clase `Nilo` en `entities.py` con su FSM (`PATROLLING_WEST`, `APPROACHING_BRIDGE`, `EXPLORING_EAST`, `DISCOVERED_SEEDS`).
  * `[ ]` **T2.4:** Instanciar a Nilo en `main.py`, actualizar `calculate_harmony()` (`+8%` al descubrir semillas) y mostrar el estado de Nilo y semillas en el Debug Overlay (`F3`).
  * `[ ]` **T2.5:** Ejecutar prueba automatizada de aceptación para la Fase 2.
* **Criterios de Aceptación (Tests):**
  1. Nilo permanece en el lado oeste y no puede cruzar mientras el puente esté en `broken` o `repairing`.
  2. Una vez que Timo repara el puente (`repaired`), Nilo cruza autónomamente el río hacia el este.
  3. Nilo llega a la ubicación de las semillas y cambia `world.seeds_discovered` a `True`.
  4. El indicador de Harmony sube de `62%` a `70%` únicamente tras el descubrimiento de las semillas.

---

### Fase 3: Granja, Almacén y Mara (La Granjera)
* **Rama:** `feat/mara-and-farming`
* **Mini-Spec (GDD Sec. 4.1, 4.2, 5, 9, 11.1):**
  * **Propósito oculto de Mara:** Mantener un suministro viable de alimentos.
  * **Zonas Noroeste:**
    * **Granja (`Farm`):** Parcelas de tierra (`TILE_FARM_SOIL`) con estados de cultivo (`empty`, `planted`, `mature`).
    * **Almacén (`Storage`):** Estructura cercana a la granja con punto de entrada y contador `world.storage_food = 0`.
  * **Comportamiento de Mara:**
    * Mientras `world.seeds_discovered == False`, Mara inspecciona la granja y el área de recursos sin poder iniciar la siembra normal (espera/reintenta).
    * Cuando `world.seeds_discovered == True`, Mara viaja a obtener semillas, regresa a la granja, planta las parcelas (`planted`), espera el tiempo de crecimiento hasta que maduren (`mature`), cosecha los cultivos y transporta la comida al Almacén (`world.storage_food += 1`, `world.farmer_producing_food = True`).
  * **Impacto en Harmony:** Cuando `world.farmer_producing_food == True`, el Harmony suma `+11%` (pasando de `70%` a `81%`).
* **Checklist de Tareas:**
  * `[ ]` **T3.1:** Definir constantes de Granja, estados de cultivo, Almacén y color de Mara en `settings.py`.
  * `[ ]` **T3.2:** Implementar las parcelas de granja, edificio de Almacén y variables de estado (`crop_state`, `storage_food`, `farmer_producing_food`) en `world.py` y su renderizado en `main.py`.
  * `[ ]` **T3.3:** Implementar la clase `Mara` en `entities.py` con su FSM (`WAITING_FOR_SEEDS`, `GETTING_SEEDS`, `PLANTING`, `TENDING_CROPS`, `HARVESTING`, `DELIVERING_TO_STORAGE`).
  * `[ ]` **T3.4:** Integrar a Mara en `main.py`, actualizar `calculate_harmony()` (`+11%`) y añadir su estado y stock de almacén al Debug Overlay (`F3`).
  * `[ ]` **T3.5:** Ejecutar prueba automatizada de aceptación para la Fase 3.
* **Criterios de Aceptación (Tests):**
  1. Mara no planta ni produce comida mientras `seeds_discovered` sea `False`.
  2. Tras descubrirse las semillas, Mara recolecta semillas, planta, cosecha y deposita comida en el Almacén (`storage_food > 0`).
  3. Las parcelas de la granja cambian visualmente de estado (`empty` $\rightarrow$ `planted` $\rightarrow$ `mature`).
  4. El indicador de Harmony sube de `70%` a `81%` cuando Mara produce y almacena comida.

---

### Fase 4: Casas y Eda (La Cuidadora)
* **Rama:** `feat/eda-and-distribution`
* **Mini-Spec (GDD Sec. 4.3, 5, 9, 11.1):**
  * **Propósito oculto de Eda:** Apoyar las necesidades básicas llevando los recursos disponibles a donde se necesitan.
  * **Casas (`Houses`):** 2 pequeñas casas con casillas de entrada/puerta que sirven como destinos de distribución.
  * **Comportamiento de Eda:**
    * Eda viaja periódicamente a la entrada del Almacén para revisar si hay comida (`world.storage_food > 0`).
    * Si el almacén está vacío, espera unos segundos o visita una casa con las manos vacías y vuelve a revisar más tarde (nunca produce comida por sí misma).
    * Si hay comida disponible en el Almacén, retira una unidad (`storage_food -= 1`), la lleva a las entradas de las casas y completa la distribución (`world.caretaker_distributing_food = True`).
  * **Impacto en Harmony:** Cuando `world.caretaker_distributing_food == True`, el Harmony suma `+10%` (pasando de `81%` a `91%`, el estado estable objetivo).
* **Checklist de Tareas:**
  * `[ ]` **T4.1:** Definir constantes para Casas y Eda en `settings.py`.
  * `[ ]` **T4.2:** Añadir Casas y casillas de entrega en `world.py` y su renderizado en `main.py`.
  * `[ ]` **T4.3:** Implementar la clase `Eda` en `entities.py` con su FSM (`CHECKING_STORAGE`, `WAITING_EMPTY`, `DELIVERING_TO_HOUSE`).
  * `[ ]` **T4.4:** Integrar a Eda en `main.py`, actualizar `calculate_harmony()` (`+10%` hasta `91%`) y mostrar el estado de Eda en el Debug Overlay (`F3`).
  * `[ ]` **T4.5:** Ejecutar prueba automatizada de aceptación para la Fase 4.
* **Criterios de Aceptación (Tests):**
  1. Eda no distribuye ni genera comida cuando `storage_food == 0`.
  2. Cuando Mara deposita comida en el almacén, Eda la recoge y la entrega en una casa.
  3. El indicador de Harmony alcanza el `91%` al completarse la primera entrega.

---

### Fase 5: Sistema de Observación, Senderos y Estado Final Estable
* **Rama:** `feat/observation-and-ending`
* **Mini-Spec (GDD Sec. 8.1, 10, 12.2, 12.3, 13):**
  * **Senderos (`TILE_DIRT_PATH`):** Caminos de tierra transitables que conectan visualmente la granja, el almacén, el bosque y el puente.
  * **Sistema de Observación y Descubrimiento:**
    * Registra eventos repetidos de los habitantes (umbral `OBSERVATION_THRESHOLD_BASIC = 2`).
    * Hacer clic izquierdo sobre un habitante lo selecciona y abre a la derecha el **Character Panel** mostrando únicamente las observaciones desbloqueadas, la hipótesis inferida y las relaciones descubiertas.
    * Presionar `Esc` cierra el panel de personaje.
  * **Condición de Final Estable (End Condition):**
    * Cuando `harmony == 91%` se mantiene estable durante unos segundos (p. ej. 5 segundos), se muestra en pantalla el mensaje final del GDD:
      * *"The colony no longer needs your help."*
      * *"You understood enough to let it live."*
* **Checklist de Tareas:**
  * `[ ]` **T5.1:** Agregar senderos de tierra (`TILE_DIRT_PATH`) en `world.py` y `main.py`.
  * `[ ]` **T5.2:** Crear el módulo/clase `ObservationSystem` con contadores de eventos y pistas desbloqueables para Timo, Nilo, Mara y Eda.
  * `[ ]` **T5.3:** Implementar selección de personaje con clic izquierdo y el renderizado del Panel Lateral de Personaje (`Esc` para cerrar).
  * `[ ]` **T5.4:** Implementar detector de Estado Estable (`91%` sostenido) y banner/mensaje de cierre con opción de continuar observando o reiniciar.
  * `[ ]` **T5.5:** Ejecutar suite de pruebas integral End-to-End (los 11 tests funcionales de GDD Sección 24.1).
* **Criterios de Aceptación (Tests):**
  1. Las pistas de cada personaje empiezan ocultas y se desbloquean al alcanzar el umbral de observación ($\ge 2$).
  2. Hacer clic sobre un agente abre su panel con las pistas obtenidas; `Esc` lo cierra.
  3. El mensaje final de colonia estable se activa única y exclusivamente cuando toda la cadena causal opera al `91%`.
