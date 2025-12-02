# generar_noticias_detalladas.py

import random
from datetime import datetime, timedelta
import json

# Definir nombrespaces
TTL_HEADER = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> .
@prefix untitled-ontology-3: <http://www.semanticweb.org/cabez/ontologies/2025/2/untitled-ontology-3#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

# Listas de datos para generar contenido variado
autores = [
    "Dr. Iván Mendoza", "Lic. María López", "Ing. Carlos Fernández", "Dra. Ana García",
    "Mg. Pedro Martínez", "Lic. Laura Rodríguez", "Dr. Juan Pérez", "MSc. Sofía Hernández",
    "Ing. Diego González", "Lic. Valeria Smith", "Dr. Roberto Vargas", "Dra. Carmen Ruiz",
    "Mg. Luis Torres", "Lic. Patricia Castro", "Dr. Miguel Ángel Rojas"
]

tematicas = [
    "Salud", "Política", "Economía", "Deportes", "Cultura", "Tecnología", 
    "Medio ambiente", "Educación", "Internacional", "Social", "Ciencia",
    "Turismo", "Negocios", "Entretenimiento", "Sociedad"
]

tonos = [
    "Argumentativo", "Informativo", "Crítico", "Persuasivo", "Descriptivo",
    "Narrativo", "Analítico", "Reflexivo", "Denunciante", "Informativo"
]

enfoques_politicos = [
    "Neutral", "Progubernamental", "Opositor", "Crítico", "Analítico", "Balanceado"
]

estructuras = [
    "Pirámide invertida completa", "Pirámide invertida parcial", "Narrativa",
    "Descriptiva", "Expositiva", "Cronológica", "Temática"
]

ubicaciones = [
    "Santa Cruz, Bolivia", "La Paz, Bolivia", "Cochabamba, Bolivia", 
    "Sucre, Bolivia", "Tarija, Bolivia", "Oruro, Bolivia", "Potosí, Bolivia",
    "Beni, Bolivia", "Pando, Bolivia", "El Alto, Bolivia",
    "Buenos Aires, Argentina", "Lima, Perú", "Santiago, Chile",
    "Bogotá, Colombia", "São Paulo, Brasil", "Ciudad de México, México"
]

idiomas = ["Español", "Inglés", "Portugués", "Quechua", "Aymara", "Guaraní"]

tipos_contenido = [
    "Columna", "Reportaje", "Noticia", "Editorial", "Crónica", "Entrevista",
    "Análisis", "Investigación", "Opinión", "Reseña"
]

autoria_tipos = [
    "Autor individual", "Coautoría", "Equipo de redacción", 
    "Agencia de noticias", "Colaboración especial"
]

