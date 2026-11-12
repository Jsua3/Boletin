# Web responsiva del boletín semestral — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que la web del boletín use el ancho de la pantalla en el computador, con un riel lateral cuyas
letras viajan de vertical a horizontal, y sea cómoda al tacto en el celular, sin cambiar el PDF.

**Architecture:** El HTML gana una cabecera, un índice de enlaces reales y una hoja de secciones; el
contenido no cambia de orden. Toda la disposición nueva va en `@media screen` dentro de `estilo.css`.
Un script nuevo, `riel.js`, mejora ese índice: en computador dibuja y mueve las letras; bajo 1100 px
atiende la cabecera y la hoja. Sin el script, el boletín se lee completo.

**Tech Stack:** Python 3.13 · Jinja2 · CSS (grid, sticky, scroll-snap) · JavaScript sin dependencias ·
Playwright (pruebas de navegador) · pytest · selectolax · Ruff

**Spec:** `docs/superpowers/specs/2026-11-11-web-responsiva-design.md`. Quien ejecute este plan lee las
dos cosas: el spec dice qué y por qué; este plan, los nombres, los valores y las pruebas.

## Global Constraints

- **Todo en español:** símbolos, comentarios, mensajes, nombres de pruebas y commits (Conventional
  Commits).
- **El PDF no cambia.** Las reglas nuevas de disposición van dentro de `@media screen`. El bloque
  `@media print` y `pdf.py` no se tocan.
- **`edicion.toml` y el modelo no cambian.** No hay campos nuevos.
- **Sin dependencias nuevas** de Python ni de JavaScript. Nada se carga de internet.
- **Cortes de pantalla:** computador 1100 px o más; tableta 700 a 1099 px; celular menos de 700 px.
- **Colores:** azul `#143D68`, azul claro `#9DB7D6`, rojo `#BD1822`, línea `#DDE3EA`, fondo de franja
  `#f3f6fa`. En el riel: gris `#a3acb7` y celeste `#8fabcf`.
- **Tamaños mínimos:** ningún texto bajo 12 px; cuerpo de 16 px o más; todo lo que se toca mide al
  menos 44 × 44 px; filas de la hoja de 48 px o más.
- **La clase `.barra` ya existe** (barras del comparativo). La barra superior se llama `.cabecera`.
- **La navegación no se imprime:** `.cabecera`, `.riel` y `.hoja` llevan la clase `solo-pantalla`.
- **Antes de cada commit:** `set -o pipefail`, luego `uv run ruff format .`, `uv run ruff check .` y
  `uv run pytest`. `docs/` está excluido de Ruff.
- **Commits:** uno por tarea, solo si el usuario ya autorizó los commits de esta rama. Sin esa
  autorización, se deja el cambio sin confirmar y se avisa. Nunca `push` sin que lo pida.
- **GateGuard:** un hook rechaza la primera escritura de cada archivo. Hay que decir quién lo usa, que
  no existe otro igual y la instrucción del usuario, y reintentar.
- **Chromium:** el 1254 no está instalado y **no se corre** `playwright install` (lo bloquea una
  instalación de otro proyecto que no se debe detener). Las pruebas de navegador usan el ejecutable de
  la variable `BOLETIN_CHROMIUM`. En este computador:
  `C:\Users\Predator\AppData\Local\ms-playwright\chromium_headless_shell-1234\chrome-headless-shell-win64\chrome-headless-shell.exe`
- **Rama:** `feat/web-responsiva`.

## Review Focus

1. **Etiqueta muy larga o con símbolos** (`&`, `<`, comillas): debe salir escapada y nunca salirse del
   riel. → Tarea 2, `test_la_etiqueta_se_escapa_en_el_indice`; Tarea 6,
   `test_nombre_largo_no_se_sale_del_riel`.
2. **Portada sin foto**, lo normal en un borrador: la portada partida no puede descuadrarse. → Tarea 3,
   `test_portada_sin_foto_no_se_descuadra`.
3. **Abrir con un ancla o recargar a mitad de página** (`index.html#seccion-03`): la navegación debe
   mostrar esa sección, no la portada. → Tarea 5, `test_al_abrir_con_ancla_la_cabecera_dice_la_seccion`;
   Tarea 6, `test_al_abrir_con_ancla_el_riel_muestra_esa_seccion`.
4. **Cambiar el ancho de la ventana cruzando 1100 px** (girar una tableta): el riel aparece y
   desaparece sin duplicar letras ni dar errores. → Tarea 6, `test_cruzar_1100_px_no_duplica_letras`.
5. **Edición sin secciones**, la de una edición recién creada: el índice lista solo Portada y Editorial
   y el script no falla. → Tarea 2, `test_edicion_sin_secciones_solo_lista_portada_y_editorial`;
   Tarea 6, `test_edicion_sin_secciones_no_falla`.

---

## Mapa de archivos

