import sqlite3
import os
from datetime import datetime

class DBManager:
    def __init__(self, db_name="empleos.db"):
        self.db_path = f"/tmp/{db_name}"
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    descripcion TEXT,
                    empresa TEXT,
                    link TEXT UNIQUE,
                    fecha_publicacion DATETIME,
                    fecha_extraccion DATETIME,
                    modalidad TEXT,
                    sueldo_estimado TEXT,
                    aplicado INTEGER DEFAULT 0,
                    matching_score INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def save_jobs(self, jobs):
        """
        Inserta jobs evitando duplicados por link.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for job in jobs:
                try:
                    cursor.execute("""
                        INSERT INTO jobs (id, titulo, descripcion, empresa, link, fecha_publicacion, fecha_extraccion, modalidad, sueldo_estimado, aplicado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(link) DO UPDATE SET
                            titulo=excluded.titulo,
                            descripcion=excluded.descripcion,
                            empresa=excluded.empresa,
                            fecha_publicacion=excluded.fecha_publicacion,
                            fecha_extraccion=excluded.fecha_extraccion,
                            modalidad=excluded.modalidad,
                            sueldo_estimado=excluded.sueldo_estimado
                    """, (
                        job['id'], job['titulo'], job.get('descripcion', ''), 
                        job['empresa'], job['link'],
                        job['fecha_publicacion'], job['fecha_extraccion'],
                        job['modalidad'], job['sueldo_estimado'], 0
                    ))
                except sqlite3.Error as e:
                    print(f"Error saving job: {e}")
            conn.commit()

    def get_jobs(self, filter_applied=False, min_score=0):
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        
        if filter_applied:
            query += " AND aplicado = 0"
        
        if min_score > 0:
            query += " AND matching_score >= ?"
            params.append(min_score)
            
        query += " ORDER BY fecha_publicacion DESC"
        
        with self._get_connection() as conn:
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def update_application_status(self, job_link, status: bool):
        with self._get_connection() as conn:
            conn.execute("UPDATE jobs SET aplicado = ? WHERE link = ?", (1 if status else 0, job_link))
            conn.commit()

    def update_matching_score(self, job_id, score):
        with self._get_connection() as conn:
            conn.execute("UPDATE jobs SET matching_score = ? WHERE id = ?", (score, job_id))
            conn.commit()

if __name__ == "__main__":
    db = DBManager()
    print("Database Initialized")
