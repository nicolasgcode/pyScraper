from playwright.sync_api import sync_playwright

import os

from helpers import (
    download_files_from_filial,
    filter_tramites_by_fecha_cierre,
    get_filiales,
    go_to_filial,
    login,
    wait,
)

from config import BASE_PATH


def run(fecha_desde, fecha_hasta):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        login(page)

        filiales = get_filiales(page)
        print(f"\n🔍 Total filiales: {len(filiales)} → {filiales}")

        for idx, filial in enumerate(filiales):
            print(f"\n{'='*50}")
            print(f"🏢 [{idx+1}/{len(filiales)}] Processing filial: {filial}")
            print(f"{'='*50}")

            carpeta = f"{BASE_PATH}/{filial}"

            os.makedirs(carpeta, exist_ok=True)

            go_to_filial(page, filial)

            filter_tramites_by_fecha_cierre(page, fecha_desde, fecha_hasta)
            wait(page)

            download_files_from_filial(page, carpeta)

        print(f"\n Process complete! {len(filiales)} filiales processed.")
        browser.close()