| Archivo | Responsabilidad |
|---|---|
| `src/boletin_semestral/render.py` | Lista de partes, identificadores, nombre del PDF, copia de estáticos |
| `src/boletin_semestral/armado.py` | Usa el nombre del PDF de `render.py` |
| `src/boletin_semestral/plantillas/_cabecera.html.j2` | Nuevo: la cabecera, compartida con el índice del sitio |
| `src/boletin_semestral/plantillas/_partes.html.j2` | Nuevo: macro con la lista de enlaces a las partes |
| `src/boletin_semestral/plantillas/boletin.html.j2` | Cabecera, lienzo, identificadores, riel, hoja y script |
| `src/boletin_semestral/plantillas/indice.html.j2` | Cabecera con la marca |
| `src/boletin_semestral/estaticos/estilo.css` | Disposición en pantalla, cabecera, riel y hoja |
| `src/boletin_semestral/estaticos/riel.js` | Nuevo: cabecera viva, hoja y riel de letras |
| `tests/conftest.py` | Navegador de pruebas y `escribir_edicion` |
| `tests/test_semestral_web.py` | Nuevo: pruebas de navegador |
| `tests/datos/impresion_base.json` | Nuevo: geometría de impresión de referencia |
| `tests/test_semestral_render.py`, `test_semestral_armado.py`, `test_semestral_sitio.py`, `test_semestral_pdf.py` | Pruebas nuevas y ajustes |

---

### Task 1: Navegador de pruebas y red de seguridad de la impresión

Se hace con el código **sin cambios**: fija cómo se imprime hoy para detectar cualquier desvío después.

**Files:**
- Modify: `tests/conftest.py`
- Modify: `tests/test_semestral_pdf.py` (usa `escribir_edicion`; conserva `_chromium_o_saltar`)
- Create: `tests/test_semestral_web.py`
- Create: `tests/datos/impresion_base.json` (lo escribe la prueba)
- Create: `salida/armar_local.py` (no se versiona: `salida/` está en `.gitignore`)

**Interfaces:**
- Produces, en `tests/conftest.py`:
  - `navegador` — fixture de sesión que entrega un `playwright.sync_api.Browser`. Lanza Chromium con
    `executable_path=os.environ["BOLETIN_CHROMIUM"]` si la variable existe; si no, el de Playwright. Si
    no hay ninguno, `pytest.skip("Chromium no disponible (BOLETIN_CHROMIUM o playwright install)")`.
  - `escribir_edicion(edicion: Edicion, carpeta_edicion: Path, destino: Path, modo: Modo = Modo.FINAL) -> Path`
    — deja en `destino` el `index.html`, los estáticos y las fotos, y devuelve la ruta del HTML.
- Produces, en `tests/test_semestral_web.py`:
  - `_abrir(navegador, html: Path, ancho: int, alto: int = 900, ancla: str = "", **contexto) -> tuple[Page, list[str]]`
    — abre `html.as_uri() + ancla` en un contexto nuevo con ese tamaño, espera `networkidle` y
    `document.fonts.ready`, y devuelve la página y la lista viva de errores (`console` de tipo `error`
    y `pageerror`). `contexto` pasa a `new_context` (`reduced_motion`, `java_script_enabled`).
  - `_caja(pagina, selector, n=0) -> dict` — `getBoundingClientRect()` del n-ésimo elemento.

- [ ] **Step 1: Escribir `navegador` y `escribir_edicion`, y pasar `test_semestral_pdf.py` a usar la segunda**

Run: `uv run pytest -q` → 72 pasan, 2 se saltan (igual que antes).

- [ ] **Step 2: Escribir las dos pruebas de red de seguridad**

```python
SELECTORES = [
    ".pagina", ".antetitulo", ".titulo", ".regla", ".cuerpo p", "figure img", "figcaption",
    ".cifra", ".franja", ".proyecto", ".grupo", ".indicador", ".fila", ".video", ".video__impreso",
    ".portada__foto", ".marca", ".portada__titular", ".portada__pie", ".firma",
    ".contraportada__cuerpo",
]

@pytest.mark.parametrize("ancho", [1280, 820, 390])
def test_la_pagina_abre_sin_errores(navegador, carpeta_edicion, tmp_path, ancho):
    ...  # errores == []

def test_la_impresion_no_cambia(navegador, carpeta_edicion, tmp_path):
    ...
```

`test_la_impresion_no_cambia`:
- abre la edición de prueba con ancho `pdf._ANCHO_UTIL_PX`, llama `emulate_media(media="print")` y
  arma la firma: por cada elemento de `main.boletin` que cumpla algún selector de `SELECTORES`, en
  orden del documento, `[índice del selector, x, y, ancho, alto]` redondeados a enteros;
- lee `tests/datos/impresion_base.json`, de forma `{"chromium": "<versión mayor>", "firma": [...]}`;
- con `BOLETIN_LINEA_BASE=1` escribe ese archivo y hace `pytest.skip("línea base escrita")`;
- si la versión mayor del navegador no es la del archivo, `pytest.skip` con un mensaje que lo diga;
- exige el mismo número de filas, el mismo selector en cada fila y cada medida a no más de 1 px.

- [ ] **Step 3: Escribir la línea base y comprobar que las pruebas pasan**

Run: `BOLETIN_CHROMIUM=<ruta> BOLETIN_LINEA_BASE=1 uv run pytest tests/test_semestral_web.py -q`
Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py -q` → 4 pasan.
Sin la variable: las 4 se saltan.

- [ ] **Step 4: Guardar la referencia del PDF real del Vol. 8**

`salida/armar_local.py` corre la consola pasándole a `BrowserType.launch` el ejecutable de
`BOLETIN_CHROMIUM`:

```python
import os, sys
from playwright.sync_api import BrowserType

_lanzar = BrowserType.launch
BrowserType.launch = lambda self, *a, **k: _lanzar(
    self, *a, **{"executable_path": os.environ["BOLETIN_CHROMIUM"], **k}
)
from boletin_semestral.cli import main  # noqa: E402

