from SPARQLWrapper import SPARQLWrapper, JSON

# Configuración
ENDPOINT = "http://dbpedia.org/sparql"
ARCHIVO_SALIDA = "dbpedia_local.ttl"

# LISTA DE TEMAS QUE QUIERES DESCARGAR
# Puedes agregar más temas a esta lista para hacer tu base de datos más grande
TEMAS = [
    # --- BOLIVIA: POLÍTICA Y ACTUALIDAD RECIENTE ---
    "Bolivia", "Estado_Plurinacional_de_Bolivia",
    "Luis_Arce", "Evo_Morales", "Jeanine_Áñez", "Carlos_Mesa", "Luis_Fernando_Camacho",
    "Crisis_política_en_Bolivia_de_2019", "Elecciones_generales_de_Bolivia_de_2020",
    "Censo_de_Población_y_Vivienda_2024_(Bolivia)", 
    "Incendios_forestales_en_Bolivia_de_2024", "Incendios_en_la_Amazonía",
    "Constitución_Política_del_Estado_(Bolivia)", "Asamblea_Legislativa_Plurinacional",

    # --- BOLIVIA: CIUDADES Y REGIONES ---
    "La_Paz", "Santa_Cruz_de_la_Sierra", "Cochabamba", "El_Alto", "Sucre", 
    "Oruro", "Potosí", "Tarija", "Trinidad_(Bolivia)", "Cobija",
    "Salar_de_Uyuni", "Lago_Titicaca", "Tiahuanaco", "Chiquitania", "Tipnis",

    # --- ECONOMÍA Y RECURSOS ---
    "Economía_de_Bolivia", "Boliviano_(moneda)", "Banco_Central_de_Bolivia",
    "Litio", "Yacimientos_de_Litio_Bolivianos", "Salar_de_Uyuni_(recurso)",
    "Gas_natural", "YPFB", "Hidrocarburos", "Exportación",
    "Inflación", "Dólar_estadounidense", "Fondo_Monetario_Internacional",
    "Mercosur", "Unasur", "BRICS",

    # --- DEPORTES (BOLIVIA Y MUNDO) ---
    "Fútbol", "Selección_de_fútbol_de_Bolivia", "Estadio_Hernando_Siles", "Estadio_Municipal_de_El_Alto",
    "Club_Bolívar", "The_Strongest", "Club_Wilstermann", "Club_Oriente_Petrolero", "Club_Blooming",
    "Héctor_Garibay", "Marcelo_Martins_Moreno", "Marco_Etcheverry",
    "Copa_América_2024", "Copa_Mundial_de_Fútbol_de_2022", "Lionel_Messi", "Kylian_Mbappé", 
    "Juegos_Olímpicos_de_París_2024", "Fórmula_1",

    # --- CULTURA Y SOCIEDAD ---
    "Carnaval_de_Oruro", "Diablada", "Morenada", "Caporales",
    "Día_del_Mar", "Guerra_del_Pacífico", "Historia_de_Bolivia",
    "Cholita", "Alasitas", "Gran_Poder_(fiesta)",

    # --- TECNOLOGÍA Y FUTURO (MUY IMPORTANTE) ---
    "Tecnología", "Inteligencia_artificial", "Inteligencia_artificial_generativa",
    "ChatGPT", "OpenAI", "Google", "Microsoft", "Elon_Musk", "Redes_sociales",
    "Criptomoneda", "Bitcoin", "Blockchain", "Ciberseguridad",
    "Exploración_espacial", "NASA", "Starlink",

    # --- CONTEXTO INTERNACIONAL RECIENTE (Últimos 8 años) ---
    "Pandemia_de_COVID-19", "Vacuna_contra_la_COVID-19", "OMS",
    "Cambio_climático", "Calentamiento_global", "Acuerdo_de_París", "Energía_renovable",
    "Guerra_ruso-ucraniana", "Vladimir_Putin", "Volodímir_Zelenski",
    "Javier_Milei", "Nayib_Bukele", "Luiz_Inácio_Lula_da_Silva", "Gabriel_Boric",
    "Donald_Trump", "Joe_Biden", "Estados_Unidos", "China", "Unión_Europea"
]

def obtener_datos_dbpedia():
    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setReturnFormat(JSON)
    
    # Encabezado del archivo Turtle
    contenido_ttl = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""
    print("🚀 Iniciando descarga masiva de DBpedia... Por favor espera.")

    for tema in TEMAS:
        print(f"   📥 Descargando información sobre: {tema}...")
        
        # Consulta: Busca entidades relacionadas con el tema
        # Trae: Título, Resumen (Español o Inglés) y Tipo
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?resource ?label ?abstract WHERE {
            # 1. Busca recursos cuyo tema o nombre contenga la palabra clave
            ?resource rdfs:label ?label .
            ?label bif:contains "'%s'" .
            
            # 2. Obtiene el resumen (abstract)
            ?resource dbo:abstract ?abstract .
            
            # 3. Filtros: Solo recursos de DBpedia, en Español o Inglés
            FILTER(STRSTARTS(STR(?resource), "http://dbpedia.org/resource/"))
            FILTER(LANG(?label) = "es")
            FILTER(LANG(?abstract) = "es" || LANG(?abstract) = "en")
        }
        LIMIT 50 
        """ % (tema) 
        # NOTA: LIMIT 50 significa que descargará 50 artículos por CADA tema. 
        # Si tienes 20 temas, tendrás 1000 noticias.

        try:
            sparql.setQuery(query)
            results = sparql.query().convert()

            for result in results["results"]["bindings"]:
                # Extraer datos
                uri = result["resource"]["value"]
                # Convertimos la URI larga en formato dbr:Nombre
                nombre_recurso = uri.split("/")[-1]
                
                label = result["label"]["value"].replace('"', '\\"')
                abstract = result["abstract"]["value"].replace('"', '\\"')
                lang_abstract = result["abstract"]["xml:lang"]

                # Formatear como Turtle (.ttl)
                tripleta = f"""
dbr:{nombre_recurso}
    a dbo:Thing ;
    rdfs:label "{label}"@es ;
    dbo:abstract "{abstract}"@{lang_abstract} .
"""
                contenido_ttl += tripleta

        except Exception as e:
            print(f"❌ Error descargando {tema}: {e}")

    # Guardar en archivo
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        f.write(contenido_ttl)
    
    print(f"\n✅ ¡Éxito! Se ha creado '{ARCHIVO_SALIDA}' con miles de datos.")
    print("Ahora reinicia tu aplicación Flask para cargar los nuevos datos.")

if __name__ == "__main__":
    obtener_datos_dbpedia()