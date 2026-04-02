# Roadmap de Implementación: StgoJobsDash (Chiletrabajos.cl) - V2

Este documento detalla la arquitectura de un ecosistema de búsqueda de empleos ligero y eficiente, optimizado para Chiletrabajos.cl con mejoras de robustez y analítica.

## User Review Required

> [!IMPORTANT]
> **Estrategia Anti-Bot**: El scraper incluirá pausas aleatorias (`time.sleep`) y rotación de `User-Agent`. Sin embargo, el uso intensivo puede resultar en bloqueos temporales de IP. Se recomienda no exceder el límite de 3 páginas por búsqueda.

> [!TIP]
> **NLP en Español**: Para el Matching de CV, utilizaremos `TfidfVectorizer` con la lista oficial de *stopwords* en español para asegurar que la relevancia se centre en habilidades técnicas y no en conectores del lenguaje.

## Proposed Changes

### Fase 1: El Motor de Extracción (Engine)
**Objetivo**: Recolección robusta y paginada de vacantes.

#### [MODIFY] [engine.py](file:///c:/Users/danyu/proyectos/StgoJobsDash/app/scraper/engine.py)
- **Estrategia Anti-Bot**: Implementación de `fake-useragent` o lista rotativa de headers.
- **Paginación**: Límite por defecto de 3 páginas (vía parámetro `&pagina=X`).
- **Intervalos**: Pausas de 2 a 5 segundos (aleatorios) entre peticiones.
- **Limpieza**: Normalización de fechas relativas (ej. "hace 3 días") a objetos `datetime` nativos de Python.

---

### Fase 2: Persistencia y API (Data Layer)
**Objetivo**: Almacenamiento estructurado y trazabilidad de postulaciones.

#### [MODIFY] [db_manager.py](file:///c:/Users/danyu/proyectos/StgoJobsDash/app/database/db_manager.py)
- **Esquema SQL Actualizado**:
  - `id` (PK), `titulo`, `empresa`, `link` (Unique), `fecha_extraccion`, `modalidad`, `sueldo_estimado`.
  - `aplicado` (BOOLEAN, Default 0): Para seguimiento del usuario.
- **Integridad**: Conversión forzada de datos antes de la inserción (especialmente fechas).

#### [MODIFY] [main.py](file:///c:/Users/danyu/proyectos/StgoJobsDash/app/api/main.py)
- Endpoint `PATCH /jobs/{id}`: Para actualizar el estado `aplicado`.
- Filtros en `GET /jobs`: Parámetro `include_applied` (bool).

---

### Fase 3: Inteligencia y Matching (AI Layer)
**Objetivo**: Procesamiento de lenguaje natural para ranking de relevancia.

#### [MODIFY] [matcher.py](file:///c:/Users/danyu/proyectos/StgoJobsDash/app/ai/matcher.py)
- **Pre-procesamiento**:
  - Conversión a minúsculas.
  - Eliminación de signos de puntuación y caracteres especiales.
  - Tokenización básica.
- **Modelo**: `TfidfVectorizer(stop_words='spanish')`.
- **Salida**: Score de 0 a 100 basado en similitud de coseno.

---

### Fase 4: Dashboard Interactivo (UI Layer)
**Objetivo**: Panel de control con gestión de estado de postulaciones.

#### [MODIFY] [dashboard.py](file:///c:/Users/danyu/proyectos/StgoJobsDash/ui/dashboard.py)
- **Control de Flujo**:
  - Filtro en Sidebar: "Ocultar ofertas ya postuladas".
  - Métricas: Total de vacantes nuevas vs. total aplicadas.
- **Interactividad**:
  - Botón "Marcar como Postulado" en cada tarjeta (dispara `PATCH` a la API).
  - Estética Dark Mode con acentos `Emerald/Electric Blue`.

---

### requirements.txt Actualizado
```text
fastapi
uvicorn
requests
beautifulsoup4
streamlit
scikit-learn
pandas
nltk # Para stopwords adicionales si es necesario
```

## Open Questions

- **NLTK**: ¿Deseas incluir lematización (llevar palabras a su raíz) para mejorar el matching, o mantenemos el TF-IDF puro para menor consumo de RAM?
- **Notificaciones**: ¿Te gustaría una alerta visual en el Dashboard cuando el Score de Matching supere el 80%?

## Verification Plan

### Automated Tests
- Validar esquema de DB con la nueva columna `aplicado`.
- Test de NLP: Asegurar que "Ingeniero" e "ingeniero," resulten en el mismo vector tras limpieza.

### Manual Verification
- Verificar en el navegador que el scraper navega correctamente por las 3 páginas de resultados.
- Comprobar que al marcar una oferta como "Aplicada", ésta desaparece si el filtro está activo.