raise SystemExit(main(sys.argv[1:]))
```

Run: `BOLETIN_CHROMIUM=<ruta> uv run python salida/armar_local.py armar 2026-2 | tee salida/linea-base-armar.txt`
Anotar en ese archivo el número de páginas del PDF (`/Type /Page`, como lo cuenta `pdf.py`).
Expected: «Secciones de más de una página: Nuestro compromiso con el planeta (2 páginas), Ruta de
emprendimiento (2 páginas)» y 10 pendientes.

- [ ] **Step 5: Commit** — `test(semestral): navegador de pruebas y línea base de impresión`

---

### Task 2: Marcado de la navegación

Sin estilos todavía: la página queda funcional, con el índice a la vista como lista simple.

**Files:**
- Modify: `src/boletin_semestral/render.py`, `src/boletin_semestral/armado.py`
- Create: `src/boletin_semestral/plantillas/_cabecera.html.j2`, `_partes.html.j2`
- Modify: `src/boletin_semestral/plantillas/boletin.html.j2`, `_portada.html.j2`, `_editorial.html.j2`,
  `_contraportada.html.j2`
- Create: `src/boletin_semestral/estaticos/riel.js` (solo el esqueleto)
- Test: `tests/test_semestral_render.py`, `tests/test_semestral_armado.py`

**Interfaces:**
- Produces, en `render.py`:
  - `class Parte(NamedTuple)`: `id: str`, `num: str`, `nombre: str`
  - `partes(edicion: Edicion) -> list[Parte]` — `Parte("portada", "", "Portada")`,
    `Parte("editorial", "", "Editorial")` y, por cada sección, `Parte("seccion-NN", "NN", etiqueta)`
    con `NN` de dos dígitos desde `01`.
  - `nombre_pdf(edicion: Edicion, modo: Modo) -> str` — `boletin-vol-N-borrador.pdf` en borrador y
    `boletin-vol-N.pdf` en final. `armado.py` deja de armar el nombre y llama a esta función.
  - `renderizar` pasa a la plantilla `partes` y `pdf`; cada elemento de `secciones` gana `id` e
    `invertida` (verdadero en la 2.ª, 4.ª, … sección de tipo `texto`).
  - `copiar_estaticos` copia también `riel.js`.
- Produces, el contrato de marcado que usan las tareas 3 a 6:

```html
<header class="cabecera solo-pantalla">
  <a class="cabecera__marca" href="#portada"><img src="logo-humboldt.png" alt="">
    <span class="cabecera__titulo">Proyección <em class="manuscrita">Social</em></span>
    <span class="cabecera__vol">Vol. 8 · Diciembre 2026</span></a>
  <p class="cabecera__actual"><span class="cabecera__num"></span><span class="cabecera__nombre"></span></p>
  <a class="boton cabecera__pdf" href="boletin-vol-8.pdf" download>Descargar PDF</a>
  <button class="boton cabecera__secciones" type="button">Secciones</button>
  <span class="cabecera__avance" aria-hidden="true"><i></i></span>
</header>
<div class="lienzo">
  <main class="boletin"> … <section id="portada" …> <section id="editorial" …>
    <section id="seccion-01" class="pagina seccion seccion--cifras" …> … <section id="contraportada" …></main>
  <nav class="riel solo-pantalla" aria-label="Secciones del boletín">
    <ol class="riel__lista"><li><a href="#portada" data-num="">Portada</a></li>
      <li><a href="#seccion-01" data-num="01">Cifras</a></li> …</ol>
  </nav>
</div>
<dialog class="hoja solo-pantalla" aria-label="Secciones">
  <div class="hoja__cabeza"><h2 class="hoja__titulo">Secciones</h2>
    <button class="hoja__cerrar" type="button" aria-label="Cerrar">✕</button></div>
  <ol class="hoja__lista"> … los mismos enlaces … </ol>
  <a class="boton hoja__pdf" href="boletin-vol-8.pdf" download>Descargar PDF</a>
</dialog>
<script src="movimiento.js" defer></script>
<script src="riel.js" defer></script>
```

- `_partes.html.j2` define la macro `lista(partes, clase)`, usada en el riel y en la hoja.
- `_cabecera.html.j2` recibe `pdf` y `partes`; si faltan, omite el enlace, el botón, el nombre actual y
  la línea de avance, y la marca no es enlace (así la usa el índice del sitio en la Tarea 4).
- Una sección `texto` con `invertida` lleva además la clase `seccion--invertida`.
- `riel.js` queda como una función autoejecutable que solo agrega la clase `con-js` a `<html>`.

- [ ] **Step 1: Escribir las pruebas que fallan**

En `tests/test_semestral_render.py`:

```python
ANCLAS = ["#portada", "#editorial"] + [f"#seccion-{n:02d}" for n in range(1, 7)]
NOMBRES = ["Portada", "Editorial", "Cifras", "Planeta", "Comunidades",
           "Prácticas empresariales", "Videos", "Sistema"]

def test_el_indice_enlaza_cada_parte_en_orden(carpeta_edicion):
    # .riel__lista a: href == ANCLAS, texto == NOMBRES, data-num == ["", "", "01", …, "06"]
    # .hoja__lista a: href == ANCLAS
    # cada ancla apunta a un id que existe exactamente una vez

def test_etiquetas_repetidas_tienen_identificadores_distintos(carpeta_edicion):
    # dos secciones con etiqueta "Proyectos": los id de .pagina no se repiten

