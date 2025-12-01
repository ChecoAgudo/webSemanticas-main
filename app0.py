from flask import Flask, request, render_template, jsonify
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from datetime import datetime
import json
from googletrans import Translator
import urllib.parse

app = Flask(__name__)
translator = Translator()

# Configurar namespaces
ONTOLOGY_NS = Namespace("http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")
DBPEDIA_NS = Namespace("http://dbpedia.org/resource/")
DBPEDIA_ONTOLOGY_NS = Namespace("http://dbpedia.org/ontology/")

# Configurar SPARQL endpoint de DBpedia
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

# Cargar la ontología
g = Graph()
try:
    if os.path.exists("noticias_ontologia.rdf"):
        g.parse("noticias_ontologia.rdf", format="xml")
    elif os.path.exists("noticias_ontologia.owl"):
        g.parse("noticias_ontologia.owl", format="xml")
    print(f"Ontología cargada correctamente con {len(g)} tripletas")
except Exception as e:
    print(f"Error al cargar la ontología: {e}")

# Configuración de idiomas
LANGUAGES = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português'
}

# Traducciones completas
TRANSLATIONS = {
    'search_placeholder': {
        'es': 'Buscar noticias...',
        'en': 'Search news...',
        'pt': 'Pesquisar notícias...'
    },
    'search_button': {
        'es': 'Buscar',
        'en': 'Search',
        'pt': 'Pesquisar'
    },
    'title': {
        'es': 'Buscador de Noticias',
        'en': 'News Search',
        'pt': 'Pesquisa de Notícias'
    },
    'no_results': {
        'es': 'No se encontraron noticias para',
        'en': 'No news found for',
        'pt': 'Nenhuma notícia encontrada para'
    },
    'results_for': {
        'es': 'Resultados para',
        'en': 'Results for',
        'pt': 'Resultados para'
    },
    'date': {
        'es': 'Fecha',
        'en': 'Date',
        'pt': 'Data'
    },
    'topic': {
        'es': 'Tema',
        'en': 'Topic',
        'pt': 'Tema'
    },
    'author': {
        'es': 'Autor',
        'en': 'Author',
        'pt': 'Autor'
    },
    'verification': {
        'es': 'Verificación',
        'en': 'Verification',
        'pt': 'Verificação'
    },
    'not_verified': {
        'es': 'No verificada',
        'en': 'Not verified',
        'pt': 'Não verificada'
    },
    'view_details': {
        'es': 'Ver detalles',
        'en': 'View details',
        'pt': 'Ver detalhes'
    },
    'view_on_dbpedia': {
        'es': 'Ver en DBpedia',
        'en': 'View on DBpedia',
        'pt': 'Ver no DBpedia'
    },
    'local_results': {
        'es': 'Resultados Locales',
        'en': 'Local Results',
        'pt': 'Resultados Locais'
    },
    'dbpedia_results': {
        'es': 'Resultados de DBpedia',
        'en': 'DBpedia Results',
        'pt': 'Resultados do DBpedia'
    },
    'inferred_results': {
        'es': 'Resultados Inferidos',
        'en': 'Inferred Results',
        'pt': 'Resultados Inferidos'
    },
    'back': {
        'es': 'Volver',
        'en': 'Back',
        'pt': 'Voltar'
    },
    'news_details': {
        'es': 'Detalle de la Noticia',
        'en': 'News Details',
        'pt': 'Detalhes da Notícia'
    },
    'dark_mode': {
        'es': 'Modo Oscuro',
        'en': 'Dark Mode',
        'pt': 'Modo Escuro'
    },
    'light_mode': {
        'es': 'Modo Claro',
        'en': 'Light Mode',
        'pt': 'Modo Claro'
    },
    'translated_from': {
        'es': 'Traducido del',
        'en': 'Translated from',
        'pt': 'Traduzido do'
    },
    'no_dbpedida_results': {
        'es': 'No se encontraron resultados en DBpedia',
        'en': 'No results found in DBpedia',
        'pt': 'Nenhum resultado encontrado no DBpedia'
    }
}

