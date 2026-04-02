from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string

class CVMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='spanish')

    def _clean_text(self, text):
        """
        Pre-procesamiento: minúsculas, strips, eliminación de puntuación.
        """
        if not text:
            return ""
        text = str(text).lower().strip()
        # Eliminar puntuación
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Eliminar números y caracteres especiales
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text

    def calculate_matching(self, cv_text, job_descriptions):
        """
        Calcula el score entre un CV y múltiples descripciones de empleos.
        Retorna una lista de scores de 0 a 100.
        """
        if not cv_text or not job_descriptions:
            return [0] * len(job_descriptions)

        clean_cv = self._clean_text(cv_text)
        clean_jobs = [self._clean_text(job) for job in job_descriptions]
        
        all_texts = [clean_cv] + clean_jobs
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            # El primer vector es el CV, el resto son los trabajos
            cv_vector = tfidf_matrix[0:1]
            jobs_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(cv_vector, jobs_vectors)[0]
            # Convertir a porcentaje de 0 a 100
            return [int(score * 100) for score in similarities]
        except Exception as e:
            print(f"Error vectorizing: {e}")
            return [0] * len(job_descriptions)

if __name__ == "__main__":
    matcher = CVMatcher()
    cv = "Desarrollador Python senior con experiencia en FastAPI y SQLite"
    jobs = ["Se busca experto en Python parabackend con FastAPI", "Vendedor de seguros con buena presencia"]
    scores = matcher.calculate_matching(cv, jobs)
    print(f"Scores: {scores}")