def test_la_etiqueta_se_escapa_en_el_indice(carpeta_edicion):
    # etiqueta '<b>A&B</b>': el HTML trae "&lt;b&gt;A&amp;B&lt;/b&gt;" y el texto del enlace es '<b>A&B</b>'

def test_edicion_sin_secciones_solo_lista_portada_y_editorial(carpeta_edicion):
    # secciones = []: los href de .riel__lista a son ["#portada", "#editorial"]

def test_enlace_al_pdf_segun_el_modo(carpeta_edicion):
    # BORRADOR: a.cabecera__pdf y a.hoja__pdf → "boletin-vol-8-borrador.pdf", con atributo download
    # FINAL: "boletin-vol-8.pdf"

def test_la_navegacion_no_se_imprime(carpeta_edicion):
    # .cabecera, .riel y .hoja llevan la clase solo-pantalla

def test_las_secciones_de_texto_alternan_el_lado(carpeta_edicion):
    # con tres secciones de texto: solo la segunda lleva seccion--invertida
```

`test_copiar_estaticos` pasa a exigir también `riel.js`.

En `tests/test_semestral_armado.py`:

```python
def test_el_pdf_se_llama_como_dice_el_enlace(carpeta_edicion, tmp_path):
    # en borrador y, tras _aprobar, en final: resultado.pdf.name == href de a.cabecera__pdf
    # y (resultado.destino / "riel.js").is_file()
```

- [ ] **Step 2: Verlas fallar**

Run: `uv run pytest tests/test_semestral_render.py tests/test_semestral_armado.py -q`
Expected: fallan las 8 nuevas y `test_copiar_estaticos`.

- [ ] **Step 3: Implementar `Parte`, `partes`, `nombre_pdf`, los cambios de `renderizar` y `copiar_estaticos`, las plantillas y el esqueleto de `riel.js`**

- [ ] **Step 4: Verlas pasar, con la red de seguridad**

Run: `uv run pytest -q` → todo pasa.
Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py -q` → 4 pasan: la impresión no
cambió y no hay errores de consola.

- [ ] **Step 5: Commit** — `feat(semestral): índice de partes, cabecera y hoja en el HTML`

---

### Task 3: Disposición del contenido en pantalla

**Files:**
- Modify: `src/boletin_semestral/estaticos/estilo.css`
- Test: `tests/test_semestral_web.py`

**Interfaces:**
- Consumes: el contrato de marcado de la Tarea 2; `_abrir` y `_caja` de la Tarea 1.
- Produces: las variables `--alto-cabecera` (64 px en computador; 63 px bajo 1100 px, que son 60 de
  barra y 3 de línea de avance) y `--ancho-riel: 264px`, que usan las tareas 4 a 6.

**Decisiones de CSS** (todas dentro de `@media screen`; el bloque `@media (max-width: 600px)` actual se
reemplaza por las reglas de celular):

- **Franjas:** `.pagina` pierde sombra, bordes redondos y margen. Fondo blanco, y `#f3f6fa` en las
  secciones pares. Relleno lateral `max(var(--margen), calc((100% - 1040px) / 2))`, con `--margen` de
  48 px en computador, 32 px en tableta y 20 px en celular.
- **Portada** (computador): rejilla `5fr 6fr`, alto `calc(100dvh - var(--alto-cabecera))`; texto y pie
  en la columna 1, foto en la columna 2 a toda la altura. Sin foto, el texto ocupa las dos columnas.
- **Editorial** (computador): rejilla `4fr 7fr`; encabezado en la columna 1; pendiente, cuerpo y firma
  en la columna 2.
- **`texto`** (computador y tableta): rejilla `7fr 5fr` sobre la sección, sin contenedores nuevos:
  encabezado (fila 1), pendiente (fila 2) y cuerpo (filas 3 y 4) en la columna 1; foto principal
  (filas 1 a 3) y fotos secundarias (fila 4) en la columna 2. Con `.seccion--invertida` las columnas se
  cambian. Sin fotos, una sola columna.
- **`texto`** (celular): en columna. `.fotos-par` pasa a ser una fila con desplazamiento horizontal y
  `scroll-snap-type: x mandatory`; cada foto ocupa el 80 % del ancho.
- **`cifras`:** `repeat(auto-fit, minmax(210px, 1fr))` en computador (da hasta 4), 2 columnas en
  tableta. En celular, una por fila con rejilla interna `5.5rem 1fr`: número a la izquierda.
- **`proyectos`:** `repeat(auto-fill, minmax(280px, 1fr))` en computador y tableta; cada ficha en
  columna, con la foto arriba en proporción 4:3. En celular, una por fila con la foto en 16:9.
- **`comparativo`** (computador): rejilla de 2 columnas sobre la sección; encabezado, pendiente y
  leyenda ocupan las dos.
- **`videos`:** 2 columnas en computador y tableta.
- **Texto:** el cuerpo no pasa de `70ch`. `.proyecto__meta` y `figcaption` suben a 12 px o más.
- **Borrador:** la marca BORRADOR y `.pendiente` se conservan.

- [ ] **Step 1: Escribir las pruebas que fallan**

Todas arman una edición con 4 cifras, 3 proyectos y una sección `texto` con 3 fotos seguida de otra
`texto` con 1.

