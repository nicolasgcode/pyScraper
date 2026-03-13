from helpers import continue_scraping, get_scraper_config, scraper_crash_log
from scraper import run_scraper


def main():

    while True:

        try:
            username, password, fecha_desde, fecha_hasta = get_scraper_config()
            run_scraper(username, password, fecha_desde, fecha_hasta)

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
