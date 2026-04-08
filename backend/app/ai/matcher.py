from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string

class CVMatcher:
    def __init__(self):
        # Por qué: Sklearn no soporta 'spanish' de forma nativa como argumento directo en el vectorizador.
        # Definir una lista ajustada a mano evita instalar dependencias grandes como NLTK o Spacy, 
        # manteniendo el código lo más liviano y eficiente posible.
        spanish_stop_words = [
            'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 'con', 
            'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 'este', 'sí', 
            'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 'me', 'hasta', 'hay', 
            'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 'uno', 'les', 'ni', 'contra', 
            'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 'mí', 'antes', 'algunos', 'qué', 'unos', 
            'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 'esa', 'estos', 'mucho', 'quienes', 'nada', 
            'muchos', 'cual', 'poco', 'ella', 'estar', 'estas', 'algunas', 'algo', 'nosotros', 'mi', 
            'mis', 'tú', 'te', 'ti', 'tu', 'tus'
        ]
        
        # Por qué: TF-IDF (Term Frequency - Inverse Document Frequency) es el algoritmo más directo
        # y rápido para comparar textos sin requerir modelos LLM complejos. Pondera más las palabras raras
        # (como tecnologías específicas) y evita que palabras muy comunes inflen el puntaje.
        # ngram_range=(1, 2) ayuda ENORMEMENTE con términos técnicos agrupados como "power bi", "machine learning", etc.
        self.vectorizer = TfidfVectorizer(stop_words=spanish_stop_words, ngram_range=(1, 2))

    def _clean_text(self, text):
        """
        Por qué: Los textos de empleos y CVs suelen venir con ruido, emojis, o formatos raros.
        Reducir todo a minúsculas y letras básicas permite que el algoritmo de matching no sea 
        estricto con la capitalización de tecnologías (ej. "Python" == "python").
        """
        if not text:
            return ""
        text = str(text).lower().strip()
        # Eliminar puntuación
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Conservar solo letras simples y espacios para evitar caracteres residuales
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text

    def calculate_matching(self, cv_text, job_texts):
        """
        Por qué: Queremos saber numéricamente (de 0 a 100) qué tan bien encaja un CV a cada oferta.
        Se usa la similitud del coseno (cosine similarity) sobre la matriz TF-IDF porque 
        compara la "dirección" de los vectores textuales ignorando su longitud (es decir,
        no penaliza un CV largo si encaja bien temáticamente).
        """
        if not cv_text or not job_texts:
            return [0] * len(job_texts)

        # Limpiamos todos los textos
        clean_cv = self._clean_text(cv_text)
        clean_jobs = [self._clean_text(j) for j in job_texts]

        # Concatenamos CV + Empleos para armar la matriz matemática (Vector Space Model)
        all_texts = [clean_cv] + clean_jobs
        
        try:
            # Generamos la matriz TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # El índice 0 es nuestro CV, del índice 1 en adelante son los empleos
            cv_tfidf = tfidf_matrix[0:1]
            jobs_tfidf = tfidf_matrix[1:]
            
            # Calculamos la Similitud del Coseno (Cosine Similarity)
            raw_scores = cosine_similarity(cv_tfidf, jobs_tfidf)[0]
            
            # Por qué: Corrección para la psicología humana y el sesgo de longitud
            # Matemáticamente, un CV extenso comparado con una descripción corta de empleo
            # rara vez pasa de 0.25 (25%) en Cosine Similarity, aunque sea el calce perfecto.
            # Aplicar raíz cuadrada ayuda a normalizar esta escala. Una similitud pura de 0.25
            # se renderiza como 50% de afinidad de negocio.
            scaled_scores = []
            for score in raw_scores:
                # Score base usando raíz cuadrada
                human_score = (score ** 0.5) * 100
                
                # Boost adicional optativo para perfiles altamente técnicos
                if score > 0.1:
                    human_score += (score * 50)  # Bonificación de afinidad estrecha
                    
                final_percent = min(round(human_score, 1), 100)
                scaled_scores.append(int(final_percent))

            return scaled_scores
        except Exception as e:
            print(f"Error vectorizing: {e}")
            return [0] * len(job_texts)

if __name__ == "__main__":
    matcher = CVMatcher()
    cv = "Desarrollador Python senior con experiencia en FastAPI y SQLite"
    jobs = ["Se busca experto en Python para backend con FastAPI", "Vendedor de seguros con buena presencia"]
    scores = matcher.calculate_matching(cv, jobs)
    print(f"Scores de prueba: {scores}")
