from helpers import run_app, scraper_crash_log
from scraper import run_scrapper


def main():

    try:
        fecha_desde, fecha_hasta = run_app()
        run_scrapper(fecha_desde, fecha_hasta)

    except KeyboardInterrupt:
        print("\nHa salido de la aplicación.\n")

    except Exception as e:
        scraper_crash_log(e, context="Error fatal del scraper")


if __name__ == "__main__":
    main()
