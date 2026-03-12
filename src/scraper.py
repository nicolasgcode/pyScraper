from playwright.sync_api import sync_playwright


from helpers import (
    download_files_from_filial,
    filter_tramites_by_fecha_cierre,
    get_filiales,
    go_to_filial,
    login,
    wait,
)


def run(fecha_desde, fecha_hasta):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)

        filiales = get_filiales(page)

        for idx, filial in enumerate(filiales):
            print(f"\n{'='*50}")
            print(f"[{idx+1}/{len(filiales)}] Procesando filial: {filial}")
            print(f"{'='*50}")

            go_to_filial(page, filial)

            filter_tramites_by_fecha_cierre(page, fecha_desde, fecha_hasta)
            wait(page)

            has_downloads = download_files_from_filial(page, filial)

            if not has_downloads:
                print(
                    f"\nNo se encontraron anexos para la filial {filial} en el rango de fechas especificado."
                )

        print(f"\nProceso completado! {len(filiales)} filiales procesadas.")
        browser.close()
