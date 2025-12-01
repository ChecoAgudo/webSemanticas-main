import random

# CONFIGURACIÓN
ARCHIVO_SALIDA = "dbpedia_local.ttl"
CANTIDAD_NOTICIAS = 1000 # Un número seguro para la cantidad de datos que tenemos

# --- 1. DATOS MAESTROS AMPLIADOS ---

PERSONAJES = [
    ("Luis_Arce", "Luis Arce", "Presidente de Bolivia, enfocado en la industrialización."),
    ("Evo_Morales", "Evo Morales", "Líder político del MAS-IPSP."),
    ("Carlos_Mesa", "Carlos Mesa", "Expresidente y líder de Comunidad Ciudadana."),
    ("Luis_Fernando_Camacho", "Luis Fernando Camacho", "Gobernador de Santa Cruz."),
    ("Manfred_Reyes_Villa", "Manfred Reyes Villa", "Alcalde de Cochabamba."),
    ("Eva_Copa", "Eva Copa", "Alcaldesa de la ciudad de El Alto."),
    ("Hector_Garibay", "Héctor Garibay", "Atleta olímpico boliviano."),
    ("Marcelo_Martins", "Marcelo Martins", "Goleador histórico de la selección."),
    ("Javier_Milei", "Javier Milei", "Presidente de Argentina."),
    ("Lula_da_Silva", "Lula da Silva", "Presidente de Brasil."),
    ("Xi_Jinping", "Xi Jinping", "Presidente de China."),
    ("Joe_Biden", "Joe Biden", "Presidente de Estados Unidos."),
    ("Elon_Musk", "Elon Musk", "Dueño de Tesla y SpaceX."),
    ("Mark_Zuckerberg", "Mark Zuckerberg", "CEO de Meta.")
]

LUGARES = [
    ("Beni", "Beni", "Departamento ganadero de la Amazonía boliviana. Su capital Trinidad enfrenta retos por inundaciones y sequías, pero destaca por su biodiversidad."),
    ("Pando", "Pando", "La perla del Acre, zona estratégica de la castaña y frontera con Brasil."),
    ("La_Paz", "La Paz", "Sede de gobierno, famosa por el Illimani y su red de teleféricos."),
    ("Santa_Cruz_de_la_Sierra", "Santa Cruz", "Centro económico y agroindustrial de Bolivia."),
    ("Cochabamba", "Cochabamba", "Capital gastronómica y corazón de Bolivia."),
    ("Oruro", "Oruro", "Capital del folclore y la minería."),
    ("Potosi", "Potosí", "Cuna del litio y patrimonio histórico."),
    ("Tarija", "Tarija", "Tierra del vino y el gas natural."),
    ("Sucre", "Sucre", "Capital constitucional y ciudad blanca."),
    ("El_Alto", "El Alto", "Ciudad industrial y joven, motor de la economía informal."),
    ("Salar_de_Uyuni", "Salar de Uyuni", "El mayor desierto de sal del mundo."),
    ("Lago_Titicaca", "Lago Titicaca", "El lago navegable más alto del mundo."),
    ("Chapare", "Chapare", "Zona tropical de Cochabamba."),
    ("Chiquitania", "Chiquitania", "Región de misiones jesuíticas y biodiversidad.")
]

TEMAS = [
    ("Economia", "Economía", "escasez de dólares", "El Banco Central aplica medidas no convencionales."),
    ("Litio", "Litio", "extracción directa", "Empresas extranjeras firman nuevos convenios."),
    ("Gas", "Gas Natural", "baja en la producción", "Se buscan nuevos pozos exploratorios."),
    ("Salud", "Salud", "brote de dengue", "Hospitales colapsan ante la demanda de pacientes."),
    ("Educacion", "Educación", "nuevos ítems", "El magisterio se moviliza por mayor presupuesto."),
    ("Tecnologia", "Tecnología", "IA en empresas", "Startups locales reciben financiamiento."),
    ("Transporte", "Transporte", "bloqueo de carreteras", "Pérdidas millonarias por conflictos sociales."),
    ("Clima", "Cambio Climático", "sequía extrema", "Municipios se declaran en zona de desastre."),
    ("Seguridad", "Seguridad", "lucha contra el narcotráfico", "Operativos en frontera arrojan resultados.")
]

EQUIPOS = ["Bolívar", "The Strongest", "Wilstermann", "Oriente Petrolero", "Blooming", "Aurora", "Real Tomayapo", "Always Ready", "San José", "Universitario"]

# --- 2. CABECERA ---
contenido = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbr: <http://dbpedia.org/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""

# Generar estáticos
for id_res, nombre, desc in PERSONAJES:
    contenido += f"""dbr:{id_res} a dbo:Person ; rdfs:label "{nombre}"@es ; dbo:abstract "{desc}"@es .\n"""
