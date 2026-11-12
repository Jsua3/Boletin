"""La web del boletín en un navegador de verdad: disposición, navegación e impresión.

Se saltan si no hay Chromium; `BOLETIN_CHROMIUM` permite usar otro ejecutable (ver conftest).
"""

import json
import os
from pathlib import Path

import pytest
from conftest import escribir_edicion, leer_datos
from playwright.sync_api import Browser, Page

from boletin_semestral import pdf
from boletin_semestral.edicion import cargar
from boletin_semestral.modelo import Edicion
from boletin_semestral.render import Modo

LINEA_BASE = Path(__file__).parent / "datos" / "impresion_base.json"

# Lo que se mide para saber si la impresión cambió: una caja por cada elemento de estos.
SELECTORES = [
    ".pagina",
    ".antetitulo",
    ".titulo",
    ".regla",
    ".cuerpo p",
    "figure img",
    "figcaption",
    ".cifra",
    ".franja",
    ".proyecto",
    ".grupo",
    ".indicador",
    ".fila",
    ".video",
    ".video__impreso",
    ".portada__foto",
    ".marca",
    ".portada__titular",
    ".portada__pie",
    ".firma",
    ".contraportada__cuerpo",
]

_FIRMA = """(selectores) => [...document.querySelectorAll('main.boletin *')].flatMap((el) => {
    const i = selectores.findIndex((s) => el.matches(s));
    if (i < 0) return [];
    const r = el.getBoundingClientRect();
    return [[i, r.x, r.y + scrollY, r.width, r.height].map(Math.round)];
})"""

_CAJA = """([selector, n]) => {
    const r = document.querySelectorAll(selector)[n].getBoundingClientRect();
    return {x: r.x, y: r.y, ancho: r.width, alto: r.height, derecha: r.right, abajo: r.bottom};
}"""


def _abrir(
    navegador: Browser,
    html: Path,
    ancho: int,
    alto: int = 900,
    ancla: str = "",
    guion: str = "",
    **contexto,
) -> tuple[Page, list[str]]:
    """Abre la página a ese tamaño y devuelve también la lista viva de errores del navegador.

    `guion` es JavaScript que corre antes que la página; `contexto` va a `new_context`.
    """
    ctx = navegador.new_context(viewport={"width": ancho, "height": alto}, **contexto)
    if guion:
        ctx.add_init_script(guion)
    # Sin red: lo que no sea un archivo local (el reproductor de YouTube) se responde vacío.
    ctx.route(
        "**/*",
        lambda ruta: (
            ruta.continue_()
            if ruta.request.url.startswith("file:")
            else ruta.fulfill(status=200, content_type="text/html", body="")
        ),
    )
    pagina = ctx.new_page()
    errores: list[str] = []
    pagina.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
    pagina.on("pageerror", lambda e: errores.append(str(e)))
    pagina.goto(html.as_uri() + ancla)
    pagina.wait_for_load_state("networkidle")
    pagina.evaluate("document.fonts.ready.then(() => true)")
    return pagina, errores


def _caja(pagina: Page, selector: str, n: int = 0) -> dict:
    """La caja del n-ésimo elemento que cumple el selector, en píxeles de la ventana."""
    return pagina.evaluate(_CAJA, [selector, n])


@pytest.mark.parametrize("ancho", [1280, 820, 390])
def test_la_pagina_abre_sin_errores(navegador, carpeta_edicion, tmp_path, ancho):
    html = escribir_edicion(cargar(carpeta_edicion), carpeta_edicion, tmp_path / "web")

    _, errores = _abrir(navegador, html, ancho)

    assert errores == []


def test_la_impresion_no_cambia(navegador, carpeta_edicion, tmp_path):
    """El PDF sale de imprimir este HTML: la posición de cada elemento impreso no se mueve.

    `BOLETIN_LINEA_BASE=1` vuelve a escribir la referencia; solo tras un cambio querido del PDF.
    """
    html = escribir_edicion(cargar(carpeta_edicion), carpeta_edicion, tmp_path / "web")
    pagina, _ = _abrir(navegador, html, pdf._ANCHO_UTIL_PX, 1000)
    pagina.emulate_media(media="print")
    firma = pagina.evaluate(_FIRMA, SELECTORES)
    mayor = navegador.version.split(".")[0]

    if os.environ.get("BOLETIN_LINEA_BASE"):
        filas = ",\n".join(f"    {json.dumps(fila)}" for fila in firma)
        LINEA_BASE.parent.mkdir(exist_ok=True)
        LINEA_BASE.write_text(
            f'{{\n  "chromium": "{mayor}",\n  "firma": [\n{filas}\n  ]\n}}\n', encoding="utf-8"
        )
        pytest.skip("línea base escrita")

    base = json.loads(LINEA_BASE.read_text(encoding="utf-8"))
    if base["chromium"] != mayor:
        pytest.skip(f"la línea base es de Chromium {base['chromium']} y este es el {mayor}")

    assert len(firma) == len(base["firma"])
    for fila, esperada in zip(firma, base["firma"], strict=True):
        assert fila[0] == esperada[0]
        cerca = all(abs(a - b) <= 1 for a, b in zip(fila[1:], esperada[1:], strict=True))
        assert cerca, (SELECTORES[fila[0]], fila, esperada)