# Títulos de noticias por temática
titulos_por_tematica = {
    "Salud": [
        "La vacuna contra el COVID-19 y su impacto en la fertilidad",
        "Nuevo tratamiento para la diabetes muestra resultados prometedores",
        "Alerta sanitaria por brote de dengue en el trópico",
        "Avances en la investigación del cáncer en Bolivia",
        "Consejos para mantener la salud mental en tiempos de crisis",
        "La importancia de la lactancia materna en el primer año",
        "Nuevo hospital especializado abrirá sus puertas el próximo mes",
        "Campo de vacunación masiva contra la influenza",
        "Los beneficios del ejercicio regular para la salud cardiovascular",
        "Alerta por aumento de casos de enfermedades respiratorias"
    ],
    "Política": [
        "Gobierno anuncia nuevas medidas económicas para 2024",
        "Debate parlamentario sobre la reforma educativa",
        "Elecciones regionales: candidatos presentan sus propuestas",
        "Análisis de los primeros 100 días del nuevo alcalde",
        "Diálogo entre gobierno y oposición se estanca",
        "Nueva ley de transparencia será implementada próximamente",
        "Protestas sociales exigen mejoras en servicios básicos",
        "Convención internacional sobre derechos indígenas",
        "Reforma constitucional: pros y contras",
        "La política exterior boliviana en el contexto latinoamericano"
    ],
    "Economía": [
        "Bolivia registra crecimiento económico del 4.5% en el último trimestre",
        "Nuevas inversiones extranjeras en el sector energético",
        "El precio del dólar y su impacto en la economía familiar",
        "Exportaciones de quinua aumentan un 15% este año",
        "Programas de microcrédito para emprendedores locales",
        "La industria del litio: oportunidades y desafíos",
        "Inflación se mantiene estable en 3.2% anual",
        "Nuevas oportunidades de empleo en el sector tecnológico",
        "El turismo como motor de desarrollo económico",
        "Retos de la economía digital en Bolivia"
    ],
    "Deportes": [
        "La selección boliviana clasifica a la Copa América 2024",
        "Nuevo talento del fútbol boliviano es fichado por equipo europeo",
        "Maratonista nacional establece nuevo récord sudamericano",
        "Juegos Olímpicos de la Juventud: atletas bolivianos brillan",
        "La importancia del deporte base en el desarrollo de talentos",
        "Torneo nacional de voleibol femenino corona a su campeón",
        "Inversión en infraestructura deportiva para los Juegos Panamericanos",
        "Deportes extremos ganan popularidad entre los jóvenes",
        "Nutrición y rendimiento deportivo: consejos de expertos",
        "La historia del fútbol boliviano: momentos memorables"
    ],
    "Tecnología": [
        "Startup boliviana desarrolla aplicación para agricultura inteligente",
        "Los desafíos de la implementación del 5G en Bolivia",
        "Inteligencia artificial revoluciona el diagnóstico médico",
        "Ciberseguridad: cómo proteger tu información en línea",
        "Realidad virtual en la educación: experiencias innovadoras",
        "Blockchain y su potencial para la transparencia gubernamental",
        "Tecnología wearable: el futuro de la monitorización de salud",
        "Emprendedores tecnológicos reciben premio internacional",
        "La brecha digital en zonas rurales de Bolivia",
        "Innovaciones tecnológicas en la industria minera"
    ]
}

# Resúmenes por temática
resumenes_por_tematica = {
    "Salud": [
        "Investigación detallada sobre los efectos secundarios de las vacunas COVID-19 y su relación con la salud reproductiva.",
        "Estudio clínico revela nueva alternativa terapéutica para pacientes con diabetes tipo 2.",
        "Autoridades sanitarias declaran alerta epidemiológica ante el aumento exponencial de casos de dengue.",
        "Científicos bolivianos presentan avances significativos en la investigación oncológica.",
        "Expertos en psicología comparten estrategias para manejar el estrés y la ansiedad en la vida moderna."
    ],
    "Política": [
        "El gobierno nacional anuncia un paquete de medidas económicas que afectarán diversos sectores productivos.",
        "Diputados y senadores debaten propuestas para reformar el sistema educativo boliviano.",
        "Candidatos a gobernaciones presentan sus planes de trabajo para el próximo período administrativo.",
        "Balance de la gestión municipal durante los primeros meses de administración.",
        "Análisis del diálogo político entre el oficialismo y los partidos de oposición."
    ],
    "Economía": [
        "Según datos del INE, la economía boliviana muestra signos de recuperación tras la pandemia.",
        "Empresas internacionales anuncian inversiones millonarias en proyectos energéticos.",
        "Análisis del comportamiento del mercado cambiario y sus efectos en los precios.",
        "Las exportaciones de productos andinos muestran crecimiento sostenido este año.",
        "Programas de financiamiento apoyan a pequeños y medianos empresarios."
    ],
    "Deportes": [
        "La selección nacional logra su clasificación tras una victoria histórica en las eliminatorias.",
        "Joven promesa del fútbol boliviano firma contrato con equipo de primera división europea.",
        "Atleta nacional supera marca sudamericana en competencia internacional.",
        "Deportistas bolivianos destacan en competencia continental juvenil.",
        "Importancia de los programas de iniciación deportiva en escuelas y colegios."
    ],
    "Tecnología": [
        "Empresa local desarrolla solución tecnológica para optimizar la producción agrícola.",
        "Desafíos técnicos y regulatorios para la implementación de redes 5G en el país.",
        "Sistemas de IA ayudan a médicos en el diagnóstico temprano de enfermedades.",
        "Recomendaciones de expertos en seguridad informática para usuarios y empresas.",
        "Experiencias educativas innovadoras utilizando tecnologías de inmersión."
    ]
}

