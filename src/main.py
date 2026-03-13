from helpers import continue_scraping, run_app, scraper_crash_log
from scraper import run_scrapper


def main():

    while True:

        try:
            username, password, fecha_desde, fecha_hasta = run_app()
            run_scrapper(username, password, fecha_desde, fecha_hasta)

            if not continue_scraping():
                print("\nFinalizando aplicación.\n")
                break

        except KeyboardInterrupt:
            print("\nHa salido de la aplicación.\n")
            break

        except Exception as e:
            scraper_crash_log(e, context="Error fatal del scraper")
            break


if __name__ == "__main__":
    main()
