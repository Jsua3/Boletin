"""El HTML del boletín: el mismo documento sirve para la web y para el PDF."""

import pytest
from conftest import leer_datos
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from boletin_semestral.edicion import cargar
from boletin_semestral.modelo import Edicion
from boletin_semestral.render import Modo, copiar_estaticos, manuscrita, parrafos, renderizar


def _edicion_con(carpeta, cambio) -> Edicion:
    datos = leer_datos(carpeta)
    cambio(datos)
    return Edicion.model_validate(datos)


def test_borrador_lleva_marca_y_recuadros(carpeta_edicion):
    def marcar(datos):
        datos["secciones"][1]["pendiente"] = "Falta X"

    html = HTMLParser(renderizar(_edicion_con(carpeta_edicion, marcar), Modo.BORRADOR))

    assert html.css_first(".marca-borrador") is not None
    assert any("Falta X" in p.text() for p in html.css(".pendiente"))


def test_final_no_lleva_marca_ni_recuadros(carpeta_edicion):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), Modo.FINAL))

    assert html.css_first(".marca-borrador") is None
    assert html.css(".pendiente") == []


def test_cada_seccion_es_una_pagina(carpeta_edicion):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), Modo.FINAL))

    assert len(html.css(".pagina.seccion")) == 6
    for clase in ("portada", "editorial", "contraportada"):
        assert html.css_first(f".pagina.{clase}") is not None


def test_titulo_con_manuscrita(carpeta_edicion):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), Modo.FINAL))

    assert "planeta" in [em.text() for em in html.css("em.manuscrita")]


def test_barras_del_comparativo(carpeta_edicion):
    html = renderizar(cargar(carpeta_edicion), Modo.FINAL)

    assert "width: 90.0%" in html
    assert "width: 100.0%" in html
    assert "left: 80.0%" in html
    assert "90,0 %" in html


def test_videos_reproductor_y_qr(carpeta_edicion):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), Modo.FINAL))

    reproductor = html.css_first(".solo-pantalla iframe")
    assert "youtube-nocookie.com/embed/abc123XYZ00" in reproductor.attributes["src"]
    assert html.css_first(".solo-impresion svg") is not None


def test_textos_con_caracteres_especiales(carpeta_edicion):
    def ensuciar(datos):
        datos["secciones"][1]["cuerpo"] = (
            'A & B <script>alert(1)</script> "citas" año ñandú 5 * 3 = 15 * 2'
        )

    html = renderizar(_edicion_con(carpeta_edicion, ensuciar), Modo.FINAL)

    assert "&lt;script&gt;" in html
    assert "<script>alert" not in html
    assert "5 * 3 = 15 * 2" in html
    assert "ñandú" in html
    assert HTMLParser(html).css_first(".seccion--texto .cuerpo em.manuscrita") is None


def test_proyectos_sin_fotos_no_dibujan_huecos(carpeta_edicion):
    def sin_fotos(datos):
        del datos["secciones"][2]["proyectos"][0]["foto"]

    html = HTMLParser(renderizar(_edicion_con(carpeta_edicion, sin_fotos), Modo.FINAL))

    assert html.css(".proyecto__sin-foto") == []
    assert html.css_first(".proyectos--sin-fotos") is not None


def test_comparativo_sin_datos_no_dibuja_leyenda(carpeta_edicion):
    def sin_grupos(datos):
        datos["secciones"][3]["grupos"] = []

    html = HTMLParser(renderizar(_edicion_con(carpeta_edicion, sin_grupos), Modo.BORRADOR))

    assert html.css(".seccion--comparativo .leyenda") == []


def test_manuscrita_escapa_y_marca():
    assert str(manuscrita("<b>*hola*</b>")) == '&lt;b&gt;<em class="manuscrita">hola</em>&lt;/b&gt;'


def test_parrafos_y_negrita():
    resultado = str(parrafos("a\n\nb **c**"))

    assert resultado.count("<p>") == 2
    assert "<strong>c</strong>" in resultado


