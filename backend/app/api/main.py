from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from ..scraper.engine import ChileScraper
from ..database.db_manager import DBManager
from ..ai.matcher import CVMatcher

app = FastAPI(title="StgoJobsDash API", version="1.0.0")
db = DBManager()
scraper = ChileScraper()
matcher = CVMatcher()

# Configuración de CORS para el frontend de Astro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar a los dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobUpdate(BaseModel):
    aplicado: bool

class CVInput(BaseModel):
    cv_text: str

@app.get("/scrape")
async def run_scrape(query: str = Query(..., description="Término de búsqueda")):
    try:
        jobs = scraper.scrape(query, max_pages=3)
        db.save_jobs(jobs)
        return {"status": "success", "jobs_found": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def get_jobs(
    include_applied: bool = Query(True, description="Incluir ofertas ya marcadas como aplicadas"),
    min_score: int = Query(0, description="Filtrar por score mínimo de matching")
):
    try:
        jobs = db.get_jobs(filter_applied=not include_applied, min_score=min_score)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/jobs/{job_id}/apply")
async def update_apply_status(job_id: str, status: JobUpdate):
    try:
        with db._get_connection() as conn:
            conn.execute("UPDATE jobs SET aplicado = ? WHERE id = ?", (1 if status.aplicado else 0, job_id))
            conn.commit()
        return {"status": "success", "job_id": job_id, "aplicado": status.aplicado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/matching")
async def calculate_match(input_data: CVInput):
    try:
        # Recuperar todos los empleos
        jobs = db.get_jobs(filter_applied=False)
        if not jobs:
            return {"status": "no jobs found", "matches": 0}
            
        # Combinar título y descripción para un matching mucho más preciso
        job_texts = [f"{job['titulo']} {job.get('descripcion', '')}" for job in jobs]
        scores = matcher.calculate_matching(input_data.cv_text, job_texts)
        
        # Actualizar scores en DB
        for i, score in enumerate(scores):
            db.update_matching_score(jobs[i]['id'], score)
            
        return {"status": "success", "matches": len(scores)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