```python
def test_en_computador_el_contenido_usa_el_ancho(navegador, carpeta_edicion, tmp_path):
    # 1440 px: main.boletin mide 1100 px o más de ancho
    # las 4 .cifra comparten la misma coordenada superior; las 3 .proyecto también
    # primera sección texto: .cuerpo termina antes de donde empieza .foto-principal
    # sección texto invertida: .foto-principal termina antes de donde empieza .cuerpo
    # portada: .portada__cuerpo termina antes de donde empieza .portada__foto
    # editorial: .encabezado termina antes de donde empieza .cuerpo

def test_en_tableta_van_de_dos_en_dos(navegador, carpeta_edicion, tmp_path):
    # 820 px: las cifras 1 y 2 comparten fila y la 3 baja; igual los proyectos

def test_en_celular_todo_va_en_una_columna(navegador, carpeta_edicion, tmp_path):
    # 390 px: documentElement.scrollWidth <= clientWidth
    # cada .cifra queda debajo de la anterior; dentro, .cifra__valor termina antes de .cifra__texto
    # cada .proyecto queda debajo del anterior
    # .fotos-par de la sección con 3 fotos: scrollWidth > clientWidth
    # ningún elemento con texto propio dentro de main tiene font-size menor de 12 px

def test_portada_sin_foto_no_se_descuadra(navegador, carpeta_edicion, tmp_path):
    # 1280 px, BORRADOR, sin portada.foto: .portada__cuerpo mide 400 px o más de ancho
    # y documentElement.scrollWidth <= clientWidth
```

- [ ] **Step 2: Verlas fallar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py -q`
Expected: fallan las 4 nuevas; las de la Tarea 1 pasan.

- [ ] **Step 3: Escribir el CSS según las decisiones de arriba**

- [ ] **Step 4: Verlas pasar y mirar el resultado**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py -q` → pasan todas, incluida
`test_la_impresion_no_cambia`.
Run: `BOLETIN_CHROMIUM=<ruta> uv run python salida/armar_local.py armar 2026-2` y capturar la vista
previa a 1440, 820 y 390 px. Comparar con la maqueta del spec §6.5 y corregir lo que se vea mal.

- [ ] **Step 5: Commit** — `feat(semestral): disposición del contenido para computador, tableta y celular`

---

### Task 4: Navegación sin JavaScript e índice del sitio

**Files:**
- Modify: `src/boletin_semestral/estaticos/estilo.css`
- Modify: `src/boletin_semestral/plantillas/indice.html.j2`
- Test: `tests/test_semestral_web.py`, `tests/test_semestral_sitio.py`

**Interfaces:**
- Consumes: `--alto-cabecera` y `--ancho-riel` (Tarea 3); `_cabecera.html.j2` (Tarea 2).
- Produces: el estado base que `riel.js` mejora. La clase `con-js` en `<html>` cambia la cabecera bajo
  1100 px.

**Decisiones de CSS** (dentro de `@media screen`):

- **Cabecera:** `position: sticky; top: 0`, por encima de la marca BORRADOR. Respeta
  `env(safe-area-inset-*)`.
- **Sin `con-js`,** en cualquier ancho: marca, volumen y «Descargar PDF». No se ven `.cabecera__actual`,
  `.cabecera__secciones` ni `.cabecera__avance`.
- **Con `con-js` y menos de 1100 px:** escudo, `.cabecera__actual`, `.cabecera__secciones` y
  `.cabecera__avance` (línea de 3 px bajo la barra). Se ocultan el título, el volumen y el PDF.
- **Lienzo** (1100 px o más): rejilla `minmax(0, 1fr) var(--ancho-riel)`. El riel es `sticky` bajo la
  cabecera, con alto `calc(100dvh - var(--alto-cabecera))` y borde izquierdo de `#DDE3EA`. Bajo
  1100 px el riel no se muestra.
- **Riel sin `riel--vivo`:** la lista alineada a la derecha, con el número en rojo y el nombre en
  Fredoka azul, filas de 32 px o más.
- **Foco:** todo enlace y botón de la navegación muestra un contorno con `:focus-visible`.
- **Anclas:** `html { scroll-padding-top: var(--alto-cabecera) }`. `scroll-behavior: smooth` solo con
  `prefers-reduced-motion: no-preference`. Así un enlace del índice funciona sin script.
- **Hoja:** `dialog.hoja` anclada abajo, ancho completo, alto máximo 84 %, esquinas superiores
  redondeadas y `::backdrop` oscurecido. Entra subiendo en 320 ms; sin animación con movimiento
  reducido. Filas de 48 px o más; `[aria-current]` resaltado.
- **Índice del sitio:** incluye `_cabecera.html.j2` sin `pdf` ni `partes`; sus bloques usan las mismas
  franjas y el mismo ancho máximo. No lleva riel, hoja ni `riel.js`.

- [ ] **Step 1: Escribir las pruebas que fallan**

```python
def test_sin_javascript_el_riel_es_una_lista_que_funciona(navegador, carpeta_edicion, tmp_path):
    # 1280 px, java_script_enabled=False
    # .riel mide 264 px de ancho y llega al borde derecho de la ventana
    # main.boletin termina donde empieza .riel
    # clic en .riel__lista a[href="#seccion-03"]: location.hash == "#seccion-03" y el borde superior
    # de #seccion-03 queda entre 0 y el alto de .cabecera + 4

def test_sin_javascript_la_cabecera_ofrece_el_pdf(navegador, carpeta_edicion, tmp_path):
    # 390 px, java_script_enabled=False
    # .cabecera__pdf visible y de 44 px de alto o más; .cabecera__secciones no visible

def test_la_cabecera_queda_fija(navegador, carpeta_edicion, tmp_path):
    # 1280 px: tras window.scrollTo(0, 2000), el borde superior de .cabecera es 0

def test_en_tableta_no_hay_riel(navegador, carpeta_edicion, tmp_path):
    # 820 px: .riel no es visible
```

