from scraper import run

print("Bienvenido a pyScraper! Iniciando proceso...")
print("Ingrese el rango de fechas para filtrar los trámites por fecha de cierre.")
print("Formato: DD/MM/AAAA")
fecha_desde = input("Fecha desde: ")
fecha_hasta = input("Fecha hasta: ")

run(fecha_desde, fecha_hasta)
