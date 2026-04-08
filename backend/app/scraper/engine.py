import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta
import re
import urllib.parse
from functools import lru_cache

class ChileScraper:
    # URL abierta sin restringir categoría ni región, para encontrar opciones en todo ChileTrabajos.
    BASE_URL = "https://www.chiletrabajos.cl/encuentra-un-empleo?2={query}&f=2&pagina={page}"
    
    def __init__(self):
        # Usamos un User-Agent estático para evitar la dependencia fake_useragent (Regla: Reducción de ruido)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "es-CL,es;q=0.8,en-US;q=0.5,en;q=0.3",
            "Referer": "https://www.chiletrabajos.cl/"
        }

    def _get_headers(self):
        return self.headers

    def _normalize_date(self, date_str):
        now = datetime.now()
        date_str = str(date_str).lower().strip()
        
        months = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
            'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
        }
        
        match_full = re.search(r'(\d+)\s+de\s+(\w+)\s+de\s+(\d+)', date_str)
        if match_full:
            day = int(match_full.group(1))
            month = months.get(match_full.group(2), now.month)
            year = int(match_full.group(3))
            return datetime(year, month, day)

        match_rel = re.search(r'(\d+)', date_str)
        if match_rel:
            number = int(match_rel.group(1))
            if "hora" in date_str: return now - timedelta(hours=number)
            if "día" in date_str or "dia" in date_str: return now - timedelta(days=number)
        
        return now

    @lru_cache(maxsize=32)
    def scrape(self, query, max_pages=1):
        """
        Extrae empleos de Chiletrabajos. 
        Implementa lru_cache (memoization) para contestar al instante si se repite la misma búsqueda.
        """
        jobs = []
        for page in range(1, max_pages + 1):
            if query.startswith('http'):
                url_parts = urllib.parse.urlparse(query)
                qs = urllib.parse.parse_qs(url_parts.query)
                qs['pagina'] = [str(page)]
                new_query = urllib.parse.urlencode(qs, doseq=True)
                target_url = urllib.parse.urlunparse((url_parts.scheme, url_parts.netloc, url_parts.path, url_parts.params, new_query, url_parts.fragment))
            else:
                encoded_query = urllib.parse.quote_plus(query)
                target_url = self.BASE_URL.format(query=encoded_query, page=page)
            print(f"Buscando en: {target_url}")
            
            try:
                response = requests.get(target_url, headers=self._get_headers(), timeout=15)
                if response.status_code != 200: break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                # Chiletrabajos usa divs con clases como 'job-item' o simplemente bloques seguidos
                # Buscamos los bloques de títulos h2 que tienen links a /trabajo/
                job_links = soup.find_all('a', href=re.compile(r'/trabajo/'))
                
                # Para evitar duplicados en la misma página (título y botón 'ver más' tienen el mismo link)
                processed_links = set()

                for link_elem in job_links:
                    link = link_elem.get('href')
                    if not link or link in processed_links: continue
                    processed_links.add(link)

                    # Subir al contenedor padre para extraer data
                    # Generalmente es un div.job-item o un div genérico
                    container = link_elem.find_parent('div', class_='job-item') or link_elem.find_parent('div')
                    if not container: continue

                    title = link_elem.text.strip()
                    if not title or len(title) < 3: continue # Ignorar links 'Ver más' o vacíos
                    
                    if not link.startswith('http'):
                        link = "https://www.chiletrabajos.cl" + link
                    
                    # Empresa: usualmente el primer h3 o un span
                    meta_info = container.find_all('h3')
                    company = "Empresa Privada"
                    date_str = "Reciente"
                    
                    if len(meta_info) >= 1:
                        company = meta_info[0].text.split(',')[0].strip()
                    if len(meta_info) >= 2:
                        date_str = meta_info[1].text.strip()

                    # DESCRIPCIÓN CORTA (Clave para el matching score)
                    # Suele estar en un <p> o un texto suelto dentro del container
                    desc_elem = container.find('p') or container.select_one('.job-description')
                    description = desc_elem.text.replace('Ver más', '').strip() if desc_elem else ""

                    # Modalidad
                    modalidad = "Presencial"
                    if "remoto" in container.text.lower() or "teletrabajo" in container.text.lower():
                        modalidad = "Remoto"
                    elif "hibrido" in container.text.lower() or "híbrido" in container.text.lower():
                        modalidad = "Híbrido"

                    salary_match = re.search(r'\$\s?[\d\.]+', container.text)
                    salary = salary_match.group(0) if salary_match else "No especificado"

                    jobs.append({
                        "id": re.search(r'-(\d+)$', link).group(1) if re.search(r'-(\d+)$', link) else link.split('/')[-1],
                        "titulo": title,
                        "descripcion": description, # Nueva columna para mejorar IA
                        "empresa": company,
                        "link": link,
                        "fecha_publicacion": self._normalize_date(date_str).isoformat(),
                        "modalidad": modalidad,
                        "sueldo_estimado": salary,
                        "fecha_extraccion": datetime.now().isoformat(),
                        "aplicado": False
                    })

                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"Falla en scraper: {e}")
                break
                
        return jobs

if __name__ == "__main__":
    scraper = ChileScraper()
    res = scraper.scrape("informatica", max_pages=1)
    for r in res[:2]: print(f"{r['titulo']} | Desc: {r['descripcion'][:50]}...")
