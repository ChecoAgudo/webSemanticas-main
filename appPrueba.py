from flask import Flask, request, render_template, jsonify, redirect, url_for
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery
import os
import urllib.parse
from googletrans import Translator

# Configurar SPARQL endpoint de DBpedia (en línea)
sparql_online = SPARQLWrapper("http://dbpedia.org/sparql")
sparql_online.setReturnFormat(JSON)
sparql_online.setTimeout(30)  # 30 segundos de timeout

app = Flask(__name__)
translator = Translator()

# ============ FUNCIONES DE DETECCIÓN Y TRADUCCIÓN ============
def detect_language(text):
    """Detecta el idioma de un texto"""
    try:
        if not text or text.strip() == "":
            return 'es'  # Por defecto español
        detection = translator.detect(text)
        return detection.lang
    except Exception as e:
        print(f"Error detectando idioma: {e}")
        return 'es'

def translate_keyword_for_search(keyword, target_lang, ontology_lang='es'):
    """
    Traduce la palabra clave para búsqueda según el contexto:
    - target_lang: idioma de la interfaz
    - ontology_lang: idioma de la ontología local (español)
    """
    try:
        # Detectar idioma del término de búsqueda
        src_lang = detect_language(keyword)
        
        # Si ya está en el idioma objetivo, no traducir
        if src_lang == target_lang:
            return keyword, src_lang, target_lang
        
        # Traducir al idioma objetivo
        translated = translator.translate(keyword, src=src_lang, dest=target_lang)
        return translated.text, src_lang, target_lang
        
    except Exception as e:
        print(f"Error traduciendo palabra clave: {e}")
        return keyword, 'es', target_lang

def get_search_keywords(keyword, interface_lang):
    """
    Devuelve las palabras clave traducidas para cada fuente:
    - Para ontología local: en español (nuestra ontología está en español)
    - Para DBpedia: en el idioma de la interfaz (puede buscar en varios idiomas)
    """
    # Palabra clave para ontología local (siempre en español)
    keyword_for_ontology = keyword
    if interface_lang != 'es':
        # Si la interfaz no está en español, traducir al español para buscar en la ontología
        keyword_for_ontology, _, _ = translate_keyword_for_search(keyword, 'es')
    
    # Palabra clave para DBpedia (en el idioma de la interfaz)
    keyword_for_dbpedia = keyword
    if detect_language(keyword) != interface_lang:
        keyword_for_dbpedia, _, _ = translate_keyword_for_search(keyword, interface_lang)
    
    return {
        'original': keyword,
        'for_ontology': keyword_for_ontology,  # En español para ontología local
        'for_dbpedia': keyword_for_dbpedia,    # En idioma de interfaz para DBpedia
        'interface_lang': interface_lang
    }

# ============ CONFIGURACIÓN DE GRAFOS ============
# Grafo principal que combina TODO
g = Graph()

# Cargar múltiples fuentes de datos
def cargar_datos():
    """Carga todos los datos RDF/OWL/TTL disponibles"""
    archivos = [
        ("noticias_ontologia.rdf", "xml"),
        ("noticias_detalladas.ttl", "turtle"),
        ("dbpedia_local.ttl", "turtle")
    ]
    
    total_triples = 0
    for archivo, formato in archivos:
        if os.path.exists(archivo):
            try:
                print(f"🔄 Intentando cargar: {archivo} como {formato}...")
                triples_iniciales = len(g)
                g.parse(archivo, format=formato)
                triples_archivo = len(g) - triples_iniciales
                total_triples = len(g)
                print(f"✅ {archivo}: {triples_archivo} triples cargados")
                
                # Diagnóstico: ver algunos triples
                if archivo == "noticias_detalladas.ttl" and triples_archivo > 0:
                    print("   🔍 Muestra de datos cargados:")
                    query_diagnostico = """
                    SELECT ?s ?p ?o WHERE {
                        ?s ?p ?o .
                        FILTER(STRSTARTS(STR(?s), "http://dbpedia.org/resource/Noticia_"))
                    } LIMIT 3
                    """
                    try:
                        for row in g.query(query_diagnostico):
                            print(f"      {row.s} -> {row.p} -> {row.o}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"❌ Error cargando {archivo}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"📭 {archivo} no encontrado")
    
    print(f"📊 TOTAL: {len(g)} triples en el grafo combinado")
    
    # Consulta de diagnóstico
    print("\n🔍 Diagnóstico de datos cargados:")
    query_count = """
    SELECT (COUNT(DISTINCT ?noticia) as ?total)
    WHERE {
        ?noticia a ?tipo .
        FILTER(STRSTARTS(STR(?tipo), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#"))
    }
    """
    try:
        for row in g.query(query_count):
            print(f"   📰 Noticias encontradas: {row.total}")
    except Exception as e:
        print(f"   ❌ Error en consulta de diagnóstico: {e}")

