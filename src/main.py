from helpers import isValidDate
from scraper import run

print("\nIngrese el rango de fechas para filtrar los trámites por fecha de cierre.")
print("\nFormato: DD/MM/AAAA\n")
fecha_desde = isValidDate("Fecha desde: ")
fecha_hasta = isValidDate("Fecha hasta: ")
print(f"\n{'='*50}")
print("Iniciando pyScraper...")
print(f"{'='*50}")
print("\nNavegando a login...\n")

run(fecha_desde, fecha_hasta)