def translate_text(text, src_lang, dest_lang):
    """Traduce texto entre idiomas usando Google Translate"""
    try:
        if src_lang == dest_lang or not text:
            return text
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def query_dbpedia(search_term, lang='es'):
    """
    Consulta DBpedia buscando específicamente dbo:abstract.
    Si no hay descripción en español, trae la de inglés como respaldo.
    """
    
    # Limpiamos el término de búsqueda
    clean_term = search_term.strip().replace('"', '').replace("'", "")
    
    # --- CAMBIO CLAVE AQUÍ ---
    # Usamos una consulta que permite español O inglés ('en')
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    
    SELECT DISTINCT ?resource ?label ?abstract WHERE {
        # 1. Buscar coincidencia en el nombre (Label)
        ?resource rdfs:label ?label .
        ?label bif:contains "'%s'" .
        
        # Filtramos para que el título coincida con el idioma buscado (o inglés por defecto)
        FILTER(LANG(?label) = "%s" || LANG(?label) = "en")
        
        # 2. EXTRAER LA DESCRIPCIÓN (dbo:abstract)
        # Aquí está el truco: Permitimos español ('es') O inglés ('en')
        OPTIONAL { 
            ?resource dbo:abstract ?abstract .
            FILTER(LANG(?abstract) = "es" || LANG(?abstract) = "en") 
        }
        
        # Aseguramos que sea un recurso de DBpedia
        FILTER(STRSTARTS(STR(?resource), "http://dbpedia.org/resource/"))
    }
    LIMIT 5
    """ % (clean_term, lang)
    
    try:
        print(f"Consultando DBpedia para: {clean_term}...")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(10) # 10 segundos máximo de espera
        
        results = sparql.query().convert()
        
        dbpedia_results = []
        # Usamos un conjunto para evitar duplicados si DBpedia manda inglés y español a la vez
        seen_resources = set()

        for result in results["results"]["bindings"]:
            resource_uri = result["resource"]["value"]
            
            # Si ya procesamos este recurso, lo saltamos para no repetir tarjetas
            if resource_uri in seen_resources:
                continue
            seen_resources.add(resource_uri)

            # Obtener el Abstract (Descripción)
            description = "Sin descripción disponible."
            if "abstract" in result:
                description = result["abstract"]["value"]
                
                # Opcional: Si es muy largo, lo cortamos a 300 caracteres
                if len(description) > 300:
                    description = description[:300] + "..."

            dbpedia_results.append({
                "resource": { "value": resource_uri },
                "label": { "value": result["label"]["value"] },
                "abstract": { "value": description }, # Aquí va el texto de tu imagen
                "date": { "value": "" },
                "author": { "value": "DBpedia" }
            })
        
        return dbpedia_results

    except Exception as e:
        print(f"Error en DBpedia: {e}")
        return []
   
def infer_properties(subject):
    """Realiza inferencias sobre un sujeto en la ontología"""
    inferred = {}
    
    # Obtener todas las clases del sujeto (incluyendo superclases)
    classes = set()
    for s, p, o in g.triples((subject, RDF.type, None)):
        classes.add(o)
        # Obtener superclases
        for s2, p2, o2 in g.triples((o, RDFS.subClassOf, None)):
            classes.add(o2)
    
    inferred['classes'] = [str(c) for c in classes]
    
    # Inferir propiedades basadas en las clases
    properties = set()
    for class_uri in classes:
        for s, p, o in g.triples((class_uri, RDFS.domain, None)):
            properties.add(p)
    
    inferred['possible_properties'] = [str(p) for p in properties]
    
    return inferred

@app.route("/", methods=["GET", "POST"])
def search():
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    
    local_results = []
    dbpedia_results = []
    keyword = request.args.get('keyword', '')
    
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        lang = request.form.get("lang", lang)
    
    if keyword:
        # Determinar el tipo de búsqueda
        search_type = "general"
        search_filters = []
        
        # Búsqueda por autor
        if "autor" in keyword.lower() or "author" in keyword.lower():
            search_type = "autor"
            author_name = keyword.replace("autor:", "").replace("author:", "").strip()
            search_filters.append(f"CONTAINS(LCASE(STR(?autor)), LCASE(\"{author_name}\"))")
        
        # Búsqueda por tema
        elif "tema" in keyword.lower() or "topic" in keyword.lower():
            search_type = "tema"
            topic = keyword.replace("tema:", "").replace("topic:", "").strip()
            search_filters.append(f"CONTAINS(LCASE(STR(?tematica)), LCASE(\"{topic}\"))")
        
        # Búsqueda por noticias verificadas
        elif "noticias verificadas" in keyword.lower() or "verified news" in keyword.lower():
            search_type = "verificadas"
            search_filters.append("?estadoVerificacion = untitled-ontology-3:Verificada")
        
        # Búsqueda por fecha
        elif "fecha" in keyword.lower() or "date" in keyword.lower():
            search_type = "fecha"
            date = keyword.replace("fecha:", "").replace("date:", "").strip()
            search_filters.append(f"STR(?fecha) = \"{date}\"")
        
        # Búsqueda general
        else:
            search_filters = [
                f"CONTAINS(LCASE(STR(?titulo)), LCASE(\"{keyword}\"))",
                f"CONTAINS(LCASE(STR(?tematica)), LCASE(\"{keyword}\"))",
                f"CONTAINS(LCASE(STR(?autor)), LCASE(\"{keyword}\"))"
            ]
        
        # Construir la consulta SPARQL dinámicamente
        query = f"""
        PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        
        SELECT DISTINCT ?noticia ?titulo ?fecha ?tematica ?autor ?estadoVerificacion ?enlaceDBpedia
        WHERE {{
            ?noticia rdf:type ?tipoNoticia .
            ?tipoNoticia rdfs:subClassOf* untitled-ontology-3:Noticia .

            OPTIONAL {{ ?noticia untitled-ontology-3:Título ?titulo . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Fecha_publicación ?fecha . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Temática ?tematica . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Autor ?autor . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:EnlaceDBpedia ?enlaceDBpedia . }}
            
            {"FILTER (" + " || ".join(search_filters) + ")" if search_filters else ""}
            
            OPTIONAL {{
                ?verificacion untitled-ontology-3:evalua ?noticia ;
                              untitled-ontology-3:Estado ?estadoVerificacion .
            }}
        }}
        ORDER BY DESC(?fecha)
        """
        
        try:
            query_results = g.query(query)
            local_results = []
            
            for row in query_results:
                # Formatear la fecha
                fecha = row.fecha.toPython().strftime("%Y-%m-%d") if hasattr(row.fecha, 'toPython') else str(row.fecha)
                
                # Traducir contenido si es necesario
                titulo = translate_text(str(row.titulo), 'es', lang) if row.titulo else ""
                tematica = translate_text(str(row.tematica), 'es', lang) if row.tematica else ""
                autor = translate_text(str(row.autor), 'es', lang) if row.autor else ""
                
                local_results.append({
                    "uri": str(row.noticia),
                    "titulo": titulo or "Sin título",
                    "fecha": fecha or "?",
                    "tematica": tematica or "?",
                    "autor": autor or "?",
                    "verificacion": str(row.estadoVerificacion) if row.estadoVerificacion else TRANSLATIONS['not_verified'][lang],
                    "enlaceDBpedia": str(row.enlaceDBpedia) if row.enlaceDBpedia else None,
                    "original_lang": "es"
                })
            
        except Exception as e:
            print(f"Error en la consulta SPARQL local: {e}")
        
        # Consultar DBpedia solo para búsquedas generales
        if search_type == "general":
            dbpedia_results = query_dbpedia(keyword, lang)

    return render_template(
        "search.html",
        local_results=local_results,
        dbpedia_results=dbpedia_results,
        keyword=keyword,
        languages=LANGUAGES,
        current_lang=lang,
        translations=TRANSLATIONS,
        dark_mode=dark_mode
    )

@app.route("/noticia/<path:uri>")
def detalle_noticia(uri):
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    keyword = request.args.get('keyword', '')
    
    # Decodificar URI (maneja caracteres especiales)
    try:
        uri_decoded = urllib.parse.unquote(uri)
    except:
        uri_decoded = uri
    
    # Consulta para obtener todos los detalles de una noticia específica
    query = """
    PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?propiedad ?valor
    WHERE {
        <%s> ?propiedad ?valor .
        FILTER (
            STRSTARTS(STR(?propiedad), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#") ||
            ?propiedad IN (rdf:type, rdfs:label, rdfs:comment)
        )
    }
    """ % uri_decoded
    
    detalles = {}
    try:
        for row in g.query(query):
            prop_name = str(row.propiedad).split("#")[-1] if "#" in str(row.propiedad) else str(row.propiedad)
            
            # Manejar diferentes tipos de valores
            if isinstance(row.valor, Literal):
                if row.valor.datatype == XSD.dateTime:
                    detalles[prop_name] = row.valor.toPython().strftime("%Y-%m-%d")
                else:
                    detalles[prop_name] = str(row.valor)
            else:
                detalles[prop_name] = str(row.valor)
    except Exception as e:
        print(f"Error al obtener detalles: {e}")
    
    # Obtener inferencias para la página de detalle
    inferred = infer_properties(URIRef(uri_decoded))
    
    return render_template(
        "detalle.html",
        noticia=detalles,
        inferred=inferred,
        translations=TRANSLATIONS,
        languages=LANGUAGES,
        current_lang=lang,
        dark_mode=dark_mode,
        keyword=keyword
    )

@app.route("/toggle_dark_mode", methods=["POST"])
def toggle_dark_mode():
    dark_mode = request.json.get('dark_mode', True)
    response = jsonify({"success": True})
    response.set_cookie('dark_mode', str(dark_mode).lower())
    return response

if __name__ == "__main__":
    app.run(debug=True)