# Ejecutar carga al inicio
cargar_datos()

# Namespaces
UNTITLED = Namespace("http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")

# ============ CONFIGURACIÓN DE IDIOMAS ============
LANGUAGES = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português'
}

TRANSLATIONS = {
    'search_placeholder': {'es': 'Buscar noticias...', 'en': 'Search news...', 'pt': 'Pesquisar notícias...'},
    'search_button': {'es': 'Buscar', 'en': 'Search', 'pt': 'Pesquisar'},
    'title': {'es': 'Buscador de Noticias', 'en': 'News Search Engine', 'pt': 'Mecanismo de busca de notícias'},
    'no_results': {'es': 'No se encontraron noticias para', 'en': 'No news found for', 'pt': 'Nenhuma notícia encontrada para'},
    'results_for': {'es': 'Resultados para', 'en': 'Results for', 'pt': 'Resultados para'},
    'date': {'es': 'Fecha', 'en': 'Date', 'pt': 'Data'},
    'topic': {'es': 'Tema', 'en': 'Topic', 'pt': 'Tema'},
    'author': {'es': 'Autor', 'en': 'Author', 'pt': 'Autor'},
    'verification': {'es': 'Verificación', 'en': 'Verification', 'pt': 'Verificação'},
    'not_verified': {'es': 'No verificada', 'en': 'Not verified', 'pt': 'Não verificada'},
    'view_details': {'es': 'Ver detalles', 'en': 'View details', 'pt': 'Ver detalhes'},
    'view_on_dbpedia': {'es': 'Ver en DBpedia', 'en': 'View on DBpedia', 'pt': 'Ver no DBpedia'},
    'local_results': {'es': 'Resultados Locales', 'en': 'Local Results', 'pt': 'Resultados Locais'},
    'dbpedia_results': {'es': 'Resultados de DBpedia', 'en': 'DBpedia Results', 'pt': 'Resultados do DBpedia'},
    'inferred_results': {'es': 'Resultados Inferidos', 'en': 'Inferred Results', 'pt': 'Resultados Inferidos'},
    'back': {'es': 'Volver', 'en': 'Back', 'pt': 'Voltar'},
    'news_details': {'es': 'Detalle de la Noticia', 'en': 'News Details', 'pt': 'Detalhes da Notícia'},
    'dark_mode': {'es': 'Modo Oscuro', 'en': 'Dark Mode', 'pt': 'Modo Escuro'},
    'light_mode': {'es': 'Modo Claro', 'en': 'Light Mode', 'pt': 'Modo Claro'},
    'translated_from': {'es': 'Traducido del', 'en': 'Translated from', 'pt': 'Traduzido do'},
    'no_dbpedida_results': {'es': 'No se encontraron resultados en DBpedia', 'en': 'No results found in DBpedia', 'pt': 'Nenhum resultado encontrado no DBpedia'},
    'properties': {'es': 'Propiedades', 'en': 'Properties', 'pt': 'Propriedades'},
    'type': {'es': 'Tipo', 'en': 'Type', 'pt': 'Tipo'},
    'content': {'es': 'Contenido', 'en': 'Content', 'pt': 'Conteúdo'},
    'location': {'es': 'Ubicación', 'en': 'Location', 'pt': 'Localização'},
    'language': {'es': 'Idioma', 'en': 'Language', 'pt': 'Idioma'},
    'multimedia': {'es': 'Multimedia', 'en': 'Multimedia', 'pt': 'Multimídia'},
    'citations': {'es': 'Citas', 'en': 'Citations', 'pt': 'Citações'},
    'political_focus': {'es': 'Enfoque Político', 'en': 'Political Focus', 'pt': 'Foco Político'},
    'tone': {'es': 'Tono', 'en': 'Tone', 'pt': 'Tom'},
    'structure': {'es': 'Estructura', 'en': 'Structure', 'pt': 'Estrutura'},
    'diffusion': {'es': 'Difusión', 'en': 'Diffusion', 'pt': 'Difusão'},
    'authorship': {'es': 'Autoría', 'en': 'Authorship', 'pt': 'Autoria'},
    'view_details': {'es': 'Ver detalles','en': 'View details','pt': 'Ver detalhes'},
    'view_on_dbpedia': {'es': 'Ver en DBpedia','en': 'View on DBpedia','pt': 'Ver no DBpedia'},
    'dbpedia_results': {'es': 'Resultados de DBpedia','en': 'DBpedia Results','pt': 'Resultados do DBpedia'},
    'type': {'es': 'Tipo','en': 'Type','pt': 'Tipo'},
    'descripcion': {'es': 'Tipo','en': 'Type','pt': 'Tipo'},
    'filter_by_type': {'es': 'Filtrar por tipo', 'en': 'Filter by type', 'pt': 'Filtrar por tipo'},
    'columns': {'es': 'Columnas', 'en': 'Columns', 'pt': 'Colunas'},
    'reports': {'es': 'Reportajes', 'en': 'Reports', 'pt': 'Reportagens'},
    'news': {'es': 'Noticias', 'en': 'News', 'pt': 'Notícias'},
    'editorials': {'es': 'Editoriales', 'en': 'Editorials', 'pt': 'Editoriais'},
    'meta_description': {
        'es': 'Buscador inteligente de noticias que combina datos locales con DBpedia',
        'en': 'Intelligent news search engine combining local data with DBpedia',
        'pt': 'Mecanismo de busca inteligente de notícias que combina dados locais com DBpedia'
    },
    
    'meta_keywords': {
        'es': 'noticias, buscador, DBpedia, ontología, inteligencia artificial, búsqueda semántica',
        'en': 'news, search engine, DBpedia, ontology, artificial intelligence, semantic search',
        'pt': 'notícias, mecanismo de busca, DBpedia, ontologia, inteligência artificial, busca semântica'
    },
    
    'recursos_relacionados': {
        'es': 'Recursos Relacionados en DBpedia',
        'en': 'Related Resources in DBpedia',
        'pt': 'Recursos Relacionados no DBpedia'
    },
    
    'recurso_relacionado': {
        'es': 'Recurso relacionado encontrado en DBpedia',
        'en': 'Related resource found in DBpedia',
        'pt': 'Recurso relacionado encontrado no DBpedia'
    },
    
    'buscar_en_dbpedia_externa': {
        'es': 'Buscar en DBpedia Externa',
        'en': 'Search in External DBpedia',
        'pt': 'Pesquisar no DBpedia Externa'
    },
    
    'buscar_en_dbpedia_desc': {
        'es': 'Esta noticia podría tener información relacionada en DBpedia.org',
        'en': 'This news might have related information in DBpedia.org',
        'pt': 'Esta notícia pode ter informações relacionadas no DBpedia.org'
    },
    
    'enlace_directo_dbpedia': {
        'es': 'Enlace directo a DBpedia',
        'en': 'Direct link to DBpedia',
        'pt': 'Link direto para o DBpedia'
    },
    
    'enlace_directo_dbpedia_desc': {
        'es': 'Este es un recurso directamente de DBpedia:',
        'en': 'This is a resource directly from DBpedia:',
        'pt': 'Este é um recurso diretamente do DBpedia:'
    },
    
    'haz_clic_para_ver_detalles': {
        'es': 'Haz clic para ver detalles completos',
        'en': 'Click to view full details',
        'pt': 'Clique para ver detalhes completos'
    },
    
    'fuente': {
        'es': 'Fuente',
        'en': 'Source',
        'pt': 'Fonte'
    },

    'no_se_encontraron': {
        'es': 'No se encontraron',
        'en': 'No',
        'pt': 'Não foram encontrados'
    },
    
    'ver': {
        'es': 'Ver',
        'en': 'View',
        'pt': 'Ver'
    },
}

