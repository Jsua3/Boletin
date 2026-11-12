# Diseño — Web responsiva del boletín semestral

**Proyecto:** Boletín «Proyección Social EN ACCIÓN» · Facultad de Ingenierías y Ciencias Básicas
**Fecha:** 11 de noviembre de 2026
**Estado:** dirección aprobada con maquetas; pendiente de revisión de este documento y de plan de
implementación

Este documento reemplaza el apartado «Web» del §8 de
`docs/superpowers/specs/2026-11-11-boletin-semestral-design.md`. Todo lo demás de ese diseño sigue
vigente.

---

## 1. Propósito

La web del boletín es hoy una columna de 728 px. Eso produce tres problemas:

- **En el computador se desperdicia la pantalla.** A 1440 px queda vacía casi la mitad: unos 356 px a
  cada lado.
- **Se recorre mal.** La página mide unos 10.100 px, cerca de 11 pantallas, sin índice ni forma de
  saltar a una sección. Tampoco hay un enlace al PDF dentro del boletín.
- **En el celular hay detalles incómodos.** El texto usa 314 de 390 px, las cifras van en dos
  columnas de 140 px, la línea de docentes sale a 11 px y no hay nada que tocar para navegar.

**Qué se quiere.** Que el boletín se lea con la misma comodidad en computador y en celular: que use
el ancho disponible, que siempre se sepa en qué sección se está y que se pueda saltar a cualquiera,
con el dedo o con el ratón.

Los lectores llegan desde los dos tipos de pantalla por igual.

## 2. Lo acordado y lo supuesto

**Dicho por el usuario**

| Tema | Decisión |
|---|---|
| Pantallas | Computador y celular importan por igual |
| Computador | Combinar la «revista a todo el ancho» con un índice siempre visible |
| Índice | A la derecha, con el efecto de https://getartcraft.com/: las secciones cambian según el punto de desplazamiento |
| Letras del índice | Son las mismas en todo el recorrido: cada letra cambia de sitio y de dirección para pasar de la palabra vertical al título horizontal |
| Celular | Cómodo para el uso táctil |
| Orden | Esto se hace antes de escribirle a la Coordinación |

**Supuesto y confirmado al presentar el diseño**

- El PDF no cambia.
- `edicion.toml` no cambia: los monitores llenan lo mismo.
- Se mantiene la dirección visual B: colores del escudo, título azul con la palabra manuscrita roja y
  las fuentes Fredoka, Kaushan Script e Inter.
- El índice `/semestral/` solo se ajusta para que combine.

**Éxito:** el Vol. 8 se lee en un portátil sin espacios vacíos y con el índice a la vista; en un
celular, sin hacer zoom y con todas las secciones a dos toques; y su PDF sale idéntico al de hoy.

## 3. Alcance

### Dentro

- Disposición nueva de la página del boletín para tres tamaños de pantalla.
- Navegación: barra superior, riel lateral animado en computador y hoja de secciones en celular.
- Enlace «Descargar PDF» dentro del boletín.
- Ajuste del índice `/semestral/` para que use el mismo ancho y la misma barra.
- Pruebas, y una nota en el manual.

### Fuera

- Cambios al PDF o a su diseño.
- Campos nuevos en `edicion.toml`.
- Ampliar una foto al tocarla.
- Modo oscuro.
- Pasar de una sección a otra deslizando a los lados.
- Cualquier biblioteca de JavaScript o recurso cargado de internet.

## 4. Tres tamaños de pantalla

| Pantalla | Ancho | Navegación | Contenido |
|---|---|---|---|
| Computador | 1100 px o más | Barra superior con la marca y «Descargar PDF». Riel de 264 px a la derecha | Repartido a lo ancho (§5) |
| Tableta o ventana angosta | 700 a 1099 px | Barra superior con la sección actual, línea de avance y botón «Secciones». Sin riel | A dos columnas donde quepa |
| Celular | menos de 700 px | La misma barra de la tableta | Una columna a todo el ancho |

- El contenido tiene un ancho máximo cercano a 1040 px dentro de su columna. Los fondos de las
  secciones llegan hasta los bordes.
- Las secciones dejan de verse como hojas apiladas con sombra: son franjas que alternan fondo blanco
  y fondo azul muy claro (`#f3f6fa`).
- La barra superior queda fija al desplazarse. En celulares con muesca respeta las zonas seguras.

## 5. Cada parte del boletín

