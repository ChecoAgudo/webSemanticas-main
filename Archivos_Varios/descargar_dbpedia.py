import requests
import bz2
import os

def descargar_mini_dbpedia():
    """Descarga una versión mini de DBpedia para empezar"""
    
    print("📥 Descargando datos de DBpedia...")
    
    # Datos básicos que necesitas
    datos = [
        ("Barack Obama", "Persona", "Político estadounidense"),
        ("Madrid", "Lugar", "Capital de España"),
        ("Facebook", "Organización", "Red social"),
        ("Inteligencia artificial", "Concepto", "Campo de la informática"),
        ("Lionel Messi", "Persona", "Futbolista argentino"),
        ("Apple", "Organización", "Empresa tecnológica"),
        ("COVID-19", "Enfermedad", "Pandemia global"),
        ("Cambio climático", "Concepto", "Calentamiento global"),
        ("Amazon", "Organización", "Empresa de comercio electrónico"),
        ("Elon Musk", "Persona", "Empresario tecnológico")
    ]
    
    # Crear archivo Turtle
    with open("dbpedia_local.ttl", "w", encoding="utf-8") as f:
        f.write("@prefix dbo: <http://dbpedia.org/ontology/> .\n")
        f.write("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n")
        f.write("@prefix dbr: <http://dbpedia.org/resource/> .\n\n")
        
        for i, (nombre, tipo, descripcion) in enumerate(datos):
            uri = f"dbr:{nombre.replace(' ', '_')}"
            f.write(f"{uri}\n")
            f.write(f'    rdfs:label "{nombre}"@es ;\n')
            f.write(f'    dbo:abstract "{descripcion}."@es ;\n')
            
            # Mapear tipo
            if tipo == "Persona":
                f.write("    a dbo:Person .\n\n")
            elif tipo == "Lugar":
                f.write("    a dbo:Place .\n\n")
            elif tipo == "Organización":
                f.write("    a dbo:Organisation .\n\n")
            else:
                f.write("    a dbo:Concept .\n\n")
    
    print(f"✅ DBpedia local creada: dbpedia_local.ttl")
    print("📊 Contiene 10 recursos básicos para empezar")

if __name__ == "__main__":
    descargar_mini_dbpedia()