def translate_text(text, dest_lang='es', src_lang=None):
    """Traduce texto entre idiomas. Si src_lang es None, detecta automáticamente."""
    try:
        if not text or text == "?" or text.strip() == "":
            return text
            
        # Si no se especifica src_lang, detectarlo automáticamente
        if src_lang is None:
            src_lang = detect_language(text)
            
        if src_lang == dest_lang:
            return text
            
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        print(f"Error traduciendo texto '{text}': {e}")
        return text
    
def query_dbpedia_online(keyword, lang='es'):
    """Consulta DBpedia en línea para información relacionada con la palabra clave"""
    # Mapear idiomas a códigos de DBpedia
    lang_map = {'es': 'es', 'en': 'en', 'pt': 'pt'}
    dbpedia_lang = lang_map.get(lang, 'en')
    
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dct: <http://purl.org/dc/terms/>
    
    SELECT DISTINCT ?resource ?label ?abstract ?type ?thumbnail
    WHERE {{
        ?resource rdfs:label ?label .
        FILTER(LANG(?label) = "{dbpedia_lang}")
        FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{keyword}")))
        
        OPTIONAL {{ 
            ?resource dbo:abstract ?abstract .
            FILTER(LANG(?abstract) = "{dbpedia_lang}") 
        }}
        
        OPTIONAL {{
            ?resource dct:subject ?type .
        }}
        
        OPTIONAL {{
            ?resource dbo:thumbnail ?thumbnail .
        }}
        
        FILTER(STRSTARTS(STR(?resource), "http://dbpedia.org/resource/"))
    }}
    LIMIT 10
    """
    
    try:
        sparql_online.setQuery(query)
        print(f"🌐 Consultando DBpedia en línea para: '{keyword}' en {dbpedia_lang}")
        
        results = sparql_online.query().convert()
        dbpedia_results = []
        
        for result in results["results"]["bindings"]:
            # Obtener tipo (si está disponible)
            tipo = "Recurso"
            if "type" in result:
                tipo_full = result["type"]["value"]
                tipo = tipo_full.split("/")[-1] if "/" in tipo_full else tipo_full
            
            dbpedia_results.append({
                "resource": {"value": result["resource"]["value"]},
                "label": {"value": result["label"]["value"]},
                "abstract": {"value": result.get("abstract", {}).get("value", "Descripción no disponible")},
                "type": tipo,
                "thumbnail": result.get("thumbnail", {}).get("value", None),
                "source": "online"
            })
        
        print(f"✅ DBpedia en línea: {len(dbpedia_results)} resultados")
        return dbpedia_results
        
    except Exception as e:
        print(f"❌ Error consultando DBpedia en línea: {e}")
        return None

# ============ BÚSQUEDA UNIFICADA ============
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
    
    print(f"\n🔍 Búsqueda iniciada: '{keyword}' en idioma '{lang}'")
    
    if keyword:
        # Obtener palabras clave traducidas para cada fuente
        keywords = get_search_keywords(keyword, lang)
        print(f"🔤 Palabras clave procesadas:")
        print(f"   Original: {keywords['original']}")
        print(f"   Para ontología (español): {keywords['for_ontology']}")
        print(f"   Para DBpedia ({lang}): {keywords['for_dbpedia']}")
        
        # ===== BÚSQUEDA EN NOTICIAS LOCALES =====
        # Usar keyword_for_ontology (siempre en español)
        query_noticias = f"""
        PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?noticia ?titulo ?fecha ?tematica ?autor ?tipo ?ubicacion ?idioma
        WHERE {{
            ?noticia a ?tipo .
            
            # Aceptar cualquier tipo de nuestra ontología
            FILTER(
                STRSTARTS(STR(?tipo), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#")
            )
            
            # Propiedades obligatorias (evitar noticias incompletas)
            ?noticia untitled-ontology-3:Título|untitled-ontology-3:Titulo ?titulo .
            ?noticia untitled-ontology-3:Autor ?autor .
            
            # Propiedades opcionales
            OPTIONAL {{ ?noticia untitled-ontology-3:Fecha_publicacion|untitled-ontology-3:Fecha_publicación ?fecha . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Tematica|untitled-ontology-3:Temática ?tematica . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Ubicacion|untitled-ontology-3:Ubicación ?ubicacion . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Idioma ?idioma . }}
            
            # Búsqueda más específica - usar keyword_for_ontology (español)
            FILTER(
                # Buscar solo en título y temática
                (regex(LCASE(STR(?titulo)), LCASE("{keywords['for_ontology']}"), "i")) ||
                (BOUND(?tematica) && regex(LCASE(STR(?tematica)), LCASE("{keywords['for_ontology']}"), "i"))
            )
            
            # Excluir noticias sin título o autor
            FILTER(BOUND(?titulo) && BOUND(?autor) && STR(?titulo) != "" && STR(?autor) != "")
        }}
        ORDER BY DESC(?fecha)
        LIMIT 10
        """
        
        print(f"📋 Ejecutando consulta SPARQL local para '{keywords['for_ontology']}'")
        
        try:
            results = g.query(query_noticias)
            count = 0
            uris_vistos = set()
            
            for row in results:
                noticia_uri = str(row.noticia)
                if noticia_uri in uris_vistos:
                    continue
                    
                uris_vistos.add(noticia_uri)
                count += 1
                
                # Formatear fecha
                fecha = str(row.fecha) if row.fecha else "Fecha no disponible"
                if "T" in fecha:
                    fecha = fecha.split("T")[0]
                
                # Traducir contenido del español al idioma de la interfaz
                titulo = translate_text(str(row.titulo), lang, 'es') if row.titulo else "Sin título"
                tematica = translate_text(str(row.tematica), lang, 'es') if row.tematica else "General"
                autor = translate_text(str(row.autor), lang, 'es') if row.autor else "Anónimo"
                ubicacion = translate_text(str(row.ubicacion), lang, 'es') if row.ubicacion else "No especificada"

                # Obtener tipo simplificado
                tipo_full = str(row.tipo)
                tipo = tipo_full.split("#")[-1] if "#" in tipo_full else tipo_full
                
                local_results.append({
                    "uri": noticia_uri,
                    "titulo": titulo,
                    "fecha": fecha,
                    "tematica": tematica,
                    "autor": autor,
                    "tipo": tipo,
                    "ubicacion": ubicacion,
                    "idioma": str(row.idioma) if row.idioma else "Español",
                    "enfoque": "Neutral",
                    "original_lang": "es"
                })
            
            print(f"✅ Encontradas {count} noticias únicas")
            
        except Exception as e:
            print(f"❌ Error en consulta noticias: {e}")
            import traceback
            traceback.print_exc()
        
        # ===== BÚSQUEDA EN DBPEDIA (EN LÍNEA + LOCAL) =====
        # Usar keyword_for_dbpedia (en idioma de interfaz)
        print(f"🌐 Intentando búsqueda en DBpedia en línea para '{keywords['for_dbpedia']}' en {lang}...")
        
        # Intentar primero DBpedia en línea
        dbpedia_online_results = query_dbpedia_online(keywords['for_dbpedia'], lang)
        
        if dbpedia_online_results is not None:
            # Usar resultados en línea si hay conexión
            count_dbpedia = 0
            recursos_vistos = set()
            
            for result in dbpedia_online_results:
                recurso_uri = result["resource"]["value"]
                if recurso_uri in recursos_vistos:
                    continue
                    
                recursos_vistos.add(recurso_uri)
                count_dbpedia += 1
                
                # Los resultados ya vienen en el idioma correcto (filtrado por lang)
                label = result["label"]["value"]
                abstract = result["abstract"]["value"]
                
                if len(abstract) > 250:
                    abstract = abstract[:250] + "..."
                
                dbpedia_results.append({
                    "resource": result["resource"],
                    "label": {"value": label},
                    "abstract": {"value": abstract},
                    "type": result["type"],
                    "all_types": [result["type"]],
                    "author": {"value": "DBpedia (En línea)"},
                    "thumbnail": result["thumbnail"],
                    "source": "online"
                })
            
            print(f"✅ Usando {count_dbpedia} resultados de DBpedia en línea")
            
        else:
            # Si falla la conexión, usar DBpedia local
            print(f"📴 Conexión a internet no disponible, usando DBpedia local para '{keywords['for_ontology']}'...")
            # Usar keyword_for_ontology (español) para búsqueda local
            query_dbpedia_local = f"""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            
            SELECT DISTINCT ?recurso ?label ?abstract (GROUP_CONCAT(DISTINCT STR(?type); separator="|") as ?tipos)
            WHERE {{
                ?recurso rdfs:label ?label .
                FILTER(LANG(?label) = "es")
                
                OPTIONAL {{ ?recurso dbo:abstract ?abstract . FILTER(LANG(?abstract) = "es") }}
                OPTIONAL {{ ?recurso a ?type }}
                
                FILTER(
                    regex(LCASE(STR(?label)), LCASE("{keywords['for_ontology']}"), "i") ||
                    (BOUND(?abstract) && regex(LCASE(STR(?abstract)), LCASE("{keywords['for_ontology']}"), "i"))
                )
            }}
            GROUP BY ?recurso ?label ?abstract
            LIMIT 5
            """
            
            try:
                results = g.query(query_dbpedia_local)
                count_dbpedia = 0
                recursos_vistos = set()
                
                for row in results:
                    recurso_uri = str(row.recurso)
                    if recurso_uri in recursos_vistos:
                        continue
                        
                    recursos_vistos.add(recurso_uri)
                    count_dbpedia += 1
                    
                    # Traducir contenido del español al idioma de la interfaz
                    label = translate_text(str(row.label), lang, 'es') if row.label else f"Recurso DBpedia"
                    abstract = translate_text(str(row.abstract), lang, 'es') if row.abstract else "Descripción no disponible"
                    
                    if len(abstract) > 250:
                        abstract = abstract[:250] + "..."
                    
                    tipos = []
                    if hasattr(row, 'tipos') and row.tipos:
                        tipos_raw = str(row.tipos).split('|')
                        for tipo_raw in tipos_raw:
                            tipo_clean = tipo_raw.split("/")[-1] if "/" in tipo_raw else tipo_raw
                            if tipo_clean and tipo_clean not in tipos:
                                tipos.append(tipo_clean)
                    
                    if not tipos:
                        tipos = ["Recurso"]
                    
                    dbpedia_results.append({
                        "resource": {"value": recurso_uri},
                        "label": {"value": label},
                        "abstract": {"value": abstract},
                        "type": tipos[0],
                        "all_types": tipos,
                        "author": {"value": "DBpedia (Local)"},
                        "thumbnail": None,
                        "source": "local"
                    })
                
                print(f"✅ Encontrados {count_dbpedia} recursos DBpedia locales")
                
            except Exception as e:
                print(f"❌ Error en consulta DBpedia local: {e}")
    
    return render_template(
        "search.html",
        local_results=local_results,
        dbpedia_results=dbpedia_results,
        keyword=keyword,  # Mostrar la palabra clave original
        languages=LANGUAGES,
        current_lang=lang,
        translations=TRANSLATIONS,
        dark_mode=dark_mode
    )

@app.route("/verificar_duplicados")
def verificar_duplicados():
    """Verifica datos duplicados en el sistema"""
    
    # Consulta para noticias con mismo título
    query_duplicados = """
    PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
    
    SELECT ?titulo (COUNT(?noticia) as ?count)
    WHERE {
        ?noticia untitled-ontology-3:Título ?titulo .
    }
    GROUP BY ?titulo
    HAVING (?count > 1)
    ORDER BY DESC(?count)
    """
    
    resultados = []
    try:
        for row in g.query(query_duplicados):
            resultados.append({
                "titulo": str(row.titulo),
                "count": int(row.count)
            })
    except Exception as e:
        return f"Error: {e}"
    
    html = "<h1>Diagnóstico de Duplicados</h1>"
    if resultados:
        html += "<h3>Títulos duplicados encontrados:</h3><ul>"
        for r in resultados:
            html += f"<li>'{r['titulo']}': {r['count']} veces</li>"
        html += "</ul>"
    else:
        html += "<p>No se encontraron títulos duplicados.</p>"
    
    return html

# ============ DETALLE DE NOTICIA ============
@app.route("/detalle/<path:uri>")
def detalle_noticia(uri):
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    keyword = request.args.get('keyword', '')
    
    # Decodificar URI
    try:
        uri_decoded = urllib.parse.unquote(uri)
    except:
        uri_decoded = uri
    
    # Verificar si es una noticia local o recurso DBpedia
    is_dbpedia = "dbpedia.org" in uri_decoded
    
    if is_dbpedia:
        # Consulta para recurso DBpedia con manejo de idiomas
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT ?prop ?val ?lang ?datatype
        WHERE {{
            <{uri_decoded}> ?prop ?val .
            OPTIONAL {{ 
                BIND(LANG(?val) AS ?lang) 
                BIND(DATATYPE(?val) AS ?datatype)
            }}
            FILTER(
                STRSTARTS(STR(?prop), "http://dbpedia.org/ontology/") ||
                STRSTARTS(STR(?prop), "http://www.w3.org/2000/01/rdf-schema#") ||
                ?prop = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ||
                ?prop = dct:subject
            )
        }}
        LIMIT 40
        """
    else:
        # Consulta para noticia local
        query = f"""
        PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
        
        SELECT ?prop ?val ?datatype
        WHERE {{
            <{uri_decoded}> ?prop ?val .
            OPTIONAL {{ BIND(DATATYPE(?val) AS ?datatype) }}
            FILTER(
                STRSTARTS(STR(?prop), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#") ||
                ?prop = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ||
                ?prop = <http://www.w3.org/2000/01/rdf-schema#label>
            )
        }}
        """
    
    detalles = {}
    propiedades_traduccibles = []  # Para propiedades que pueden traducirse
    
    try:
        for row in g.query(query):
            prop_name = str(row.prop)
            
            # Formatear nombre de propiedad
            if "#" in prop_name:
                prop_short = prop_name.split("#")[-1]
            elif "/" in prop_name:
                prop_short = prop_name.split("/")[-1]
            else:
                prop_short = prop_name
            
            # Obtener valor
            valor = str(row.val)
            
            # Manejar fechas
            if hasattr(row, 'datatype') and row.datatype:
                datatype_str = str(row.datatype)
                if "dateTime" in datatype_str or "date" in datatype_str:
                    valor = str(row.val).split("T")[0]
            
            # Determinar si la propiedad es traducible (texto, no URI)
            es_traducible = not valor.startswith("http://") and not valor.startswith("urn:")
            
            # Manejar traducción para recursos DBpedia (tienen idioma en la consulta)
            if is_dbpedia and hasattr(row, 'lang') and row.lang:
                lang_valor = str(row.lang)
                if lang_valor != lang and es_traducible:
                    valor = translate_text(valor, lang, lang_valor)
                elif es_traducible:
                    # Si está en el idioma correcto pero es español y la interfaz no
                    if lang_valor == 'es' and lang != 'es' and es_traducible:
                        valor = translate_text(valor, lang, 'es')
            elif not is_dbpedia and es_traducible and lang != 'es':
                # Para noticias locales, traducir del español al idioma de interfaz
                valor = translate_text(valor, lang, 'es')
            
            # Guardar propiedad con metadata adicional
            detalles[prop_short] = {
                "valor": valor,
                "traducido": es_traducible and lang != 'es',
                "original": str(row.val) if hasattr(row, 'val') else valor
            }
            
            # Si es texto traducible, agregar a la lista para mostrar indicador
            if es_traducible:
                propiedades_traduccibles.append(prop_short)
        
    except Exception as e:
        print(f"Error obteniendo detalles para {uri_decoded}: {e}")
        import traceback
        traceback.print_exc()
    
    # Buscar recursos relacionados en DBpedia
    recursos_relacionados = []
    if not is_dbpedia and detalles:
        # Extraer temas de los detalles
        temas = []
        for prop, info in detalles.items():
            prop_lower = prop.lower()
            if any(keyword in prop_lower for keyword in ['tematica', 'título', 'titulo', 'ubicacion', 'tema']):
                if isinstance(info, dict):
                    temas.append(info['valor'])
                else:
                    temas.append(str(info))
        
        # Buscar recursos DBpedia relacionados
        for tema in temas[:3]:  # Solo primeros 3 temas
            if len(tema) > 3:  # Evitar términos muy cortos
                try:
                    # Buscar en DBpedia local primero
                    query_relacionados = f"""
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX dbo: <http://dbpedia.org/ontology/>
                    
                    SELECT DISTINCT ?recurso ?label ?abstract
                    WHERE {{
                        ?recurso rdfs:label ?label .
                        FILTER(LANG(?label) = "es")
                        OPTIONAL {{ ?recurso dbo:abstract ?abstract . FILTER(LANG(?abstract) = "es") }}
                        FILTER(REGEX(LCASE(STR(?label)), LCASE("{tema}"), "i"))
                    }}
                    LIMIT 3
                    """
                    
                    for row in g.query(query_relacionados):
                        label = translate_text(str(row.label), lang, 'es') if row.label else f"Recurso: {tema}"
                        abstract = ""
                        if hasattr(row, 'abstract') and row.abstract:
                            abstract = translate_text(str(row.abstract), lang, 'es')
                            if len(abstract) > 150:
                                abstract = abstract[:150] + "..."
                        
                        recursos_relacionados.append({
                            "uri": str(row.recurso),
                            "label": label,
                            "abstract": abstract,
                            "tema_relacionado": tema
                        })
                except Exception as e:
                    print(f"Error buscando recursos relacionados para '{tema}': {e}")
    
    # Traducir etiquetas de propiedades para la vista
    detalles_traducidos = {}
    prop_traducciones = {
        'Título': TRANSLATIONS.get('title', {}).get(lang, 'Título'),
        'Autor': TRANSLATIONS.get('author', {}).get(lang, 'Autor'),
        'Fecha_publicacion': TRANSLATIONS.get('date', {}).get(lang, 'Fecha'),
        'Tematica': TRANSLATIONS.get('topic', {}).get(lang, 'Tema'),
        'Ubicacion': TRANSLATIONS.get('location', {}).get(lang, 'Ubicación'),
        'Idioma': TRANSLATIONS.get('language', {}).get(lang, 'Idioma'),
        'type': TRANSLATIONS.get('type', {}).get(lang, 'Tipo')
    }
    
    for prop, info in detalles.items():
        prop_traducida = prop_traducciones.get(prop, prop)
        if isinstance(info, dict):
            detalles_traducidos[prop_traducida] = info['valor']
        else:
            detalles_traducidos[prop_traducida] = info
    
    return render_template(
        "detalle.html",
        noticia=detalles_traducidos,
        noticia_original=detalles,
        is_dbpedia=is_dbpedia,
        recursos_relacionados=recursos_relacionados[:5],
        propiedades_traduccibles=propiedades_traduccibles,
        translations=TRANSLATIONS,
        languages=LANGUAGES,
        current_lang=lang,
        dark_mode=dark_mode,
        keyword=keyword,
        uri=uri_decoded,
        detect_language=detect_language  # Pasar función para usar en template si es necesario
    )

# ============ BÚSQUEDA POR TIPO ============
@app.route("/tipo/<tipo>")
def buscar_por_tipo(tipo):
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    
    # Traducir el tipo de noticia para mostrar en la interfaz
    tipo_traducido = tipo
    tipo_map = {
        'Columnas': {'es': 'Columnas', 'en': 'Columns', 'pt': 'Colunas'},
        'Reportajes': {'es': 'Reportajes', 'en': 'Reports', 'pt': 'Reportagens'},
        'Noticias': {'es': 'Noticias', 'en': 'News', 'pt': 'Notícias'},
        'Editoriales': {'es': 'Editoriales', 'en': 'Editorials', 'pt': 'Editoriais'}
    }
    
    if tipo in tipo_map and lang in tipo_map[tipo]:
        tipo_traducido = tipo_map[tipo][lang]
    
    query = f"""
    PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
    SELECT DISTINCT ?noticia ?titulo ?autor ?fecha ?tematica ?ubicacion
    WHERE {{
        ?noticia a untitled-ontology-3:{tipo} ;
                 untitled-ontology-3:Título|untitled-ontology-3:Titulo ?titulo .
        OPTIONAL {{ ?noticia untitled-ontology-3:Autor ?autor . }}
        OPTIONAL {{ ?noticia untitled-ontology-3:Fecha_publicacion|untitled-ontology-3:Fecha_publicación ?fecha . }}
        OPTIONAL {{ ?noticia untitled-ontology-3:Tematica|untitled-ontology-3:Temática ?tematica . }}
        OPTIONAL {{ ?noticia untitled-ontology-3:Ubicacion|untitled-ontology-3:Ubicación ?ubicacion . }}
    }}
    ORDER BY DESC(?fecha)
    LIMIT 10
    """
    
    resultados = []
    try:
        for row in g.query(query):
            # Traducir cada campo individualmente del español al idioma de la interfaz
            titulo = translate_text(str(row.titulo), lang, 'es') if row.titulo else "Sin título"
            
            # Para autor, fecha y otros, traducir si es necesario
            autor = translate_text(str(row.autor), lang, 'es') if row.autor else TRANSLATIONS['author'][lang]
            
            # Formatear fecha
            fecha = str(row.fecha) if row.fecha else "?"
            if fecha != "?" and "T" in fecha:
                fecha = fecha.split("T")[0]
            
            # Traducir temática y ubicación
            tematica = translate_text(str(row.tematica), lang, 'es') if row.tematica else TRANSLATIONS['topic'][lang]
            ubicacion = translate_text(str(row.ubicacion), lang, 'es') if row.ubicacion else TRANSLATIONS['location'][lang]
            
            resultados.append({
                "uri": str(row.noticia),
                "titulo": titulo,
                "autor": autor,
                "fecha": fecha,
                "tematica": tematica,
                "ubicacion": ubicacion,
                "tipo_original": tipo,
                "tipo_traducido": tipo_traducido
            })
    except Exception as e:
        print(f"Error en búsqueda por tipo '{tipo}': {e}")
        import traceback
        traceback.print_exc()
    
    return render_template(
        "busqueda_tipo.html",
        resultados=resultados,
        tipo=tipo,
        tipo_traducido=tipo_traducido,
        languages=LANGUAGES,
        current_lang=lang,
        translations=TRANSLATIONS,
        dark_mode=dark_mode
    )

# ============ FUNCIONES AUXILIARES ============
@app.route("/toggle_dark_mode", methods=["POST"])
def toggle_dark_mode():
    dark_mode = request.json.get('dark_mode', True)
    response = jsonify({"success": True})
    response.set_cookie('dark_mode', str(dark_mode).lower())
    return response

@app.route("/recargar_datos")
def recargar_datos():
    """Recarga todos los datos RDF (útil para desarrollo)"""
    global g
    g = Graph()
    cargar_datos()
    return jsonify({"status": "ok", "triples": len(g)})

# ============ DIAGNÓSTICO ============
@app.route("/diagnostico")
def diagnostico():
    """Página de diagnóstico para verificar datos"""
    
    # Consulta para contar noticias
    query_count = """
    SELECT (COUNT(DISTINCT ?s) as ?total) 
    WHERE {
        ?s a ?type .
        FILTER(STRSTARTS(STR(?type), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#"))
    }
    """
    
    # Consulta para ver ejemplos
    query_samples = """
    SELECT ?noticia ?titulo ?tipo
    WHERE {
        ?noticia a ?tipo .
        FILTER(STRSTARTS(STR(?tipo), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#"))
        OPTIONAL { ?noticia untitled-ontology-3:Título|untitled-ontology-3:Titulo ?titulo . }
    }
    LIMIT 10
    """
    
    resultados = []
    total = 0
    
    try:
        # Contar total
        for row in g.query(query_count):
            total = row.total
        
        # Obtener ejemplos
        for row in g.query(query_samples):
            resultados.append({
                "uri": str(row.noticia),
                "titulo": str(row.titulo) if row.titulo else "Sin título",
                "tipo": str(row.tipo).split("#")[-1]
            })
    except Exception as e:
        return f"Error en diagnóstico: {e}"
    
    html = f"""
    <h1>Diagnóstico del Sistema</h1>
    <h3>Total de noticias en el sistema: {total}</h3>
    <h3>Ejemplos de noticias:</h3>
    <table border="1">
        <tr><th>URI</th><th>Título</th><th>Tipo</th></tr>
    """
    
    for r in resultados:
        html += f"""
        <tr>
            <td><a href="/detalle/{r['uri']}">{r['uri'][:50]}...</a></td>
            <td>{r['titulo']}</td>
            <td>{r['tipo']}</td>
        </tr>
        """
    
    html += "</table>"
    html += f"<p>Total de triples en grafo: {len(g)}</p>"
    
    # Mostrar algunas propiedades disponibles
    query_props = """
    SELECT DISTINCT ?prop (COUNT(?s) as ?count)
    WHERE {
        ?s ?prop ?o .
        FILTER(STRSTARTS(STR(?prop), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#"))
    }
    GROUP BY ?prop
    ORDER BY DESC(?count)
    LIMIT 20
    """
    
    html += "<h3>Propiedades más comunes:</h3><ul>"
    try:
        for row in g.query(query_props):
            prop_name = str(row.prop).split("#")[-1]
            html += f"<li>{prop_name}: {row.count} ocurrencias</li>"
    except Exception as e:
        html += f"<li>Error: {e}</li>"
    
    html += "</ul>"
    
    return html

if __name__ == "__main__":
    app.run(debug=True, port=5001)