| Parte | Computador | Tableta | Celular |
|---|---|---|---|
| Portada | Partida: texto a la izquierda, foto a la derecha, a la altura de la pantalla | Igual que el celular | Foto arriba, texto abajo |
| Editorial | Título a la izquierda, texto a la derecha | Apilado | Apilado |
| `texto` | Bajo el encabezado, texto y fotos lado a lado; el lado de las fotos alterna de una sección a la siguiente | Igual que el computador | Foto principal, texto y fotos secundarias deslizables |
| `cifras` | Hasta 4 por fila | 2 por fila | Una por fila: número grande a la izquierda, texto a la derecha |
| `proyectos` | Tarjetas de 3 en 3 | De 2 en 2 | Apiladas, con la foto arriba |
| `comparativo` | Grupos en 2 columnas | 1 columna | 1 columna |
| `videos` | 2 por fila | 2 por fila | 1 por fila |
| `imagen` | A todo el ancho del contenido | Igual | Igual |
| Contraportada | Franja azul a todo el ancho | Igual | Igual |

**Reglas comunes**

- El texto de lectura no pasa de unos 70 caracteres por línea.
- Ningún texto baja de 12 px. El cuerpo se queda en 16 px o más.
- Todo lo que se toca mide al menos 44 × 44 px.
- En el celular, las fotos secundarias de una sección `texto` van en una fila que se desliza a los
  lados, con ajuste a cada foto. La segunda foto asoma para que se note que hay más.
- La marca BORRADOR y los recuadros de pendientes se mantienen en los tres tamaños.
- Una sección `proyectos` sin fotos muestra tarjetas de solo texto, como hoy.

## 6. Navegación

### 6.1 El índice, base de todo

El HTML lleva una lista ordenada de enlaces, uno por cada parte: Portada, Editorial y cada sección.
La contraportada no entra.

- Cada parte tiene un identificador fijo: `portada`, `editorial`, `seccion-01`, `seccion-02`, …
- El nombre de cada sección en el índice es su `etiqueta`, con su número. No hay campo nuevo.
- La misma lista se usa dos veces: en el riel del computador y en la hoja del celular.

**Sin JavaScript** el boletín se lee completo. En el computador el riel queda como una lista fija de
enlaces que funcionan. En el celular no aparece el botón «Secciones».

### 6.2 Barra superior

- **Computador:** escudo, «Proyección *Social*», «Vol. N · fecha» y el botón «Descargar PDF».
- **Tableta y celular:** escudo, número y nombre de la sección actual, y el botón «Secciones». Debajo,
  una línea roja de 3 px que crece con el avance de la lectura. Al cambiar de sección, el nombre
  nuevo entra subiendo en unos 350 ms.

### 6.3 Hoja de secciones (tableta y celular)

- «Secciones» abre una hoja que sube desde abajo, sobre un fondo oscurecido.
- Usa el elemento `<dialog>` del navegador: atrapa el foco, se cierra con Esc y devuelve el foco al
  botón.
- Contiene el índice, con filas de al menos 48 px de alto y la sección actual resaltada, y el botón
  «Descargar PDF».
- Se cierra al elegir una sección, al tocar la ✕ o al tocar el fondo.

### 6.4 Riel lateral (computador)

El riel ocupa 264 px a la derecha, fijo bajo la barra y a toda la altura de la pantalla. Muestra, de
arriba abajo:

1. **Las secciones ya leídas**, en gris, a 13 px.
2. **La sección actual**: su número en letra manuscrita roja (30 px), su nombre en Fredoka azul (hasta
   36 px) y una línea roja corta debajo.
3. **Las secciones que faltan**, en gris, ancladas abajo.
4. **En la orilla derecha**, una regla de marcas que se mueve con la página y una marca roja con el
   porcentaje leído.

Un clic en cualquier nombre lleva a esa sección. Al pasar el cursor, el nombre se pone azul.

### 6.5 El efecto de las letras

Cada letra de cada nombre es un elemento propio que nunca se reemplaza: solo cambia de posición, de
giro, de tamaño y de color. Un nombre pasa por cuatro poses.

| Pose | Cuándo | Cómo se ve |
|---|---|---|
| Próxima | Su sección aún no asoma | En la lista de abajo, 13 px, gris |
| Vertical | El borde superior de su sección ya está en pantalla | En la orilla del riel, girada −90° (se lee de abajo arriba), 19 px, azul claro. Cuelga del borde de su sección y sube con él |
| Actual | Su sección es la que se lee | Horizontal, hasta 36 px, azul |
| Leída | Empezó el paso de la sección siguiente | En la lista de arriba, 13 px, gris |

**El paso de vertical a actual**

- Lo gobierna el desplazamiento: dura 220 px de recorrido y termina cuando el borde de la sección
  llega a la altura del título.
- Las letras se sueltan una por una, empezando por la de más arriba, que es la última del nombre. El
  título se arma de derecha a izquierda.