En `tests/test_semestral_sitio.py`:

```python
def test_el_indice_del_sitio_lleva_la_cabecera(tmp_path):
    # tras publicar: index.html tiene .cabecera con .cabecera__titulo
    # y no tiene .riel, .hoja ni <script src="riel.js">
```

- [ ] **Step 2: Verlas fallar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py tests/test_semestral_sitio.py -q`
Expected: fallan las 5 nuevas.

- [ ] **Step 3: Escribir el CSS y ajustar `indice.html.j2`**

- [ ] **Step 4: Verlas pasar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest -q` → todo pasa, incluida `test_la_impresion_no_cambia`.

- [ ] **Step 5: Commit** — `feat(semestral): cabecera fija, riel como lista e índice del sitio`

---

### Task 5: Cabecera viva y hoja de secciones

**Files:**
- Modify: `src/boletin_semestral/estaticos/riel.js`
- Test: `tests/test_semestral_web.py`

**Interfaces:**
- Consumes: el marcado de la Tarea 2 y los estilos de la Tarea 4.
- Produces, dentro de `riel.js`:
  - `seccionActual() -> number` — índice de la última parte cuyo borde superior está a 35 % o menos del
    alto de la ventana, contado bajo la cabecera.
  - `marcarActual(i)` — pone `aria-current="true"` en el enlace `i` de `.riel__lista` y de
    `.hoja__lista`, y lo quita de los demás. La Tarea 6 la reutiliza.

**Comportamiento** (spec §6.2 y §6.3):

- Al cargar y en cada desplazamiento: escribe el número y el nombre de la parte actual en
  `.cabecera__num` y `.cabecera__nombre`, y pone el ancho de `.cabecera__avance i` en el porcentaje
  recorrido. Si la parte cambió, el nombre entra subiendo en 350 ms; sin animación con movimiento
  reducido.
- «Secciones» llama a `showModal()`. La hoja se cierra al elegir un enlace, con ✕, con Esc o al tocar
  el fondo. Al cerrarse, el foco vuelve al botón.
- Si el navegador no tiene `HTMLDialogElement.prototype.showModal`, el botón se oculta.
- El evento de desplazamiento es pasivo y el trabajo se agrupa en `requestAnimationFrame`.

- [ ] **Step 1: Escribir las pruebas que fallan** (todas a 390 px)

```python
def test_secciones_abre_la_hoja_y_lleva_a_la_seccion(navegador, carpeta_edicion, tmp_path):
    # .cabecera__secciones visible, de 44 × 44 px o más; al hacer clic, dialog.hoja tiene open
    # cada .hoja__lista a mide 48 px de alto o más
    # clic en a[href="#seccion-03"]: la hoja se cierra y #seccion-03 queda bajo la cabecera (± 4 px)
    # .cabecera__num == "03" y .cabecera__nombre == "Comunidades"
    # ese enlace de la hoja tiene aria-current="true" y es el único

def test_la_hoja_se_cierra_con_escape_y_devuelve_el_foco(navegador, carpeta_edicion, tmp_path):
    # tras Escape: sin open, y document.activeElement es .cabecera__secciones

def test_la_linea_de_avance_crece(navegador, carpeta_edicion, tmp_path):
    # arriba del todo: .cabecera__avance i mide 1 px o menos de ancho
    # abajo del todo: mide lo mismo que .cabecera (± 2 px)

def test_al_abrir_con_ancla_la_cabecera_dice_la_seccion(navegador, carpeta_edicion, tmp_path):
    # _abrir(..., ancla="#seccion-02"): .cabecera__nombre == "Planeta"

def test_sin_dialog_no_hay_boton(navegador, carpeta_edicion, tmp_path):
    # con add_init_script que borra HTMLDialogElement.prototype.showModal:
    # .cabecera__secciones no es visible y no hay errores
```

- [ ] **Step 2: Verlas fallar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py -q -k "hoja or avance or ancla or dialog"`
Expected: fallan las 5.

- [ ] **Step 3: Implementar la cabecera viva y la hoja en `riel.js`**

- [ ] **Step 4: Verlas pasar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest -q` → todo pasa.

- [ ] **Step 5: Commit** — `feat(semestral): cabecera con la sección actual y hoja de secciones`

---

### Task 6: El riel de letras

**Files:**
- Modify: `src/boletin_semestral/estaticos/riel.js`, `src/boletin_semestral/estaticos/estilo.css`
- Test: `tests/test_semestral_web.py`

**Interfaces:**
- Consumes: `marcarActual(i)` (Tarea 5); el riel como lista (Tarea 4).
- Produces, en el DOM, solo con 1100 px o más:
  - la clase `riel--vivo` en `.riel`;
  - `div.riel__capa[aria-hidden="true"]` con un `span.riel__letra[data-parte="k"]` por carácter visible
    de cada nombre. Las letras se crean una vez y no se reemplazan;
  - `span.riel__num`, `i.riel__linea`, `div.riel__regla` y `div.riel__marca`, todos con
    `aria-hidden="true"`;
  - los enlaces de `.riel__lista` siguen ahí, con su texto para el lector de pantalla pero sin
    pintarlo, colocados sobre su palabra como zona de clic y de foco.

