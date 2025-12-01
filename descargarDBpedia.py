from SPARQLWrapper import SPARQLWrapper, JSON
import time
import random

# Configuración
ENDPOINT = "http://dbpedia.org/sparql"
ARCHIVO_SALIDA = "dbpedia_local.ttl"

# TU LISTA DE TEMAS (Ya actualizada)
TEMAS = [
    "Bolivia", "La_Paz", "Santa_Cruz_de_la_Sierra", "Cochabamba",
    "Luis_Arce", "Evo_Morales", "Carlos_Mesa", "Jeanine_Áñez",
    "Fútbol", "Club_Bolívar", "The_Strongest", "Selección_de_fútbol_de_Bolivia",
    "Economía", "Litio", "Gas_natural", "Dólar_estadounidense",
    "Inteligencia_artificial", "ChatGPT", "Tecnología", "Cambio_climático",
    "Lionel_Messi", "Javier_Milei", "Nayib_Bukele", "Luiz_Inácio_Lula_da_Silva",
    "Carnaval_de_Oruro", "Salar_de_Uyuni"
]

def obtener_datos_dbpedia():
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setReturnFormat(JSON)
    
    # --- CORRECCIÓN CLAVE 1: DISFRAZAR EL SCRIPT ---
    # Esto le dice a DBpedia que somos un navegador web, no un script de Python
    sparql.setAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    contenido_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""
    print("🚀 Iniciando descarga INTELIGENTE de DBpedia...")

    count_total = 0
    
    for tema in TEMAS:
        print(f"   🔎 Buscando: {tema}...", end=" ")
        
        # Consulta SPARQL simplificada para evitar Timeouts
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?resource ?label ?abstract WHERE {
            # Buscamos coincidencias en el título
            ?resource rdfs:label ?label .
            FILTER (contains(lcase(?label), lcase("%s")))
            
            # Obtenemos el resumen
            ?resource dbo:abstract ?abstract .
            
            # Filtros estrictos
            FILTER(STRSTARTS(STR(?resource), "http://dbpedia.org/resource/"))
            FILTER(LANG(?label) = "es")
            FILTER(LANG(?abstract) = "es" || LANG(?abstract) = "en")
        }
        LIMIT 15
        """ % (tema)

        try:
            sparql.setQuery(query)
            results = sparql.query().convert()
            
            bindings = results["results"]["bindings"]
            
            if not bindings:
                print("⚠️ Sin datos.")
            else:
                print(f"✅ {len(bindings)} noticias encontradas.")

            for result in bindings:
                uri = result["resource"]["value"]
                # Limpieza de caracteres que rompen el archivo TTL
                nombre_recurso = uri.split("/")[-1].replace("(", "").replace(")", "").replace(",", "").replace(".", "")
                
                label = result["label"]["value"].replace('"', '\\"').strip()
                abstract = result["abstract"]["value"].replace('"', '\\"').replace('\n', ' ').strip()
                lang = result["abstract"]["xml:lang"]

                tripleta = f"""
dbr:{nombre_recurso}
    a dbo:Thing ;
    rdfs:label "{label}"@es ;
    dbo:abstract "{abstract}"@{lang} .
"""
                contenido_ttl += tripleta
                count_total += 1
            
            # --- CORRECCIÓN CLAVE 2: PAUSA ---
            # Esperamos 1 segundo entre consultas para que no nos bloqueen
            time.sleep(1.5)

        except Exception as e:
            print(f"\n❌ Error con '{tema}': {e}")
            # Si falla, esperamos 5 segundos antes de seguir
            time.sleep(5)

    # Guardar archivo
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(contenido_ttl)
    
    print(f"\n🎉 PROCESO FINALIZADO.")
    print(f"   Se guardaron {count_total} registros en '{ARCHIVO_SALIDA}'")
    print("   -> Reinicia tu aplicación Flask para ver los cambios.")

if __name__ == "__main__":
    obtener_datos_dbpedia()