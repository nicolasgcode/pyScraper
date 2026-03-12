from helpers import launch_scraper, launch_scraper, scraper_crash_log
from scraper import run

fecha_desde, fecha_hasta = launch_scraper()

try:
    run(fecha_desde, fecha_hasta)
except Exception as e:
    scraper_crash_log(e, context="Error fatal del scraper")