- Cada letra gira de −90° a 0°, crece y se mueve por una curva: primero se corre a la izquierda y
  después sube a su puesto. Así llega desde abajo y no pasa por encima de las que ya llegaron.
- El desfase entre letras es amplio: en cada momento hay pocas letras en el aire.
- El movimiento va amortiguado. Cada letra se acerca a su destino con una constante de tiempo cercana
  a 75 ms, así que termina de acomodarse un instante después de que la página se detiene.

**Lo que pasa alrededor**

- El título saliente se encoge, con sus mismas letras, hasta su fila en la lista de arriba. Lo hace
  durante la primera mitad del paso.
- El número manuscrito y la línea roja se apagan en el primer 40 % del paso y reaparecen, ya en su
  sitio nuevo, en el último 10 %.
- Un nombre que no cabe en el ancho del riel se parte en líneas por palabras y, si hace falta, se
  achica. Es el caso de «Prácticas empresariales» y «Aprendizaje con impacto».
- Las letras en vuelo se dibujan por detrás de las que ya llegaron.
- En un título de varias líneas se arma primero la última línea. Las letras de las líneas de
  arriba no llegan desde abajo, porque la cruzarían: suben en fila por la orilla, doblan, corren
  por encima de su línea y bajan a su puesto.

**Parámetros de partida**, tomados de la maqueta aprobada. Se pueden afinar al construir:

| Parámetro | Valor |
|---|---|
| Ancho del riel | 264 px |
| Ancho útil del título | 184 px |
| Tamaños: lista, vertical, título | 13, 19 y hasta 36 px |
| Alto de fila de las listas | 18 px |
| Recorrido del paso | 220 px |
| Desfase entre la primera y la última letra | 1,5 veces la duración de una letra |
| Curvas | horizontal: salida rápida; vertical, giro y tamaño: entrada y salida suaves |
| Colores | gris `#a3acb7`, azul claro `#8fabcf`, azul `#143D68`, rojo `#BD1822` |

**Maqueta de referencia:** `.superpowers/brainstorm/52682-1794454587/content/combinacion-riel-v6.html`.
Esa carpeta no entra al repositorio; este apartado es la descripción que cuenta.

## 7. Accesibilidad y movimiento

- Las letras animadas son decoración y van ocultas para el lector de pantalla. La navegación real son
  los enlaces del índice, que conservan su nombre accesible y reciben el foco del teclado.
- El enlace de la sección actual lleva `aria-current`.
- El foco del teclado siempre se ve.
- Con «reducir movimiento» activo en el equipo:
  - no hay pose vertical ni vuelo de letras: el título cambia de golpe a mitad del paso;
  - el salto a una sección es inmediato, sin desplazamiento animado;
  - la hoja y el nombre de la barra cambian sin transición.
- Los colores de texto mantienen el contraste actual. Los grises del riel solo se usan en nombres que
  además son enlaces y tienen su versión resaltada.

## 8. El PDF no cambia

- Todas las reglas nuevas de disposición van dentro de `@media screen`.
- La barra, el riel y la hoja llevan la clase `solo-pantalla`, que ya los oculta al imprimir.
- Si hace falta agregar contenedores al HTML, no pueden cambiar cómo fluye el contenido al imprimir.

**Cómo se comprueba.** Con el Vol. 8, antes y después del cambio:

1. `armar` informa las mismas páginas y las mismas «secciones de más de una página».
2. Una captura de página completa en modo impresión, al ancho que usa `pdf.py`, sale igual.

## 9. Arquitectura

| Archivo | Cambio |
|---|---|
| `plantillas/boletin.html.j2` | Barra superior, identificadores de cada parte, índice, hoja de secciones y el script nuevo |
| `plantillas/_*.html.j2` | Contenedores para repartir el contenido, solo donde el CSS no alcance |
| `plantillas/indice.html.j2` | El mismo ancho y la barra superior solo con la marca; sin riel ni hoja |
| `estaticos/estilo.css` | Disposición por tamaño de pantalla, barra, riel y hoja. Lo de impresión no se toca |
| `estaticos/riel.js` | Nuevo: riel, barra y hoja. JavaScript propio, sin dependencias |
| `render.py` | Pasa a la plantilla la lista de partes y el nombre del PDF; `copiar_estaticos` copia `riel.js` |
| `armado.py` | Toma el nombre del PDF del mismo sitio que `render.py`, para que el enlace y el archivo coincidan |
| `docs/manual-boletin-semestral.md` | Una nota: la web tiene índice y botón de PDF; el trabajo del monitor no cambia |

