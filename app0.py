from flask import Flask, request, render_template, jsonify, redirect, url_for
from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery
import os
import urllib.parse
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

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
    'title': {'es': 'Buscador de Noticias Inteligente', 'en': 'Intelligent News Search', 'pt': 'Pesquisa Inteligente de Notícias'},
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
    'dbpedia_results': {
        'es': 'Resultados de DBpedia',
        'en': 'DBpedia Results',
        'pt': 'Resultados do DBpedia'
    },
    'type': {
        'es': 'Tipo',
        'en': 'Type',
        'pt': 'Tipo'
    },
}

def translate_text(text, src_lang, dest_lang):
    """Traduce texto entre idiomas"""
    try:
        if src_lang == dest_lang or not text or text == "?":
            return text
        translation = translator.translate(text, src=src_lang, dest=dest_lang)
        return translation.text
    except Exception as e:
        print(f"Error traduciendo texto: {e}")
        return text

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
        # ===== BÚSQUEDA EN NOTICIAS LOCALES =====
        # CONSULTA CORREGIDA - más flexible
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
            
            # Buscar propiedades - algunas pueden tener nombres ligeramente diferentes
            OPTIONAL {{ ?noticia untitled-ontology-3:Título|untitled-ontology-3:Titulo ?titulo . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Fecha_publicacion|untitled-ontology-3:Fecha_publicación ?fecha . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Tematica|untitled-ontology-3:Temática ?tematica . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Autor ?autor . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Ubicacion|untitled-ontology-3:Ubicación ?ubicacion . }}
            OPTIONAL {{ ?noticia untitled-ontology-3:Idioma ?idioma . }}
            
            # Búsqueda más flexible - en múltiples campos
            FILTER(
                # Si hay título, buscar en él
                (BOUND(?titulo) && (regex(STR(?titulo), "{keyword}", "i"))) ||
                # Si hay temática, buscar en ella
                (BOUND(?tematica) && (regex(STR(?tematica), "{keyword}", "i"))) ||
                # Si hay autor, buscar en él
                (BOUND(?autor) && (regex(STR(?autor), "{keyword}", "i"))) ||
                # Si hay ubicación, buscar en ella
                (BOUND(?ubicacion) && (regex(STR(?ubicacion), "{keyword}", "i"))) ||
                # Buscar en todas las propiedades literales del recurso
                EXISTS {{
                    ?noticia ?p ?valor .
                    FILTER(isLiteral(?valor))
                    FILTER(regex(STR(?valor), "{keyword}", "i"))
                }}
            )
        }}
        ORDER BY DESC(?fecha)
        LIMIT 50
        """
        
        print(f"📋 Ejecutando consulta SPARQL para '{keyword}'")
        
        try:
            results = g.query(query_noticias)
            count = 0
            
            for row in results:
                count += 1
                
                # Formatear fecha
                fecha = str(row.fecha) if row.fecha else "?"
                if "T" in fecha:
                    fecha = fecha.split("T")[0]
                
                # Traducir contenido
                titulo = translate_text(str(row.titulo), 'es', lang) if row.titulo else "Sin título"
                tematica = translate_text(str(row.tematica), 'es', lang) if row.tematica else "General"
                autor = translate_text(str(row.autor), 'es', lang) if row.autor else "Anónimo"
                ubicacion = translate_text(str(row.ubicacion), 'es', lang) if row.ubicacion else "No especificada"
                
                # Obtener tipo simplificado
                tipo_full = str(row.tipo)
                tipo = tipo_full.split("#")[-1] if "#" in tipo_full else tipo_full
                
                local_results.append({
                    "uri": str(row.noticia),
                    "titulo": titulo,
                    "fecha": fecha,
                    "tematica": tematica,
                    "autor": autor,
                    "tipo": tipo,
                    "ubicacion": ubicacion,
                    "idioma": str(row.idioma) if row.idioma else "Español",
                    "enfoque": "Neutral",  # Valor por defecto
                    "original_lang": "es"
                })
            
            print(f"✅ Encontradas {count} noticias para '{keyword}'")
            
        except Exception as e:
            print(f"❌ Error en consulta noticias: {e}")
            import traceback
            traceback.print_exc()
        
        # ===== BÚSQUEDA EN DBPEDIA LOCAL =====
        query_dbpedia = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?recurso ?label ?abstract ?type
        WHERE {{
            ?recurso rdfs:label ?label .
            FILTER(LANG(?label) = "es")
            
            OPTIONAL {{ ?recurso dbo:abstract ?abstract . FILTER(LANG(?abstract) = "es") }}
            OPTIONAL {{ ?recurso a ?type }}
            
            FILTER(
                regex(STR(?label), "{keyword}", "i") ||
                (BOUND(?abstract) && regex(STR(?abstract), "{keyword}", "i"))
            )
        }}
        LIMIT 20
        """
        
        try:
            results = g.query(query_dbpedia)
            count_dbpedia = 0
            
            for row in results:
                count_dbpedia += 1
                # Traducir contenido
                label = translate_text(str(row.label), 'es', lang) if row.label else f"Recurso DBpedia"
                abstract = translate_text(str(row.abstract), 'es', lang) if row.abstract else "Descripción no disponible"
                
                # Limitar longitud
                if len(abstract) > 250:
                    abstract = abstract[:250] + "..."
                
                # Obtener tipo
                tipo = str(row.type).split("/")[-1] if row.type else "Thing"
                
                dbpedia_results.append({
                    "resource": {"value": str(row.recurso)},
                    "label": {"value": label},
                    "abstract": {"value": abstract},
                    "type": tipo,
                    "author": {"value": "DBpedia"},
                    "thumbnail": None
                })
            
            print(f"✅ Encontrados {count_dbpedia} recursos DBpedia para '{keyword}'")
            
        except Exception as e:
            print(f"❌ Error en consulta DBpedia: {e}")
    
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
        # Consulta para recurso DBpedia
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?prop ?val ?lang
        WHERE {{
            <{uri_decoded}> ?prop ?val .
            OPTIONAL {{ BIND(LANG(?val) AS ?lang) }}
            FILTER(
                STRSTARTS(STR(?prop), "http://dbpedia.org/ontology/") ||
                STRSTARTS(STR(?prop), "http://www.w3.org/2000/01/rdf-schema#") ||
                ?prop = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
            )
        }}
        LIMIT 30
        """
    else:
        # Consulta para noticia local
        query = f"""
        PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
        
        SELECT ?prop ?val
        WHERE {{
            <{uri_decoded}> ?prop ?val .
            FILTER(
                STRSTARTS(STR(?prop), "http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#") ||
                ?prop = <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ||
                ?prop = <http://www.w3.org/2000/01/rdf-schema#label>
            )
        }}
        """
    
    detalles = {}
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
            
            # Manejar fechas y literales
            if hasattr(row.val, 'datatype') and row.val.datatype:
                if XSD.dateTime in row.val.datatype or XSD.date in row.val.datatype:
                    valor = str(row.val).split("T")[0]
            
            # Traducir si es texto y tiene idioma específico
            if hasattr(row, 'lang') and row.lang and row.lang != lang:
                valor = translate_text(valor, str(row.lang), lang)
            
            detalles[prop_short] = valor
        
    except Exception as e:
        print(f"Error obteniendo detalles: {e}")
    
    # Buscar recursos relacionados en DBpedia
    recursos_relacionados = []
    if not is_dbpedia:
        # Buscar si esta noticia menciona temas que existen en DBpedia
        temas = [v for k, v in detalles.items() if k.lower() in ['tematica', 'título', 'ubicacion']]
        
        for tema in temas[:3]:  # Solo primeros 3 temas
            query_relacionados = f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?recurso ?label
            WHERE {{
                ?recurso rdfs:label ?label .
                FILTER(LANG(?label) = "es" && LCASE(STR(?label)) LIKE "%{tema.lower()}%")
            }}
            LIMIT 2
            """
            
            try:
                for row in g.query(query_relacionados):
                    recursos_relacionados.append({
                        "uri": str(row.recurso),
                        "label": str(row.label)
                    })
            except:
                pass
    
    return render_template(
        "detalle.html",
        noticia=detalles,
        is_dbpedia=is_dbpedia,
        recursos_relacionados=recursos_relacionados[:5],  # Máximo 5
        translations=TRANSLATIONS,
        languages=LANGUAGES,
        current_lang=lang,
        dark_mode=dark_mode,
        keyword=keyword,
        uri=uri_decoded
    )