# ---------- Disposición del contenido ----------

_SIN_DESBORDE = "document.documentElement.scrollWidth <= document.documentElement.clientWidth"

_TEXTOS_CHICOS = """() => [...document.querySelectorAll('main.boletin *')]
    .filter((el) => el.offsetParent !== null)
    .filter((el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()))
    .filter((el) => parseFloat(getComputedStyle(el).fontSize) < 12)
    .map((el) => el.tagName + '.' + el.className + ' ' + getComputedStyle(el).fontSize)"""


def _edicion_amplia(carpeta_edicion) -> Edicion:
    """La edición de prueba con 4 cifras, 3 proyectos y dos secciones de texto (3 fotos y 1).

    Queda así: 01 Cifras, 02 Planeta (texto), 03 Emprendimiento (texto, invertida),
    04 Comunidades (proyectos), 05 Prácticas, 06 Videos y 07 Sistema.
    """
    datos = leer_datos(carpeta_edicion)
    cifras, texto, proyectos = datos["secciones"][:3]
    cifras["cifras"] = [
        {"valor": str(valor), "texto": f"cifra número {valor} del semestre"}
        for valor in (20, 4, 158, 21)
    ]
    parrafo = "Un párrafo sobre la jornada de siembra. " * 4
    texto["cuerpo"] = "\n\n".join([parrafo] * 4)
    texto["fotos"] = [
        {"archivo": "siembra.jpg", "pie": "Siembra"},
        {"archivo": "taller.jpg", "pie": "Taller"},
        {"archivo": "portada.jpg", "pie": "Grupo"},
    ]
    proyectos["proyectos"] = [
        dict(proyectos["proyectos"][0], nombre=f"Proyecto {n}") for n in (1, 2, 3)
    ]
    otra = dict(
        texto,
        etiqueta="Emprendimiento",
        titulo="Ruta de *emprendimiento*",
        fotos=[{"archivo": "taller.jpg", "pie": "Taller"}],
    )
    datos["secciones"].insert(2, otra)
    return Edicion.model_validate(datos)


def _filas(pagina: Page, selector: str, cuantos: int) -> list[int]:
    """La coordenada superior de los primeros elementos: iguales si comparten fila."""
    return [round(_caja(pagina, selector, n)["y"]) for n in range(cuantos)]


def test_en_computador_el_contenido_usa_el_ancho(navegador, carpeta_edicion, tmp_path):
    html = escribir_edicion(_edicion_amplia(carpeta_edicion), carpeta_edicion, tmp_path / "web")
    pagina, _ = _abrir(navegador, html, 1440)

    assert _caja(pagina, "main.boletin")["ancho"] >= 1100
    assert len(set(_filas(pagina, ".cifra", 4))) == 1
    assert len(set(_filas(pagina, ".proyecto", 3))) == 1
    texto, fotos = "#seccion-02 .cuerpo", "#seccion-02 .foto-principal"
    assert _caja(pagina, texto)["derecha"] <= _caja(pagina, fotos)["x"]
    texto, fotos = "#seccion-03 .cuerpo", "#seccion-03 .foto-principal"
    assert _caja(pagina, fotos)["derecha"] <= _caja(pagina, texto)["x"]
    assert _caja(pagina, ".portada__cuerpo")["derecha"] <= _caja(pagina, ".portada__foto")["x"]
    assert (
        _caja(pagina, "#editorial .encabezado")["derecha"]
        <= _caja(pagina, "#editorial .cuerpo")["x"]
    )


def test_en_tableta_van_de_dos_en_dos(navegador, carpeta_edicion, tmp_path):
    html = escribir_edicion(_edicion_amplia(carpeta_edicion), carpeta_edicion, tmp_path / "web")
    pagina, _ = _abrir(navegador, html, 820)

    cifras = _filas(pagina, ".cifra", 4)
    assert cifras[0] == cifras[1] < cifras[2] == cifras[3]
    proyectos = _filas(pagina, ".proyecto", 3)
    assert proyectos[0] == proyectos[1] < proyectos[2]