- `movimiento.js`, que hace aparecer las cifras, se conserva.
- El nombre del PDF se calcula en un solo lugar: `boletin-vol-N.pdf` o `boletin-vol-N-borrador.pdf`.
- Cada edición publicada sigue siendo autosuficiente: lleva su copia de los estilos y de los scripts.

**Cómo trabaja `riel.js`**

1. Al cargar, y cuando las fuentes están listas, crea una letra por carácter de cada nombre y mide su
   ancho.
2. En cada evento de desplazamiento calcula, para cada letra, su pose de destino.
3. Un ciclo de animación acerca cada letra a su destino y se detiene cuando todas llegaron.
4. Solo cambia `transform`, `opacity` y `color`. El evento de desplazamiento es pasivo.
5. Vuelve a medir si cambia el tamaño de la ventana.
6. Bajo 1100 px no crea las letras: solo atiende la barra y la hoja.

## 10. Degradación

| Situación | Comportamiento |
|---|---|
| Sin JavaScript | El boletín se lee completo. Riel como lista de enlaces en computador; sin botón «Secciones» en celular |
| Navegador sin `<dialog>` | No aparece el botón «Secciones»; el resto funciona |
| «Reducir movimiento» | Cambios de golpe (§7) |
| Edición sin PDF junto al HTML | No pasa: `armar` siempre genera el PDF antes de dejar la carpeta en su sitio |
| Nombre muy largo en el riel | Se parte en líneas y se achica; nunca se sale del riel |
| Ventana que cambia de tamaño | El riel aparece o desaparece al cruzar 1100 px, sin recargar |
| Falla `riel.js` | El contenido no depende de él: queda la lista de enlaces |

## 11. Pruebas

Primero la prueba, luego el código. Todas corren sin red.

- **Render**
  - El índice trae un enlace por cada parte, en orden, y cada enlace apunta a un identificador que
    existe y es único.
  - El nombre de cada sección en el índice es su etiqueta, escapada.
  - El enlace «Descargar PDF» apunta a `boletin-vol-N-borrador.pdf` en borrador y a
    `boletin-vol-N.pdf` en la edición final.
  - La barra, el riel y la hoja llevan `solo-pantalla`.
  - Las pruebas actuales de render siguen pasando.
- **Armado**
  - `riel.js` queda junto al HTML, en la vista previa y en `publicada/`.
  - El PDF que se genera se llama como dice el enlace.
- **Sitio:** el índice `/semestral/` sigue listando ediciones y enlazando sus PDF.
- **Navegador**, una prueba de humo que se salta sin Chromium, como las de PDF:
  - la página abre sin errores de consola;
  - a 1280 px, un clic en un nombre del riel lleva a esa sección;
  - a 390 px, «Secciones» abre la hoja y elegir una sección la cierra y lleva a ella.
- **Revisión visual**, fuera de `pytest`:
  - capturas a 1440, 820 y 390 px;
  - la transición del riel cuadro a cuadro en un nombre corto, uno largo y uno de varias líneas;
  - la comparación de impresión del §8.

## 12. Riesgos y preguntas abiertas

| Tema | Estado |
|---|---|
| Letras de un título de varias líneas | Resuelto al construir: llegan por encima de su línea (§6.5) |
| Chromium 1254 sin instalar | La prueba de navegador y las de PDF se saltan. Se verifica con `chromium_headless_shell-1234` y el parche temporal, como hasta ahora |
| Rendimiento | Unas 150 letras con `transform`. Probar en un portátil modesto y en un celular real |
| Fecha | El Vol. 8 sale en diciembre de 2026. Si el efecto de letras se atrasa, lo demás puede publicarse con el riel como lista de enlaces |
| Mónica no ha visto esta dirección | Mostrarle la vista previa del Vol. 8 cuando esté construida |

## 13. Criterios de aceptación

1. A 1440 px el Vol. 8 usa el ancho de la pantalla, con el contenido repartido como dice el §5 y el
   riel a la derecha.
2. Al desplazarse, cada nombre del riel pasa de vertical a horizontal con sus mismas letras, como en
   la maqueta aprobada.
3. Un clic en cualquier nombre del riel lleva a su sección.
4. A 390 px no hay desplazamiento horizontal de la página, el texto se lee sin zoom y cualquier
   sección queda a dos toques.
5. Con JavaScript apagado el boletín se lee completo y los enlaces del índice funcionan.
6. Con «reducir movimiento» no hay letras en vuelo.
7. El PDF del Vol. 8 tiene las mismas páginas que antes del cambio y su captura de impresión es igual.
8. `uv run ruff format --check .`, `uv run ruff check .` y `uv run pytest` pasan.
9. El usuario aprueba la vista previa del Vol. 8 en computador y en celular.
