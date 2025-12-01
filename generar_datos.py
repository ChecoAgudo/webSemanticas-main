import random

# CONFIGURACIÓN
ARCHIVO_SALIDA = "dbpedia_local.ttl"
CANTIDAD_NOTICIAS_EXTRA = 1200 # Generaremos más de 1000 para asegurar variedad

# --- DATOS BASE (ENTIDADES REALES) ---
# Estos son los bloques de construcción para las noticias

PERSONAJES = [
    ("Luis_Arce", "Luis Arce", "Presidente de Bolivia"),
    ("Evo_Morales", "Evo Morales", "Ex-mandatario y líder político"),
    ("Carlos_Mesa", "Carlos Mesa", "Político y ex-presidente"),
    ("Manfred_Reyes_Villa", "Manfred Reyes Villa", "Alcalde de Cochabamba"),
    ("Jhonny_Fernandez", "Jhonny Fernández", "Alcalde de Santa Cruz"),
    ("Eva_Copa", "Eva Copa", "Alcaldesa de El Alto"),
    ("Hector_Garibay", "Héctor Garibay", "Atleta fondista olímpico"),
    ("Marcelo_Martins", "Marcelo Martins", "Futbolista histórico"),
    ("Ramiro_Vaca", "Ramiro Vaca", "Futbolista de la selección"),
    ("Javier_Milei", "Javier Milei", "Presidente de Argentina"),
    ("Lula_da_Silva", "Lula da Silva", "Presidente de Brasil"),
    ("Nayib_Bukele", "Nayib Bukele", "Presidente de El Salvador"),
    ("Elon_Musk", "Elon Musk", "CEO de Tesla y SpaceX"),
    ("Sam_Altman", "Sam Altman", "CEO de OpenAI"),
    ("Vladimir_Putin", "Vladimir Putin", "Presidente de Rusia"),
    ("Volodimir_Zelenski", "Volodímir Zelenski", "Presidente de Ucrania")
]

LUGARES = [
    ("Bolivia", "Bolivia"), ("La_Paz", "La Paz"), ("Santa_Cruz_de_la_Sierra", "Santa Cruz"),
    ("Cochabamba", "Cochabamba"), ("Oruro", "Oruro"), ("Potosi", "Potosí"),
    ("Tarija", "Tarija"), ("Beni", "Beni"), ("Pando", "Pando"), ("Chuquisaca", "Chuquisaca"),
    ("Salar_de_Uyuni", "Salar de Uyuni"), ("Lago_Titicaca", "Lago Titicaca"),
    ("El_Alto", "El Alto"), ("Chapare", "Chapare"), ("Chiquitania", "Chiquitania"),
    ("Estados_Unidos", "Estados Unidos"), ("China", "China"), ("Union_Europea", "Unión Europea")
]

TEMAS = [
    ("Economia", "Economía", "Crisis de dólares y exportaciones"),
    ("Litio", "Litio", "Industrialización y extracción directa (EDL)"),
    ("Gas_Natural", "Gas Natural", "Reservas y exportación a Brasil/Argentina"),
    ("Censo_2024", "Censo 2024", "Redistribución de escaños y recursos"),
    ("Judiciales", "Elecciones Judiciales", "Proceso de preselección de magistrados"),
    ("Futbol", "Fútbol", "Liga profesional y eliminatorias"),
    ("Salud", "Salud", "Campañas de vacunación y hospitales"),
    ("Tecnologia", "Tecnología", "IA y digitalización"),
    ("Cambio_Climatico", "Cambio Climático", "Sequías e incendios forestales"),
    ("Mineria", "Minería", "Cooperativas y oro ilegal")
]

EQUIPOS = [
    "Club Bolívar", "The Strongest", "Wilstermann", "Oriente Petrolero", 
    "Blooming", "Always Ready", "Aurora", "Gualberto Villarroel San José"
]

# --- CABECERA DEL ARCHIVO ---
contenido = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ==========================================
#  ENTIDADES PRINCIPALES (DATOS REALES)
# ==========================================
"""

# 1. Generar Entidades Estáticas (Personas y Lugares)
for id_res, nombre, desc in PERSONAJES:
    contenido += f"""
dbr:{id_res}
    a dbo:Person ;
    rdfs:label "{nombre}"@es, "{nombre}"@en ;
    dbo:abstract "{desc}. Figura clave en la actualidad de 2024-2025."@es .
"""

for id_res, nombre in LUGARES:
    contenido += f"""