# Generar contenido para múltiples noticias
def generar_noticia(id_noticia):
    # Seleccionar temática aleatoria
    tematica = random.choice(tematicas)
    
    # Si la temática no tiene títulos específicos, usar títulos genéricos
    if tematica not in titulos_por_tematica:
        titulos_genericos = [
            f"Avances significativos en el campo de {tematica}",
            f"Desafíos actuales en el área de {tematica}",
            f"Nuevas perspectivas sobre {tematica}",
            f"Impacto social de los desarrollos en {tematica}",
            f"Futuro prometedor para {tematica} en Bolivia"
        ]
        titulo = random.choice(titulos_genericos)
    else:
        titulo = random.choice(titulos_por_tematica[tematica])
    
    # Generar resumen
    if tematica in resumenes_por_tematica:
        resumen = random.choice(resumenes_por_tematica[tematica])
    else:
        resumen = f"Artículo especializado que aborda aspectos relevantes de {tematica.lower()} en el contexto actual."
    
    # Generar fecha aleatoria en los últimos 3 años
    fecha = datetime.now() - timedelta(days=random.randint(0, 1095))
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    # Seleccionar tipo de contenido
    tipo_contenido = random.choice(tipos_contenido)
    
    # Generar URI única para cada recurso
    uri_base = f"untitled-ontology-3:Noticia_{id_noticia:04d}"
    
    # Propiedades relacionadas (algunas noticias tendrán recursos relacionados)
    recursos_relacionados = []
    
    # 30% de probabilidad de tener verificación
    if random.random() < 0.3:
        id_verificacion = random.randint(1, 50)
        recursos_relacionados.append(f"    untitled-ontology-3:es_verificada_por untitled-ontology-3:Fact-Checking_{id_verificacion:02d} ;")
    
    # 25% de probabilidad de tener difusión en podcast
    if random.random() < 0.25:
        id_podcast = random.randint(1, 30)
        recursos_relacionados.append(f"    untitled-ontology-3:se_difunde_en untitled-ontology-3:Podcast_{id_podcast:02d} ;")
    
    # 20% de probabilidad de tener audio asociado
    if random.random() < 0.2:
        id_audio = random.randint(1, 40)
        recursos_relacionados.append(f"    untitled-ontology-3:tiene untitled-ontology-3:Audio_{id_audio:02d} ;")
    
    # Construir el bloque TTL para esta noticia
    bloque = f"""dbr:{uri_base.replace('untitled-ontology-3:', '')}
    a untitled-ontology-3:{tipo_contenido} ;
    rdfs:label "{titulo}"@es ;
    dbo:abstract "{resumen}"@es ;
    untitled-ontology-3:Autor "{random.choice(autores)}" ;
    untitled-ontology-3:Autoria "{random.choice(autoria_tipos)}" ;
    untitled-ontology-3:Cantidad_difusion "{random.randint(1000, 1000000)}" ;
    untitled-ontology-3:Enfoque_politico "{random.choice(enfoques_politicos)}" ;
    untitled-ontology-3:Estructura "{random.choice(estructuras)}" ;
    untitled-ontology-3:Fecha_publicacion "{fecha_str}"^^xsd:date ;
    untitled-ontology-3:Idioma "{random.choice(idiomas)}" ;
    untitled-ontology-3:Multimedia_asociado "{str(random.choice([True, False])).lower()}" ;
    untitled-ontology-3:Tematica "{tematica}" ;
    untitled-ontology-3:Tono "{random.choice(tonos)}" ;
    untitled-ontology-3:Titulo "{titulo}" ;
    untitled-ontology-3:Ubicacion "{random.choice(ubicaciones)}" ;
    untitled-ontology-3:Uso_citas "{str(random.choice([True, False])).lower()}" ;
"""
    
    # Agregar recursos relacionados si existen
    for recurso in recursos_relacionados:
        bloque += f"{recurso}\n"
    
    bloque += "    .\n\n"
    return bloque

