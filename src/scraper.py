from playwright.sync_api import sync_playwright


from helpers import (
    download_files_from_filial,
    filter_tramites_by_fecha_cierre,
    get_filiales,
    go_to_filial,
    login,
    scraper_crash_log,
    skipped_files_log,
)


def run_scrapper(fecha_desde, fecha_hasta):

    skipped_files = []

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            login(page)

            filiales = get_filiales(page)

            for idx, filial in enumerate(filiales):
                print(f"\n{'='*50}")
                print(f"[{idx+1}/{len(filiales)}] Procesando filial: {filial}")
                print(f"{'='*50}")

                try:
                    go_to_filial(page, filial)

                    filter_tramites_by_fecha_cierre(page, fecha_desde, fecha_hasta)

                    has_downloads = download_files_from_filial(
                        page, filial, skipped_files, fecha_desde, fecha_hasta
                    )

                    if not has_downloads:
                        print(f"\nNo se encontraron anexos para la filial {filial}")

                except Exception as e:
                    print(f"\nError procesando filial {filial}: {e}")
                    scraper_crash_log(e, context=f"Error procesando filial {filial}")
                    skipped_files.append(f"{filial} - ERROR: {e}")
                    continue

            browser.close()

    except Exception as e:

        scraper_crash_log(e)

    finally:

        skipped_files_log(skipped_files)

        print(f"\nProceso completado. Filiales procesadas: {len(filiales)}")