def test_en_celular_todo_va_en_una_columna(navegador, carpeta_edicion, tmp_path):
    html = escribir_edicion(_edicion_amplia(carpeta_edicion), carpeta_edicion, tmp_path / "web")
    pagina, _ = _abrir(navegador, html, 390)

    assert pagina.evaluate(_SIN_DESBORDE)
    cifras = _filas(pagina, ".cifra", 4)
    assert cifras == sorted(set(cifras))
    assert _caja(pagina, ".cifra__valor")["derecha"] <= _caja(pagina, ".cifra__texto")["x"]
    proyectos = _filas(pagina, ".proyecto", 3)
    assert proyectos == sorted(set(proyectos))
    assert pagina.evaluate(
        "(() => { const f = document.querySelector('#seccion-02 .fotos-par');"
        " return f.scrollWidth > f.clientWidth; })()"
    )
    assert pagina.evaluate(_TEXTOS_CHICOS) == []


def test_portada_sin_foto_no_se_descuadra(navegador, carpeta_edicion, tmp_path):
    datos = leer_datos(carpeta_edicion)
    del datos["portada"]["foto"]
    edicion = Edicion.model_validate(datos)
    html = escribir_edicion(edicion, carpeta_edicion, tmp_path / "web", Modo.BORRADOR)
    pagina, _ = _abrir(navegador, html, 1280)

    assert _caja(pagina, ".portada__cuerpo")["ancho"] >= 800
    assert pagina.evaluate(_SIN_DESBORDE)


# ---------- Navegación sin JavaScript ----------


def _web(carpeta_edicion, tmp_path) -> Path:
    return escribir_edicion(cargar(carpeta_edicion), carpeta_edicion, tmp_path / "web")