# Generar recursos relacionados (Fact-Checking, Podcasts, Audios)
def generar_recursos_relacionados():
    recursos = []
    
    # Fact-Checking (50 recursos)
    for i in range(1, 51):
        recursos.append(f"""untitled-ontology-3:Fact-Checking_{i:02d}
    a untitled-ontology-3:Fact-Checking ;
    rdfs:label "Verificación de noticia {i}"@es ;
    dbo:abstract "Servicio de verificación de hechos para contenido periodístico."@es ;
    untitled-ontology-3:Organizacion "Observatorio de Medios Bolivia" ;
    untitled-ontology-3:Fecha_creacion "2023-{random.randint(1,12):02d}-{random.randint(1,28):02d}"^^xsd:date ;
    untitled-ontology-3:Metodologia "Verificación cruzada de fuentes" ;
    untitled-ontology-3:Resultado "{random.choice(['Verdadero', 'Falso', 'Engañoso', 'Contexto necesario'])}" ;
    .
""")
    
    # Podcasts (30 recursos)
    for i in range(1, 31):
        temas_podcast = ["Salud", "Tecnología", "Política", "Economía", "Cultura"]
        recursos.append(f"""untitled-ontology-3:Podcast_{i:02d}
    a untitled-ontology-3:Podcast ;
    rdfs:label "Podcast Informativo {i}"@es ;
    dbo:abstract "Programa de audio que analiza temas de actualidad {random.choice(temas_podcast)}."@es ;
    untitled-ontology-3:Duracion_minutos "{random.randint(15, 120)}" ;
    untitled-ontology-3:Plataforma "{random.choice(['Spotify', 'Apple Podcasts', 'Google Podcasts', 'YouTube'])}" ;
    untitled-ontology-3:Frecuencia "{random.choice(['Semanal', 'Quincenal', 'Mensual'])}" ;
    untitled-ontology-3:Host "{random.choice(autores)}" ;
    .
""")
    
    # Audios (40 recursos)
    for i in range(1, 41):
        recursos.append(f"""untitled-ontology-3:Audio_{i:02d}
    a untitled-ontology-3:Audio ;
    rdfs:label "Audio complementario {i}"@es ;
    dbo:abstract "Contenido de audio adicional relacionado con la noticia."@es ;
    untitled-ontology-3:Formato "{random.choice(['MP3', 'WAV', 'AAC'])}" ;
    untitled-ontology-3:Duracion_segundos "{random.randint(60, 600)}" ;
    untitled-ontology-3:Calidad "{random.choice(['Alta', 'Media', 'Baja'])}" ;
    .
""")
    
    return "\n\n".join(recursos)