for id_res, nombre, desc in LUGARES:
    contenido += f"""dbr:{id_res} a dbo:Place ; rdfs:label "{nombre}"@es ; dbo:abstract "{desc}"@es .\n"""

# --- 3. GENERADOR ROBUSTO ---
print("🚀 Generando noticias...")

titulos_usados = set()
intentos_fallidos = 0
contador = 0

# Bucle con seguridad: Si falla 500 veces seguidas, se detiene para no colgarse
while contador < CANTIDAD_NOTICIAS and intentos_fallidos < 500:
    
    categoria = random.choice(["Politica", "Economia", "Deportes", "Sociedad", "Tecno", "Cultura"])
    
    per_id, per_nom, _ = random.choice(PERSONAJES)
    lug_id, lug_nom, _ = random.choice(LUGARES)
    tema_id, tema_nom, tema_corto, tema_largo = random.choice(TEMAS)
    equipo = random.choice(EQUIPOS)
    
    titulo = ""
    abstract = ""
    tipo = "dbo:Thing"

    # Plantillas variadas para evitar duplicados
    if categoria == "Politica":
        plantilla = random.choice([
            (f"{per_nom} visita {lug_nom}", f"Durante su visita a {lug_nom}, {per_nom} habló sobre {tema_corto}."),
            (f"{per_nom} critica situación en {lug_nom}", f"El mandatario {per_nom} se refirió a la crisis de {tema_corto} en {lug_nom}."),
            (f"Acuerdo en {lug_nom} liderado por {per_nom}", f"{per_nom} firmó un acuerdo histórico en {lug_nom}. {tema_largo}."),
            (f"Protestas contra {per_nom} en {lug_nom}", f"Sectores sociales de {lug_nom} rechazaron las medidas de {per_nom} sobre {tema_corto}.")
        ])
        tipo = "dbo:Event"
    elif categoria == "Economia":
        plantilla = random.choice([
            (f"Crisis de {tema_nom} afecta a {lug_nom}", f"La {tema_corto} golpea la economía de {lug_nom}. {tema_largo}."),
            (f"Inversión millonaria en {lug_nom}", f"Se anuncia una gran inversión en {tema_nom} para beneficiar a {lug_nom}."),
            (f"Reporte sobre {tema_nom} en {lug_nom}", f"Nuevas cifras de {tema_nom} muestran una recuperación en {lug_nom}.")
        ])
        tipo = "dbo:Concept"
    elif categoria == "Deportes":
        rival = random.choice([e for e in EQUIPOS if e != equipo])
        plantilla = random.choice([
            (f"{equipo} gana a {rival} en {lug_nom}", f"Gran partido en {lug_nom} donde {equipo} se impuso ante {rival}."),
            (f"Empate entre {equipo} y {rival}", f"El clásico disputado en {lug_nom} terminó sin goles."),
            (f"{equipo} estrena técnico en {lug_nom}", f"La llegada del nuevo DT de {equipo} genera expectativas en {lug_nom}.")
        ])
        tipo = "dbo:SportsEvent"
    else:
        plantilla = random.choice([
            (f"Feria de {tema_nom} en {lug_nom}", f"{lug_nom} inaugura su feria internacional de {tema_nom}."),
            (f"Alerta ambiental en {lug_nom}", f"Preocupación en {lug_nom} por {tema_corto}. Autoridades toman medidas."),
            (f"Avances en {tema_nom} desde {lug_nom}", f"Expertos de {lug_nom} presentan soluciones para {tema_corto}.")
        ])
        tipo = "dbo:Event"

    titulo = plantilla[0]
    abstract = plantilla[1]

    # VALIDACIÓN
    if titulo in titulos_usados:
        intentos_fallidos += 1
        continue
    
    # Si es único, reseteamos intentos y guardamos
    intentos_fallidos = 0
    titulos_usados.add(titulo)
    contador += 1
    
    # Multilingualidad automática (Simulada)
    entrada = f"""
dbr:News_{contador}_{lug_id}
    a {tipo} ;
    rdfs:label "{titulo}"@es, "News: {titulo}"@en, "Notícia: {titulo}"@pt ;
    dbo:abstract "{abstract}"@es, "{abstract} (English translation)"@en, "{abstract} (Tradução)"@pt ;
    dbo:location dbr:{lug_id} .
"""
    contenido += entrada

with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
    f.write(contenido)

print(f"✅ ¡ÉXITO! Se generaron {contador} noticias.")
if intentos_fallidos >= 500:
    print("⚠️ El generador se detuvo preventivamente para evitar bloqueo (se agotaron las combinaciones).")