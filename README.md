# StgoJobsDash 🇨🇱

Un dashboard inteligente y de alto rendimiento optimizado exhaustivamente para la caza de empleo en **Chiletrabajos.cl**. Extrae masivamente ofertas tecnológicas y las compara con tu CV mediante Inteligencia Artificial clásica (NLP).

## ✨ Características Principales

- **Web Scraper Bypasser:** Elude bloqueos y scrapea de forma agresiva enlaces completos insertados por el usuario. Soporta paginación inteligente de múltiples páginas e inyección de query params en crudo.
- **AI Matchmaking Local:** Usa procesamiento de lenguaje natural `TF-IDF Vectorizer` y `Cosine Similarity` (Scikit-Learn). Extrae Bigramas (ej. "Machine Learning", "Power BI") y penaliza palabras clave genéricas para escalar afinidad técnica precisa.
- **Dashboard Premium (Astro + Vanilla DS):** Construcción modular 100% server-client decoupled, un Dark-Mode con estilo cristalino y renderizado reactivo instantáneo vía `localStorage`.
- **Filtros Matemáticos & Pipeline de Decisión:** Reglas de ordenamiento visual (`Score Ponderado` primario -> `Recencia` secundario), filtrado de empresas ya postuladas, y exportación de hallazgos como CSV en MS.

---

## 🚀 Instalación y Despliegue Local

StgoJobsDash ha sido rediseñado como un entorno totalmente local y privado. Sus dos servicios (Frontend y Backend) corren de manera agnóstica a la nube en tu propio Hardware.

### 1. Iniciar el Motor Backend (Python / FastAPI / Scikit-Learn)

El backend orquesta el *web scraping* asíncrono y los *cálculos de Machine Learning* exponiendo una API REST fulgurante.

```bash
cd backend
# Instala las librerías necesarias
pip install -r requirements.txt

# Inicia el servidor (Por defecto apuntará al puerto 8000)
python main.py
```

### 2. Iniciar el Interfaz Frontend (Astro / Vite)

Astro gestiona el layout, el DOM virtual y manda peticiones seguras al Backend en background.

```bash
cd frontend
# Instala todas las dependencias preconstruidas de Astro.js
npm install

# Levanta el host de desarrollo
npm run dev
```

Una vez levantados ambos entornos, abre tu navegador en `http://localhost:4321`.

---

## 🛠️ Cómo Utilizarlo Eficazmente

1. **Obtén tu Enlace de Búsqueda:** Ve a [Chiletrabajos.cl](https://chiletrabajos.cl), utiliza todos los filtros posibles de la interfaz oficial (ej: Santiago central, fecha reciente, categoría TI, teletrabajo). Copia la **URL cruda entera** generada en la barra de tu navegador.
2. **Scrapear Data:** Pega exactamente la URL en el panel de control del Dashboard y haz clic en **Scrapear**. El Backend automáticamente recorrerá las primeras 3 páginas de paginación extraídas de ese enlace crudo y descargará las ofertas optimizando llamadas de bloqueos.
3. **Mide la Afinidad (Matchmaking):** Copia el texto textual de tu Currículum Vitae (CV) y pégalo en el gran bloque lateral. Presiona **Actualizar Scores**.
4. **Interactúa y Exporta:** Verás como el Dashboard re-ordena dinámicamente tu vista enviando a los empleos con mejor *Afinidad Numérica* y *Recencia* de fechas de salida hacia arriba del todo. Presiona CSV para descargarlas en Excel.

---

## 🧠 Arquitectura Tecnológica Resumida

*   **Frontend:** `Astro` (SSR para rendimiento Extremo), `TypeScript`, CSS-Natual Dark System.
*   **Backend:** `Python 3.10+`, `FastAPI` (Pydantic, Uvicorn, ASGI REST).
*   **Datos y AI:** `urllib`, `requests`, `BeatifulSoup4` (Data Injection y Parsing), `scikit-learn` (Vectorización TF-IDF N-grams).

---
*Diseñado bajo una filosofía "Agnostic-Cloud Local-First" - by Daniel Isaac & Antigravity AI*