**Punto de partida:** el script de la maqueta aprobada,
`.superpowers/brainstorm/52682-1794454587/content/combinacion-riel-v6.html`. Si esa carpeta no está, lo
que sigue y el §6.5 del spec bastan.

**Diferencias con la maqueta:**

- Se desplaza la ventana, no un contenedor. La posición de una sección es el borde superior de su
  rectángulo menos el del riel.
- Los nombres salen del texto de los enlaces y los números de `data-num`.
- El clic es la navegación normal del enlace: el script no desplaza.
- El título se parte por palabras llenando cada línea hasta 184 px; la maqueta ponía una palabra por
  línea.
- La amortiguación depende del tiempo, no del número de cuadros.

**Algoritmo.** Medidas en px, sobre letras dibujadas a 36 px que cada pose escala:

- Constantes: ancho útil del título 184; borde derecho del texto a 60 del borde del riel; eje de la
  palabra vertical a 41; tamaños 13 (listas), 19 (vertical) y hasta 36 (título); fila 18; margen
  superior 30 e inferior 26; alto de línea del título 38; alto del número 32; hueco 12; recorrido
  `TRAMO = 220`; desfase `ESCALON = 1.5`; constante de tiempo `TAU = 75` ms.
- Por parte `k`, de `n`: `yLeida = 30 + 18k`; `yProxima = altoRiel − 26 − 18(n − 1 − k)`;
  `yNum = 30 + 18k − 9 + 12`; `yTitulo = yNum + 32`.
- Avance: `P[0] = 1`; `P[k] = limitar((yTitulo[k] + 20 + TRAMO − arriba[k]) / TRAMO)`, con `arriba[k]`
  la posición de la sección. Con movimiento reducido, `P[k]` vale 1 si llega a 0,5 y 0 si no.
- Parte actual: la mayor `k` con `P[k] ≥ 0,5`. Se pasa a `marcarActual`. Con el riel vivo, la parte
  actual la decide esta regla; la del 35 % de la Tarea 5 queda para menos de 1100 px.
- Pose de cada letra de la parte `k`, con `sale = P[k + 1]` (0 en la última):
  1. si `sale > 0`: mezcla de **grande** a **leída** con `suave(limitar(2 · sale))`;
  2. si no, si `k = 0` o `P[k] = 1`: **grande**;
  3. si no, si `P[k] > 0` o la sección ya asoma (`arriba[k] < altoRiel − 30`) y no hay movimiento
     reducido: mezcla de **vertical** a **grande** con `t = limitar(P[k] · (1 + ESCALON) − ESCALON · orden)`,
     donde `orden` va de 0 en la última letra a 1 en la primera. La horizontal usa `fuera(t)`; la
     vertical, el giro, la escala y el color usan `suave(t)`;
  4. si no: **próxima**.
- Poses: **lista** (leída o próxima): alineada a la derecha, escala 13/36, gris. **Grande**: cada línea
  alineada a la derecha, escala `min(1, 184 / línea más ancha)`, azul. **Vertical**: sobre el eje, con
  la primera letra abajo, giro −90°, escala 19/36, celeste; cuelga 14 px bajo el borde de su sección.
- Curvas: `fuera(t) = 1 − (1 − t)³`; `suave(t)` es la cúbica de entrada y salida.
- Cada cuadro: `valor += (destino − valor) · (1 − e^(−dt / TAU))`. El ciclo se detiene cuando todas las
  letras llegaron. Con movimiento reducido el valor salta al destino.
- Las letras que ya llegaron se dibujan por encima de las que van en vuelo.
- Número y línea roja: opacidad 1 fuera de un paso; durante el paso, con `p` el avance en curso,
  `1 − p / 0,4` hasta 0,4, 0 hasta 0,75 y `(p − 0,75) / 0,25` después. Cambian de sitio mientras no se
  ven.
- Regla: su fondo se corre a la mitad de la velocidad de la página. La marca roja baja con el
  porcentaje leído y lo muestra.
- Un enlace bajo el cursor o con foco pone su palabra en azul.
- Se vuelve a medir cuando las fuentes terminan de cargar y cuando cambia el tamaño de la ventana. Al
  bajar de 1100 px se retiran la capa y `riel--vivo`; al volver a subir se crean de nuevo.

- [ ] **Step 1: Escribir las pruebas que fallan** (a 1280 px salvo que se diga)

El ángulo de una letra sale de su matriz calculada: `atan2(b, a)` en grados. Tras cada desplazamiento
se esperan 700 ms a que las letras se asienten.