# ============ BÚSQUEDA POR TIPO ============
@app.route("/tipo/<tipo>")
def buscar_por_tipo(tipo):
    lang = request.args.get('lang', 'es')
    dark_mode = request.cookies.get('dark_mode', 'true') == 'true'
    
    query = f"""
    PREFIX untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#>
    SELECT ?noticia ?titulo ?autor ?fecha
    WHERE {{
        ?noticia a untitled-ontology-3:{tipo} ;
                 untitled-ontology-3:Título ?titulo .
        OPTIONAL {{ ?noticia untitled-ontology-3:Autor ?autor . }}
        OPTIONAL {{ ?noticia untitled-ontology-3:Fecha_publicacion ?fecha . }}
    }}
    LIMIT 30
    """
    
    resultados = []
    try:
        for row in g.query(query):
            resultados.append({
                "uri": str(row.noticia),
                "titulo": translate_text(str(row.titulo), 'es', lang),
                "autor": translate_text(str(row.autor), 'es', lang) if row.autor else "Anónimo",
                "fecha": str(row.fecha).split("T")[0] if row.fecha else "?"
            })
    except Exception as e:
        print(f"Error en búsqueda por tipo: {e}")
    
    return render_template(
        "busqueda_tipo.html",
        resultados=resultados,
        tipo=tipo,
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