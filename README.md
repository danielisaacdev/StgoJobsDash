# StgoJobsDash V3 (Astro + FastAPI)

Dashboard inteligente de búsqueda de empleos optimizado para el mercado chileno (Chiletrabajos.cl).

## ✨ Características
- **Scraper Inteligente:** Extracción automatizada con rotación de User-Agents.
- **Smart Matching (NLP):** Cálculo de compatibilidad entre tu CV (texto) y las ofertas usando TF-IDF.
- **Dashboard Premium:** Interfaz Dark Mode construida con Astro (Vercel-Ready).
- **Control de Postulaciones:** Marca y filtra las empresas donde ya has aplicado.

## 🚀 Instalación Local

### 1. Backend (Python/FastAPI)
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### 2. Frontend (Astro)
```bash
cd frontend
npm install
npm run dev
```

## 🧠 Arquitectura
- **Frontend:** Astro (SSR para Vercel Serverless).
- **Backend:** FastAPI + SQLite.
- **IA:** Scikit-Learn (Vectorización de texto).

---
*Desarrollado con Antigravity AI*