def test_copiar_estaticos(tmp_path):
    copiar_estaticos(tmp_path)

    for nombre in ("estilo.css", "movimiento.js", "riel.js", "logo-humboldt.png"):
        assert (tmp_path / nombre).is_file()
    assert len(list((tmp_path / "fuentes").glob("*.woff2"))) == 5


ANCLAS = ["#portada", "#editorial"] + [f"#seccion-{n:02d}" for n in range(1, 7)]
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


def test_el_indice_enlaza_cada_parte_en_orden(carpeta_edicion):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), Modo.FINAL))

    enlaces = html.css(".riel__lista a")
    assert [a.attributes["href"] for a in enlaces] == ANCLAS
    assert [a.text() for a in enlaces] == NOMBRES
    numeros = [a.attributes["data-num"] or "" for a in enlaces]
    assert numeros == ["", ""] + [f"{n:02d}" for n in range(1, 7)]
    assert [a.attributes["href"] for a in html.css(".hoja__lista a")] == ANCLAS
    for ancla in ANCLAS:
        assert len(html.css(f'[id="{ancla[1:]}"]')) == 1


def test_etiquetas_repetidas_tienen_identificadores_distintos(carpeta_edicion):
    def repetir(datos):
        datos["secciones"][1]["etiqueta"] = "Proyectos"
        datos["secciones"][2]["etiqueta"] = "Proyectos"

    html = HTMLParser(renderizar(_edicion_con(carpeta_edicion, repetir), Modo.FINAL))

    identificadores = [pagina.attributes.get("id") for pagina in html.css(".pagina")]
    assert None not in identificadores
    assert len(set(identificadores)) == len(identificadores) == 9


def test_la_etiqueta_se_escapa_en_el_indice(carpeta_edicion):
    def ensuciar(datos):
        datos["secciones"][0]["etiqueta"] = "<b>A&B</b>"

    crudo = renderizar(_edicion_con(carpeta_edicion, ensuciar), Modo.FINAL)

    assert "<b>A&B</b>" not in crudo
    enlace = HTMLParser(crudo).css_first('.riel__lista a[href="#seccion-01"]')
    assert enlace is not None
    assert enlace.text() == "<b>A&B</b>"


def test_edicion_sin_secciones_solo_lista_portada_y_editorial(carpeta_edicion):
    def vaciar(datos):
        datos["secciones"] = []

    html = HTMLParser(renderizar(_edicion_con(carpeta_edicion, vaciar), Modo.BORRADOR))

    assert [a.attributes["href"] for a in html.css(".riel__lista a")] == ["#portada", "#editorial"]


@pytest.mark.parametrize(
    ("modo", "nombre"),
    [(Modo.BORRADOR, "boletin-vol-8-borrador.pdf"), (Modo.FINAL, "boletin-vol-8.pdf")],
)
def test_enlace_al_pdf_segun_el_modo(carpeta_edicion, modo, nombre):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), modo))

    enlaces = html.css("a.cabecera__pdf, a.hoja__pdf")
    assert len(enlaces) == 2
    for enlace in enlaces:
        assert enlace.attributes["href"] == nombre
        assert "download" in enlace.attributes


def test_la_navegacion_no_se_imprime(carpeta_edicion):
    html = HTMLParser(renderizar(cargar(carpeta_edicion), Modo.FINAL))

    for selector in (".cabecera", ".riel", ".hoja"):
        nodo = html.css_first(selector)
        assert nodo is not None, selector
        assert "solo-pantalla" in nodo.attributes["class"].split()


def test_las_secciones_de_texto_alternan_el_lado(carpeta_edicion):
    def triplicar(datos):
        texto = datos["secciones"][1]
        datos["secciones"] += [dict(texto), dict(texto)]

    html = HTMLParser(renderizar(_edicion_con(carpeta_edicion, triplicar), Modo.FINAL))

    clases = [seccion.attributes["class"].split() for seccion in html.css(".seccion--texto")]
    assert ["seccion--invertida" in c for c in clases] == [False, True, False]