```python
def test_el_riel_crea_una_letra_por_caracter(navegador, carpeta_edicion, tmp_path):
    # .riel tiene riel--vivo; hay tantas .riel__letra como caracteres sin espacios suman NOMBRES
    # .riel__capa tiene aria-hidden="true"; los 8 enlaces conservan su texto

def test_las_letras_son_las_mismas_al_desplazarse(navegador, carpeta_edicion, tmp_path):
    # guardar las letras en window.__letras; recorrer la página en 12 pasos
    # al final: todas siguen conectadas al documento y el total no cambió

def test_el_titulo_actual_va_horizontal_y_el_siguiente_vertical(navegador, carpeta_edicion, tmp_path):
    # con el borde de #seccion-03 al 80 % del alto de la ventana:
    # letras de la parte 3 (seccion-02): ángulo 0 ± 1; letras de la parte 4: ángulo −90 ± 1

def test_clic_en_el_riel_lleva_a_la_seccion(navegador, carpeta_edicion, tmp_path):
    # clic en .riel__lista a[href="#seccion-04"]: #seccion-04 queda bajo la cabecera (± 4 px)
    # y ese enlace tiene aria-current="true"

def test_al_abrir_con_ancla_el_riel_muestra_esa_seccion(navegador, carpeta_edicion, tmp_path):
    # _abrir(..., ancla="#seccion-03"): el enlace #seccion-03 del riel tiene aria-current="true"
    # y las letras de esa parte están a ángulo 0 ± 1

def test_con_movimiento_reducido_no_hay_letras_giradas(navegador, carpeta_edicion, tmp_path):
    # reduced_motion="reduce": en 12 posiciones de la página, toda letra está a ángulo 0 ± 1

def test_cruzar_1100_px_no_duplica_letras(navegador, carpeta_edicion, tmp_path):
    # contar letras; set_viewport_size a 800 de ancho: .riel no visible y 0 letras
    # de vuelta a 1280: el mismo número del principio; sin errores

def test_nombre_largo_no_se_sale_del_riel(navegador, carpeta_edicion, tmp_path):
    # etiqueta "Internacionalizacionesextraordinarias & <co>": estando en esa sección,
    # el rectángulo de cada letra suya queda dentro del de .riel (± 1 px); sin errores

def test_edicion_sin_secciones_no_falla(navegador, carpeta_edicion, tmp_path):
    # secciones = []: sin errores; hay len("Portada") + len("Editorial") letras
```

- [ ] **Step 2: Verlas fallar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest tests/test_semestral_web.py -q -k "riel or letras or titulo or reducido or 1100 or nombre_largo or sin_secciones"`
Expected: fallan las 9.

- [ ] **Step 3: Implementar el riel en `riel.js` y los estilos de `riel--vivo`**

- [ ] **Step 4: Verlas pasar**

Run: `BOLETIN_CHROMIUM=<ruta> uv run pytest -q` → todo pasa.

- [ ] **Step 5: Revisar el movimiento cuadro a cuadro**

Con la vista previa del Vol. 8, capturar el riel en 8 posiciones dentro del paso de tres partes:
«Cifras» (corta), «Emprendimiento» (larga) y «Prácticas empresariales» (dos líneas). En las tiras debe
verse:
- el título se arma de derecha a izquierda;
- ninguna letra en vuelo tapa a una que ya llegó;
- el título anterior ya está en la lista de arriba a mitad del paso;
- el número y la línea roja no se cruzan con las letras.

- [ ] **Step 6: Commit** — `feat(semestral): riel lateral con letras que viajan de vertical a horizontal`

---

### Task 7: Documentación y verificación final

**Files:**
- Modify: `docs/manual-boletin-semestral.md`, `README.md`

- [ ] **Step 1: Documentar**

- Manual, tras «Paso 4: la vista previa»: un párrafo que diga que la web lleva un índice de secciones y
  un botón «Descargar PDF», que salen solos, y que el trabajo del monitor no cambia.
- README, sección «Desarrollo»: enlazar el spec y este plan, y explicar `BOLETIN_CHROMIUM` en una
  línea.

- [ ] **Step 2: Comprobar que el PDF del Vol. 8 no cambió**

Run: `BOLETIN_CHROMIUM=<ruta> uv run python salida/armar_local.py armar 2026-2`
Expected: las mismas páginas, las mismas dos «secciones de más de una página» y los mismos 10
pendientes que en `salida/linea-base-armar.txt`.

- [ ] **Step 3: Correr todo**

Run: `set -o pipefail; uv run ruff format --check . && uv run ruff check . && BOLETIN_CHROMIUM=<ruta> uv run pytest -q`
Expected: sin errores; solo se saltan las 2 pruebas de PDF.
Run: `uv run pytest -q` → las de navegador se saltan y el resto pasa: así corre en GitHub.

- [ ] **Step 4: Revisión visual con el usuario**

Capturas del Vol. 8 a 1440, 820 y 390 px, y las tiras de la Tarea 6. El usuario prueba la vista previa
en su computador y en su celular (criterio 9 del spec).

- [ ] **Step 5: Commit** — `docs(semestral): la web responsiva en el manual y el README`

---

## Cobertura del spec

| Spec | Tarea |
|---|---|
| §4 tres tamaños de pantalla | 3, 4 |
| §5 cada parte del boletín y reglas comunes | 3 |
| §6.1 índice e identificadores | 2 |
| §6.2 cabecera | 2, 4, 5 |
| §6.3 hoja de secciones | 2, 4, 5 |
| §6.4 y §6.5 riel y efecto de las letras | 4, 6 |
| §7 accesibilidad y movimiento reducido | 2, 4, 5, 6 |
| §8 el PDF no cambia | 1 (línea base), y se comprueba en 2, 3, 4 y 7 |
| §9 arquitectura | 2 a 6 |
| §10 degradación | 4 (sin JavaScript), 5 (sin `<dialog>`), 6 (cambio de tamaño, nombre largo) |
| §11 pruebas | todas |
| §13 criterios 1 a 8 | 3, 6, 6, 3 y 5, 4, 6, 7, 7 · el criterio 9 (aprobación del usuario) cierra la Tarea 7 |
