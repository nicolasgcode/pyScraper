from datetime import datetime
import os
from playwright.sync_api import Page
from config import BASE_PATH, LOGIN_URL, USERNAME, PASSWORD, FILIAL_URL


def login(page: Page):

    try:
        page.goto(LOGIN_URL)

        page.fill("input[placeholder='Ingresá tu email']", USERNAME)
        page.fill("input[placeholder='Ingresá tu contraseña']", PASSWORD)

        page.click("text=Ingresar")

        wait(page)
        print("\nLogin exitoso!\n")
        print(f"{'='*50}")
        print("Logueado como: " + USERNAME)
        print(f"{'='*50}")
        print("\nNavegando a sección de filiales...\n")

    except Exception as e:
        print(
            f"Login fallido. Por favor, checkea tus credenciales e intentalo de nuevo. Error: {e}"
        )
        raise


def get_filiales(page: Page) -> list[str]:
    try:
        page.click("text=Volver al inicio")
        wait(page)
        page.click("text=Profesionales")
        wait(page)
    except Exception as e:
        print(f"Error navegando a filiales: {e}")
        raise

    try:
        page.wait_for_selector("a.hB-link-button")
        elementos = page.query_selector_all("a.hB-link-button")
        filiales = []
        for el in elementos:
            texto = el.query_selector(".hB-lb-text").inner_text()
            numero = texto.split("·")[0].strip()
            filiales.append(numero)
        print(f'Filiales encontradas: {len(filiales)} -> "{filiales}"')
        return filiales
    except Exception as e:
        print(f"No se pudieron cargar las filiales: {e}")
        raise


def go_to_filial(page: Page, filial_numero: str):
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
            f"""(prev) => {{
                const alert = document.querySelector("h4.alert-heading");
                if (alert) return true;

                const filas = document.querySelectorAll("tbody tr");
                for (const fila of filas) {{
                    const link = fila.querySelector("a");
                    if (link && /^\\d/.test(link.innerText.trim())) {{
                        return link.innerText.trim() !== prev;
                    }}
                }}
                return false;
            }}""",
            arg=primer_antes,
            timeout=15000,
        )
        print("\nFiltro por fechas aplicado correctamente.")
        print("\nBuscando archivos para descargar...")
    except Exception as e:
        print(f"\nError al aplicar filtro de fechas: {e}")
        raise


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


def download_files_from_filial(page: Page, filial: str) -> bool:
    frame = page.frame(url=lambda u: "anexofacturacion" in u)
    current_page = 1
    downloaded_files = False

    while True:

        frame.wait_for_selector("tbody tr, h4.alert-heading", timeout=10000)

        if (frame.locator("h4.alert-heading")).count() > 0:
            return False

        all_rows = frame.locator("tbody tr")
        total = all_rows.count()

        if total == 0:
            return False

        carpeta = f"{BASE_PATH}/{filial}"

        for i in range(total):
            fila = all_rows.nth(i)
            links = fila.locator("a")

            if links.count() == 0:
                continue

            primer_link_texto = links.first.inner_text().strip()

            if not primer_link_texto[:2].isdigit():
                continue

            numero_tramite = primer_link_texto

            if not numero_tramite.startswith("01-44"):
                print(f"\nSalteando trámite: {numero_tramite}")
                continue

            for j in range(links.count()):
                link = links.nth(j)
                texto = link.inner_text().strip()
                if "CSV - Cabecera" in texto or "CSV - Detalle" in texto:

                    os.makedirs(carpeta, exist_ok=True)

                    print(f"\nProcesando trámite: {numero_tramite}\n")

                    print(f"Descargando: {texto}")
                    with frame.page.expect_download(timeout=20000) as dl:
                        link.click()
                    download = dl.value
                    path = os.path.join(carpeta, download.suggested_filename)
                    download.save_as(path)
                    print(f"\nGuardando en: {path}")
                    downloaded_files = True

        siguiente = get_next_page_button(frame)
        if siguiente is None:
            print(f"\nPágina final: ({current_page}). Filial recorrida con éxito!.")
            break

        primer_tramite_actual = get_primer_tramite(frame)
        print(f"\n{'-'*50}")
        print(f"Accediendo a página: {current_page + 1}...")
        print(f"{'-'*50}")
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
            print("Asumiendo que se llegó a la última página.")
            break

        current_page += 1

    return downloaded_files


def wait(page):
    page.wait_for_load_state("networkidle", timeout=60000)


def isValidDate(prompt="Fecha (DD/MM/YYYY): "):
    while True:
        date_str = input(prompt)

        try:
            fecha = datetime.strptime(date_str, "%d/%m/%Y")
            hoy = datetime.now()

            if fecha > hoy:
                print(
                    "\nNo se pueden ingresar fechas futuras. Por favor, intentelo nuevamente."
                )
                continue

            return date_str

        except ValueError:
            print(f"\nFecha incorrecta: {date_str}. Formato esperado: DD/MM/YYYY")
