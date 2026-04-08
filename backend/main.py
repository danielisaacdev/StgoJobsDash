from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.scraper.engine import ChileScraper
from app.ai.matcher import CVMatcher

# Por qué: Separar responsabilidades es clave. FastAPI solo actúa como enrutador ligero.
app = FastAPI(title="StgoJobsDash API", version="1.0.0")
scraper = ChileScraper()
matcher = CVMatcher()

# Por qué: Configuración de CORS estricta pero abierta para localhost o producción,
# permitiendo al frontend Astro consumir el API sin bloqueos del navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CVInput(BaseModel):
    cv_text: str
    jobs: List[dict]

@app.get("/scrape")
async def run_scrape(query: str = Query(..., description="Término de búsqueda")):
    """
    Por qué: Llama al scraper, que ya cuenta con memoization local para resolver peticiones
    repetidas instantáneamente sin quemar el servidor ni ser bloqueados.
    """
    try:
        jobs = scraper.scrape(query, max_pages=3)
        return {"status": "success", "jobs_found": len(jobs), "jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/matching")
async def calculate_match(input_data: CVInput):
    """
    Por qué: Método Stateless. En vez de guardar empleos en una Base de Datos local
    y tener que actualizar scores id por id, el frontend manda los empleos scrapeados,
    el backend actualiza los puntajes y devuelve la lista mejorada en ms.
    """
    try:
        jobs = input_data.jobs
        if not jobs or not input_data.cv_text:
            return {"status": "success", "jobs": jobs}

        # Combinar título y descripción mejora la precisión del TD-IDF.
        job_texts = [f"{job.get('titulo', '')} {job.get('descripcion', '')}" for job in jobs]
        scores = matcher.calculate_matching(input_data.cv_text, job_texts)
        
        # Actualizamos la estructura de jobs al vuelo (in memory)
        for i, score in enumerate(scores):
            jobs[i]['matching_score'] = score
            
        return {"status": "success", "jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