dbr:{id_res}
    a dbo:Place ;
    rdfs:label "{nombre}"@es ;
    dbo:abstract "{nombre} es un lugar estratégico con gran importancia política y turística."@es .
"""

# ==========================================
#  GENERADOR DE NOTICIAS SINTÉTICAS (MASIVO)
# ==========================================
contenido += "\n# ==========================================\n"
contenido += "#  NOTICIAS GENERADAS (SIMULACIÓN DBPEDIA)\n"
contenido += "# ==========================================\n"

acciones_politica = ["anuncia nuevas medidas", "inaugura obras", "visita", "critica la gestión de", "se reúne con sectores sociales en"]
acciones_economia = ["reporta crecimiento en", "enfrenta crisis por", "firma convenios para", "busca inversiones en"]
acciones_deportes = ["gana partido decisivo en", "clasifica a torneo internacional desde", "presenta nuevos refuerzos en"]

# Generamos 1200 noticias combinando datos aleatoriamente
for i in range(1, CANTIDAD_NOTICIAS_EXTRA + 1):
    categoria = random.choice(["Politica", "Economia", "Deportes", "Tecnologia", "Sociedad"])
    
    # Seleccionar elementos al azar
    persona_id, persona_nom, _ = random.choice(PERSONAJES)
    lugar_id, lugar_nom = random.choice(LUGARES)
    tema_id, tema_nom, tema_desc = random.choice(TEMAS)
    equipo = random.choice(EQUIPOS)
    
    # Construir Título y Resumen según categoría
    if categoria == "Politica":
        accion = random.choice(acciones_politica)
        titulo = f"{persona_nom} {accion} {lugar_nom}"
        abstract = f"El {persona_nom} {accion} {lugar_nom} en el marco del debate sobre {tema_desc}. La noticia ha generado repercusiones."
        recurso = f"Noticia_Politica_{i}_{lugar_id}"
        tipo = "dbo:Event"
        
    elif categoria == "Economia":
        titulo = f"Informe sobre {tema_nom} en {lugar_nom}"
        abstract = f"Nuevos datos sobre {tema_nom} revelan el impacto en {lugar_nom}. {tema_desc}. Analistas sugieren medidas urgentes."
        recurso = f"Noticia_Economia_{i}_{tema_id}"
        tipo = "dbo:Concept"
        
    elif categoria == "Deportes":
        rival = random.choice([e for e in EQUIPOS if e != equipo])
        titulo = f"{equipo} vence a {rival} en {lugar_nom}"
        abstract = f"En un emocionante encuentro en {lugar_nom}, {equipo} logró una victoria clave contra {rival}. La afición celebró el resultado."
        recurso = f"Noticia_Deportes_{i}_{lugar_id}"
        tipo = "dbo:SportsEvent"
        
    elif categoria == "Tecnologia":
        titulo = f"Avance de IA en {lugar_nom}"
        abstract = f"Empresas en {lugar_nom} adoptan herramientas de Inteligencia Artificial como ChatGPT para mejorar la productividad en el sector de {tema_nom}."
        recurso = f"Noticia_Tech_{i}"
        tipo = "dbo:Software"
        
    else: # Sociedad
        titulo = f"Festejos en {lugar_nom} por {tema_nom}"
        abstract = f"La población de {lugar_nom} salió a las calles por {tema_nom}. Se reportan actividades culturales y gran movimiento económico."
        recurso = f"Noticia_Sociedad_{i}"
        tipo = "dbo:Event"

    # Traducir (Simulado) para multilingualidad
    titulo_en = f"News report: {titulo} (Translated)"
    abstract_en = f"{abstract} (English translation regarding {lugar_nom})"
    titulo_pt = f"Notícia: {titulo} (Traduzido)"
    abstract_pt = f"{abstract} (Tradução em português sobre {lugar_nom})"

    # Crear entrada RDF
    entrada = f"""
dbr:{recurso}
    a {tipo} ;
    rdfs:label "{titulo}"@es, "{titulo_en}"@en, "{titulo_pt}"@pt ;
    dbo:abstract "{abstract}"@es, "{abstract_en}"@en, "{abstract_pt}"@pt ;
    dbo:location dbr:{lugar_id} ;
    dbo:related dbr:{persona_id} .
"""
    contenido += entrada

# GUARDAR ARCHIVO
with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    f.write(contenido)

print(f"✅ ¡ÉXITO! Se generó '{ARCHIVO_SALIDA}' con más de {CANTIDAD_NOTICIAS_EXTRA} noticias.")
print("   -> Ahora ejecuta 'python app.py' y prueba tu buscador.")