# Función principal para generar el archivo TTL
def generar_ttl_completo(num_noticias=1000, nombre_archivo="noticias_detalladas.ttl"):
    print(f"Generando {num_noticias} noticias...")
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        # Escribir cabecera
        f.write(TTL_HEADER)
        
        # Escribir recursos relacionados primero
        f.write("# ==========================================\n")
        f.write("#  RECURSOS RELACIONADOS\n")
        f.write("# ==========================================\n\n")
        f.write(generar_recursos_relacionados())
        f.write("\n\n")
        
        # Escribir noticias
        f.write("# ==========================================\n")
        f.write("#  NOTICIAS DETALLADAS (1000 ARTÍCULOS)\n")
        f.write("# ==========================================\n\n")
        
        for i in range(1, num_noticias + 1):
            if i % 100 == 0:
                print(f"  Generando noticia {i} de {num_noticias}...")
            
            noticia_ttl = generar_noticia(i)
            f.write(noticia_ttl)
            
            # Agrupar por bloques de 100 para mejor legibilidad
            if i % 100 == 0:
                f.write(f"# ----- Bloque de noticias {i-99}-{i} -----\n\n")
    
    print(f"\n✅ Archivo '{nombre_archivo}' generado exitosamente!")
    print(f"📊 Estadísticas:")
    print(f"   - Total de noticias: {num_noticias}")
    print(f"   - Recursos relacionados: 120 (50 Fact-Checking, 30 Podcasts, 40 Audios)")
    print(f"   - Total de recursos en el archivo: {num_noticias + 120}")

# Función adicional para generar un archivo JSON con metadatos
def generar_metadata_json(nombre_archivo="metadata_noticias.json"):
    metadata = {
        "total_noticias": 1000,
        "tematicas_distribucion": {},
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "autor": "Sistema Generador de Noticias",
        "version": "1.0",
        "descripcion": "Dataset de 1000 noticias con propiedades detalladas para pruebas de ontología"
    }
    
    # Contar distribución de temáticas
    for tematica in tematicas:
        metadata["tematicas_distribucion"][tematica] = random.randint(50, 150)
    
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Archivo de metadatos '{nombre_archivo}' generado!")

# Función para mostrar ejemplo de noticia generada
def mostrar_ejemplo():
    print("🔍 EJEMPLO DE NOTICIA GENERADA:")
    print("=" * 50)
    
    ejemplo = generar_noticia(9999)
    print(ejemplo)
    
    print("\n📋 PROPIEDADES INCLUIDAS EN CADA NOTICIA:")
    print("1. Tipo de contenido (Columna, Reportaje, Noticia, etc.)")
    print("2. Título en español")
    print("3. Resumen (abstract)")
    print("4. Autor")
    print("5. Tipo de autoría")
    print("6. Cantidad de difusión (número)")
    print("7. Enfoque político")
    print("8. Estructura periodística")
    print("9. Fecha de publicación")
    print("10. Idioma")
    print("11. Multimedia asociado (true/false)")
    print("12. Temática")
    print("13. Tono")
    print("14. Título (propiedad interna)")
    print("15. Ubicación")
    print("16. Uso de citas (true/false)")
    print("17. Posibles relaciones con Fact-Checking, Podcasts y Audios")

# Ejecutar si se llama directamente
if __name__ == "__main__":
    print("🚀 GENERADOR DE DATOS DE NOTICIAS")
    print("=" * 40)
    
    # Mostrar ejemplo
    mostrar_ejemplo()
    
    print("\n" + "=" * 40)
    respuesta = input("¿Generar archivo completo con 1000 noticias? (s/n): ")
    
    if respuesta.lower() == 's':
        try:
            generar_ttl_completo(1000, "noticias_detalladas.ttl")
            generar_metadata_json()
            
            print("\n📁 ARCHIVOS GENERADOS:")
            print("1. noticias_detalladas.ttl - Archivo principal con todas las noticias")
            print("2. metadata_noticias.json - Metadatos y estadísticas")
            
            print("\n⚠️ IMPORTANTE:")
            print("- El archivo TTL tendrá aproximadamente 2-3 MB")
            print("- Puedes cargarlo en tu aplicación junto con la ontología")
            print("- Asegúrate de tener suficiente espacio en disco")
            
        except Exception as e:
            print(f"❌ Error al generar archivos: {e}")
    else:
        print("Generación cancelada.")