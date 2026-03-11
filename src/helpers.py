import os
from playwright.sync_api import Page
from config import LOGIN_URL, USERNAME, PASSWORD, FILIAL_URL


def login(page: Page):

    print(USERNAME)
    print(PASSWORD)

    try:
        page.goto(LOGIN_URL)

        page.fill("input[placeholder='Ingresá tu email']", USERNAME)
        page.fill("input[placeholder='Ingresá tu contraseña']", PASSWORD)

        page.click("text=Ingresar")

        wait(page)

        print(
            "Login successful. Logged in as: "
            + USERNAME
            + "\n"
            + "Navigating to filiales..."
        )

    except Exception as e:
        print(f"Login failed. Please check your credentials and try again. Error: {e}")
        raise


def get_filiales(page: Page) -> list[str]:
    try:
        page.click("text=Volver al inicio")
        wait(page)
        page.click("text=Profesionales")
        wait(page)
    except Exception as e:
        print(f"Error navigating to filiales: {e}")
        raise

    try:
        page.wait_for_selector("a.hB-link-button")
        elementos = page.query_selector_all("a.hB-link-button")
        filiales = []
        for el in elementos:
            texto = el.query_selector(".hB-lb-text").inner_text()
            numero = texto.split("·")[0].strip()
            filiales.append(numero)
        print(f"🏢 Filiales encontradas: {filiales}")
        return filiales
    except Exception as e:
        print(f"Couldn't load filiales: {e}")
        raise


def go_to_filial(page: Page, filial_numero: str):
    print(f"Entering filial: {filial_numero}...")
    page.goto(FILIAL_URL.format(filial_numero=filial_numero))
    page.wait_for_selector("text=En otro momento", timeout=60000)
    page.click("text=En otro momento")
    wait(page)
    try:
        close_btn = page.locator("img.mi_close")
        if close_btn.is_visible():
            close_btn.click()
            page.wait_for_selector(
                "#overlayMensajeInicial", state="hidden", timeout=5000
            )
    except Exception:
        pass
    page.click("#linkAnexos")
    wait(page)


def filter_tramites_by_fecha_cierre(page: Page, fecha_desde: str, fecha_hasta: str):
    frame = page.frame(url=lambda u: "anexofacturacion" in u)
    frame.wait_for_selector("#fechaDesde", timeout=60000)
    primer_antes = get_primer_tramite(frame)
    frame.evaluate(
        """
        (params) => {
            const f = document.forms['datos'];
            f.fechaDesde.value = params.desde;
            f.fechaHasta.value = params.hasta;
            f.page.value = 0;
            evalAndSubmit();
        }
        """,
        {"desde": fecha_desde, "hasta": fecha_hasta},
    )

    try:
        frame.wait_for_function(
            f"""() => {{
                const filas = document.querySelectorAll('tbody tr');
                for (const fila of filas) {{
                    const link = fila.querySelector('a');
                    if (link && /^\\d/.test(link.innerText.trim())) {{
                        return link.innerText.trim() !== '{primer_antes}';
                    }}
                }}
                return false;
            }}""",
            timeout=15000,
        )
        print("Filter applied successfully.")
    except Exception:
        print("Failed to apply filter.")


def get_primer_tramite(frame) -> str:
    filas = frame.locator("tbody tr")
    for i in range(filas.count()):
        texto = filas.nth(i).locator("a").first.inner_text().strip()
        if texto[:2].isdigit():
            return texto
    return ""


def get_next_page_button(frame):
    try:
        el = frame.locator("input[value='Siguiente >']").first
        if el.count() == 0:
            return None
        if el.is_visible() and el.is_enabled():
            return el
    except Exception:
        pass
    return None


def download_files_from_filial(page: Page, carpeta: str):
    frame = page.frame(url=lambda u: "anexofacturacion" in u)
    pagina_actual = 1

    while True:
        print(f"\n📄 Procesando página {pagina_actual}...")
        frame.wait_for_selector("tbody tr")

        todas_las_filas = frame.locator("tbody tr")
        total = todas_las_filas.count()

        for i in range(total):
            fila = todas_las_filas.nth(i)
            links = fila.locator("a")

            if links.count() == 0:
                continue

            primer_link_texto = links.first.inner_text().strip()

            if not primer_link_texto[:2].isdigit():
                continue

            numero_tramite = primer_link_texto
            print(f"🔍 Trámite: {numero_tramite}")

            if not numero_tramite.startswith("01-44"):
                print(f"Skipping: {numero_tramite}")
                continue

            print(f"Processing: {numero_tramite}")

            for j in range(links.count()):
                link = links.nth(j)
                texto = link.inner_text().strip()
                if "CSV - Cabecera" in texto or "CSV - Detalle" in texto:
                    print(f"⬇️  Descargando: {texto}")
                    with frame.page.expect_download() as dl:
                        link.click()
                    download = dl.value
                    path = os.path.join(carpeta, download.suggested_filename)
                    download.save_as(path)
                    print(f"Saving at: {path}")

        siguiente = get_next_page_button(frame)
        if siguiente is None:
            print(f"\nLast page: ({pagina_actual}). Filial complete!.")
            break

        primer_tramite_actual = get_primer_tramite(frame)
        print(f"Going to page: {pagina_actual + 1}...")
        siguiente.click()

        try:
            frame.wait_for_function(
                f"""() => {{
                    const filas = document.querySelectorAll('tbody tr');
                    for (const fila of filas) {{
                        const link = fila.querySelector('a');
                        if (link && /^\\d/.test(link.innerText.trim())) {{
                            return link.innerText.trim() !== '{primer_tramite_actual}';
                        }}
                    }}
                    return false;
                }}""",
                timeout=15000,
            )
        except Exception:
            print("Assuming last page reached.")
            break

        pagina_actual += 1


def wait(page):
    page.wait_for_load_state("networkidle", timeout=60000)
