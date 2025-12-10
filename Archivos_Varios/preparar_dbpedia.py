from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, DCTERMS
import os
import urllib.request
import bz2
import shutil

def descargar_dbpedia_files():
    """Descarga archivos necesarios de DBpedia Databus"""
    archivos = {
        "labels_es.ttl": "https://databus.dbpedia.org/dbpedia/collections/latest-core/labels/labels_es.ttl.bz2",
        "short_abstracts_es.ttl": "https://databus.dbpedia.org/dbpedia/collections/latest-core/abstracts/short_abstracts_es.ttl.bz2"
    }
    
    for nombre_final, url in archivos.items():
        archivo_bz2 = nombre_final + ".bz2"
        
        if os.path.exists(nombre_final):
            print(f"✅ {nombre_final} ya existe, omitiendo descarga")
            continue
        
        try:
            print(f"📥 Descargando {nombre_final}...")
            urllib.request.urlretrieve(url, archivo_bz2)
            
            print(f"   Descomprimiendo {archivo_bz2}...")
            with bz2.BZ2File(archivo_bz2) as f_in:
                with open(nombre_final, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            os.remove(archivo_bz2)
            print(f"✅ {nombre_final} listo")
            
        except Exception as e:
            print(f"❌ Error descargando {nombre_final}: {e}")

def preparar_dbpedia_local():
    """Combina archivos DBpedia en uno solo optimizado"""
    
    print("🔄 Preparando DBpedia local...")
    
    # Crear grafo combinado
    g_combined = Graph()
    
    # Namespaces
    DBO = Namespace("http://dbpedia.org/ontology/")
    DBR = Namespace("http://dbpedia.org/resource/")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    
    # Cargar archivos descargados
    archivos = [
        "labels_es.ttl",
        "short_abstracts_es.ttl",
        # Agrega aquí otros archivos que hayas descargado
    ]
    
    for archivo in archivos:
        if os.path.exists(archivo):
            print(f"  Cargando {archivo}...")
            g_combined.parse(archivo, format="turtle")
        else:
            print(f"  ⚠️ {archivo} no encontrado")
    
    # Opcional: Filtrar solo datos relevantes para noticias
    print("  Filtrando datos relevantes...")
    
    # Crear consulta para extraer solo datos útiles
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    CONSTRUCT {
        ?s rdfs:label ?label .
        ?s dbo:abstract ?abstract .
        ?s dbo:thumbnail ?thumb .
        ?s dbo:birthDate ?birth .
        ?s dbo:deathDate ?death .
        ?s foaf:name ?name .
    }
    WHERE {
        ?s rdfs:label ?label .
        FILTER(LANG(?label) = "es")
        
        OPTIONAL { ?s dbo:abstract ?abstract . 
                  FILTER(LANG(?abstract) = "es") }
        OPTIONAL { ?s dbo:thumbnail ?thumb }
        OPTIONAL { ?s dbo:birthDate ?birth }
        OPTIONAL { ?s dbo:deathDate ?death }
        OPTIONAL { ?s foaf:name ?name }
        
        # Filtrar por tipos relevantes para noticias
        FILTER(EXISTS { ?s a ?type . 
                FILTER(?type IN (dbo:Person, dbo:Place, dbo:Organisation, 
                                 dbo:Event, dbo:Work, dbo:Agent)) })
    }
    LIMIT 50000  # Limitar a 50,000 recursos (ajustable)
    """
    
    # Crear grafo filtrado
    g_filtrado = Graph()
    resultados = g_combined.query(query)
    
    # Agregar resultados al grafo filtrado
    for triple in resultados:
        g_filtrado.add(triple)
    
    # Guardar archivo optimizado
    print("  Guardando dbpedia_local.ttl...")
    g_filtrado.serialize("dbpedia_local.ttl", format="turtle")
    
    print(f"✅ DBpedia local preparada: {len(g_filtrado)} triples")
    print("📁 Archivo: dbpedia_local.ttl")

if __name__ == "__main__":
    descargar_dbpedia_files()
    preparar_dbpedia_local()