def test_sin_javascript_el_riel_es_una_lista_que_funciona(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(
        navegador,
        _web(carpeta_edicion, tmp_path),
        1280,
        java_script_enabled=False,
        reduced_motion="reduce",
    )

    riel = _caja(pagina, ".riel")
    assert round(riel["ancho"]) == 264
    assert round(riel["derecha"]) == 1280
    assert round(_caja(pagina, "main.boletin")["derecha"]) == round(riel["x"])

    pagina.click('.riel__lista a[href="#seccion-03"]')

    assert pagina.evaluate("location.hash") == "#seccion-03"
    assert 0 <= _caja(pagina, "#seccion-03")["y"] <= _caja(pagina, ".cabecera")["alto"] + 4


def test_sin_javascript_la_cabecera_ofrece_el_pdf(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 390, java_script_enabled=False)

    assert pagina.locator(".cabecera__pdf").is_visible()
    assert _caja(pagina, ".cabecera__pdf")["alto"] >= 44
    assert not pagina.locator(".cabecera__secciones").is_visible()
    assert pagina.evaluate(_SIN_DESBORDE)


def test_la_cabecera_queda_fija(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 1280, reduced_motion="reduce")

    pagina.evaluate("window.scrollTo(0, 2000)")

    assert pagina.evaluate("scrollY") == 2000
    assert round(_caja(pagina, ".cabecera")["y"]) == 0


def test_en_tableta_no_hay_riel(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 820)

    assert not pagina.locator(".riel").is_visible()


# ---------- Cabecera viva y hoja de secciones (celular) ----------

_HOJA_ABIERTA = "document.querySelector('dialog.hoja').open"


def _celular(navegador, carpeta_edicion, tmp_path, **opciones) -> tuple[Page, list[str]]:
    web = _web(carpeta_edicion, tmp_path)
    return _abrir(navegador, web, 390, 844, reduced_motion="reduce", **opciones)


def test_secciones_abre_la_hoja_y_lleva_a_la_seccion(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _celular(navegador, carpeta_edicion, tmp_path)
    boton = _caja(pagina, ".cabecera__secciones")
    assert pagina.locator(".cabecera__secciones").is_visible()
    assert boton["ancho"] >= 44
    assert boton["alto"] >= 44

    pagina.click(".cabecera__secciones")

    assert pagina.evaluate(_HOJA_ABIERTA)
    altos = pagina.evaluate(
        "[...document.querySelectorAll('.hoja__lista a')]"
        ".map((a) => a.getBoundingClientRect().height)"
    )
    assert min(altos) >= 48

    pagina.click('.hoja__lista a[href="#seccion-03"]')
    pagina.wait_for_timeout(300)

    assert not pagina.evaluate(_HOJA_ABIERTA)
    assert abs(_caja(pagina, "#seccion-03")["y"] - _caja(pagina, ".cabecera")["alto"]) <= 4
    assert pagina.inner_text(".cabecera__num") == "03"
    assert pagina.inner_text(".cabecera__nombre") == "Comunidades"
    actuales = pagina.evaluate(
        "[...document.querySelectorAll('.hoja__lista a[aria-current]')].map((a) => a.hash)"
    )
    assert actuales == ["#seccion-03"]


def test_la_hoja_se_cierra_con_escape_y_devuelve_el_foco(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _celular(navegador, carpeta_edicion, tmp_path)
    pagina.click(".cabecera__secciones")
    assert pagina.evaluate(_HOJA_ABIERTA)

    pagina.keyboard.press("Escape")

    assert not pagina.evaluate(_HOJA_ABIERTA)
    assert "cabecera__secciones" in pagina.evaluate("document.activeElement.className")


def test_la_linea_de_avance_crece(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _celular(navegador, carpeta_edicion, tmp_path)
    assert _caja(pagina, ".cabecera__avance i")["ancho"] <= 1

    pagina.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    pagina.wait_for_timeout(300)

    lleno = _caja(pagina, ".cabecera")["ancho"]
    assert abs(_caja(pagina, ".cabecera__avance i")["ancho"] - lleno) <= 2


def test_al_abrir_con_ancla_la_cabecera_dice_la_seccion(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _celular(navegador, carpeta_edicion, tmp_path, ancla="#seccion-02")
    pagina.wait_for_timeout(300)

    assert pagina.inner_text(".cabecera__nombre") == "Planeta"


def test_sin_dialog_no_hay_boton(navegador, carpeta_edicion, tmp_path):
    sin_dialog = "delete HTMLDialogElement.prototype.showModal"
    pagina, errores = _celular(navegador, carpeta_edicion, tmp_path, guion=sin_dialog)

    assert not pagina.locator(".cabecera__secciones").is_visible()
    assert pagina.locator(".cabecera__pdf").is_visible()
    assert errores == []


# ---------- El riel de letras (computador) ----------

NOMBRES = [
    "Portada",
    "Editorial",
    "Cifras",
    "Planeta",
    "Comunidades",
    "Prácticas empresariales",
    "Videos",
    "Sistema",
]

_LETRAS = "document.querySelectorAll('.riel__letra').length"

# El giro de cada letra de una parte, en grados, leído de su transformación calculada.
_ANGULOS = """(parte) => [...document.querySelectorAll('.riel__letra')]
    .filter((letra) => parte === null || letra.dataset.parte === String(parte))
    .map((letra) => {
        const m = new DOMMatrix(getComputedStyle(letra).transform);
        return Math.round(Math.atan2(m.b, m.a) * 180 / Math.PI);
    })"""

_LLEVAR = """([selector, fraccion]) => {
    const arriba = document.querySelector(selector).getBoundingClientRect().top + scrollY;
    window.scrollTo({top: arriba - innerHeight * fraccion, behavior: 'instant'});
}"""


def _recorrer(pagina: Page, pasos: int = 12):
    """Baja por toda la página en pasos iguales y se detiene un momento en cada uno."""
    total = pagina.evaluate("document.documentElement.scrollHeight - innerHeight")
    for paso in range(pasos + 1):
        pagina.evaluate(f"window.scrollTo({{top: {total * paso / pasos}, behavior: 'instant'}})")
        pagina.wait_for_timeout(80)
        yield paso


def test_el_riel_crea_una_letra_por_caracter(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 1280)

    assert "riel--vivo" in pagina.get_attribute(".riel", "class")
    assert pagina.evaluate(_LETRAS) == sum(len(n.replace(" ", "")) for n in NOMBRES)
    assert pagina.get_attribute(".riel__capa", "aria-hidden") == "true"
    assert pagina.locator(".riel__lista a").all_text_contents() == NOMBRES


def test_las_letras_son_las_mismas_al_desplazarse(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 1280)
    antes = pagina.evaluate(
        "(window.__letras = [...document.querySelectorAll('.riel__letra')]).length"
    )
    assert antes > 0

    for _ in _recorrer(pagina):
        pass

    assert pagina.evaluate("window.__letras.every((letra) => letra.isConnected)")
    assert pagina.evaluate(_LETRAS) == antes


def test_el_titulo_actual_va_horizontal_y_el_siguiente_vertical(
    navegador, carpeta_edicion, tmp_path
):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 1280)

    pagina.evaluate(_LLEVAR, ["#seccion-03", 0.8])
    pagina.wait_for_timeout(700)

    actual, siguiente = pagina.evaluate(_ANGULOS, 3), pagina.evaluate(_ANGULOS, 4)
    assert actual
    assert all(abs(angulo) <= 1 for angulo in actual)
    assert siguiente
    assert all(abs(angulo + 90) <= 1 for angulo in siguiente)


def test_clic_en_el_riel_lleva_a_la_seccion(navegador, carpeta_edicion, tmp_path):
    web = _web(carpeta_edicion, tmp_path)
    pagina, _ = _abrir(navegador, web, 1280, reduced_motion="reduce")
    enlace = '.riel__lista a[href="#seccion-04"]'

    pagina.click(enlace)
    pagina.wait_for_timeout(300)

    assert abs(_caja(pagina, "#seccion-04")["y"] - _caja(pagina, ".cabecera")["alto"]) <= 4
    assert pagina.get_attribute(enlace, "aria-current") == "true"


def test_al_abrir_con_ancla_el_riel_muestra_esa_seccion(navegador, carpeta_edicion, tmp_path):
    pagina, _ = _abrir(navegador, _web(carpeta_edicion, tmp_path), 1280, ancla="#seccion-03")
    pagina.wait_for_timeout(800)

    enlace = '.riel__lista a[href="#seccion-03"]'
    assert pagina.get_attribute(enlace, "aria-current") == "true"
    angulos = pagina.evaluate(_ANGULOS, 4)
    assert angulos
    assert all(abs(angulo) <= 1 for angulo in angulos)


def test_con_movimiento_reducido_no_hay_letras_giradas(navegador, carpeta_edicion, tmp_path):
    web = _web(carpeta_edicion, tmp_path)
    pagina, _ = _abrir(navegador, web, 1280, reduced_motion="reduce")
    assert pagina.evaluate(_LETRAS) > 0

    for _ in _recorrer(pagina):
        assert set(pagina.evaluate(_ANGULOS, None)) == {0}


def test_cruzar_1100_px_no_duplica_letras(navegador, carpeta_edicion, tmp_path):
    pagina, errores = _abrir(navegador, _web(carpeta_edicion, tmp_path), 1280)
    antes = pagina.evaluate(_LETRAS)
    assert antes > 0

    pagina.set_viewport_size({"width": 800, "height": 900})
    pagina.wait_for_timeout(300)
    assert not pagina.locator(".riel").is_visible()
    assert pagina.evaluate(_LETRAS) == 0

    pagina.set_viewport_size({"width": 1280, "height": 900})
    pagina.wait_for_timeout(300)
    assert pagina.evaluate(_LETRAS) == antes
    assert errores == []


def test_nombre_largo_no_se_sale_del_riel(navegador, carpeta_edicion, tmp_path):
    datos = leer_datos(carpeta_edicion)
    datos["secciones"][1]["etiqueta"] = "Internacionalizacionesextraordinarias & <co>"
    edicion = Edicion.model_validate(datos)
    web = escribir_edicion(edicion, carpeta_edicion, tmp_path / "web")
    pagina, errores = _abrir(navegador, web, 1280, ancla="#seccion-02", reduced_motion="reduce")
    pagina.wait_for_timeout(400)

    fuera = pagina.evaluate(
        """() => {
            const riel = document.querySelector('.riel').getBoundingClientRect();
            return [...document.querySelectorAll('.riel__letra[data-parte="3"]')]
                .map((letra) => letra.getBoundingClientRect())
                .filter((c) => c.left < riel.left - 1 || c.right > riel.right + 1
                    || c.top < riel.top - 1 || c.bottom > riel.bottom + 1).length;
        }"""
    )
    assert (
        pagina.evaluate("document.querySelectorAll('.riel__letra[data-parte=\"3\"]').length") > 30
    )
    assert fuera == 0
    assert errores == []


def test_edicion_sin_secciones_no_falla(navegador, carpeta_edicion, tmp_path):
    datos = leer_datos(carpeta_edicion)
    datos["secciones"] = []
    edicion = Edicion.model_validate(datos)
    web = escribir_edicion(edicion, carpeta_edicion, tmp_path / "web", Modo.BORRADOR)

    pagina, errores = _abrir(navegador, web, 1280)

    assert errores == []
    assert pagina.evaluate(_LETRAS) == len("Portada") + len("Editorial")
