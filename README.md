# Boletín semestral «Proyección Social EN ACCIÓN»

Programa que arma, cada semestre, el boletín de proyección social de la **Facultad de Ingenierías y
Ciencias Básicas** de la Corporación Universitaria Empresarial Alexander von Humboldt (Armenia,
Quindío).

Cada edición es un archivo de texto, `datos/semestral/<semestre>/edicion.toml`, del que salen dos
cosas con el mismo diseño:

- una **página web**, publicada en https://jsua3.github.io/Boletin/;
- un **PDF**, que se sube a Heyzine como las ediciones anteriores.

Lo que falta en una edición aparece en rojo como **pendiente** en la vista previa, y una edición con
pendientes no se puede publicar: el programa nunca inventa datos.

## Uso

Instalación, una sola vez por computador:

```bash
uv sync
uv run playwright install chromium   # el navegador con el que se imprime el PDF
```

Cada semestre:

```bash
uv run semestral nueva 2026-2      # crea la edición con la estructura de la anterior
uv run semestral armar 2026-2      # vista previa (borrador) o edición publicada (aprobada)
uv run semestral borrador 2026-2 --correo correo.txt   # opcional: Claude propone textos aparte
```

El paso a paso para monitores y para la Coordinación está en
[`docs/manual-boletin-semestral.md`](docs/manual-boletin-semestral.md).

## Cómo se publica

`semestral armar` sobre una edición aprobada deja en `datos/semestral/<semestre>/publicada/` la web,
el PDF y las fotos: lo que se aprueba es exactamente lo que se publica. Al subir a `main`, el flujo
`sitio.yml` copia esas carpetas a GitHub Pages y arma el índice. No genera PDFs ni instala un
navegador: los borradores nunca llegan al sitio.

## Estado

- **Vol. 8 (2026-2): en borrador**, armado con el correo de la Coordinación del 6 de noviembre de
  2026. Le faltan 10 datos; `semestral armar 2026-2` los lista.
- El Vol. 7 (junio de 2026) y los anteriores se hicieron fuera del programa; el índice enlaza el Vol. 7
  en Heyzine (`datos/semestral/anteriores.toml`).

**El repositorio y el sitio son públicos.** Solo entran las fotos que la Coordinación entrega para el
boletín; la Coordinación responde por la autorización de uso, como en las ediciones anteriores.

## Desarrollo

```bash
uv run pytest            # las pruebas de PDF y de navegador se saltan si no está Chromium
uv run ruff check . && uv run ruff format --check .
```

- Diseño: `docs/superpowers/specs/2026-11-11-boletin-semestral-design.md`
- Plan de implementación: `docs/superpowers/plans/2026-11-11-boletin-semestral.md`
- Web responsiva (riel de secciones, cabecera y hoja): diseño en
  `docs/superpowers/specs/2026-11-11-web-responsiva-design.md` y plan en
  `docs/superpowers/plans/2026-11-12-web-responsiva.md`
- Análisis del Vol. 7: `docs/02-analisis-boletin-anterior.md`

Las pruebas de navegador (`tests/test_semestral_web.py`) usan el Chromium de Playwright. Si no
está instalado, la variable `BOLETIN_CHROMIUM` puede apuntar a otro ejecutable de Chromium.

Este programa nació en `Jsua3/proy_social_proyectos`, junto al boletín de empleos, y se mudó aquí el
12 de noviembre de 2026.
