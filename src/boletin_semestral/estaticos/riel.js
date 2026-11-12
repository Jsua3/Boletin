// Navegación del boletín: cabecera viva, hoja de secciones y riel de letras.
// Sin este script el boletín se lee completo y el índice sigue siendo una lista de enlaces.
(function () {
  "use strict";

  var raiz = document.documentElement;
  raiz.classList.add("con-js");

  var cabecera = document.querySelector(".cabecera");
  var riel = document.querySelector(".riel");
  var enlacesRiel = Array.prototype.slice.call(document.querySelectorAll(".riel__lista a"));
  var enlacesHoja = Array.prototype.slice.call(document.querySelectorAll(".hoja__lista a"));
  // Las partes del boletín salen del índice: cada enlace dice su sección, su número y su nombre.
  var partes = enlacesRiel.map(function (enlace) {
    return {
      seccion: document.getElementById(enlace.getAttribute("href").slice(1)),
      num: enlace.dataset.num || "",
      nombre: enlace.textContent,
    };
  });
  if (!cabecera || !riel || !partes.length) return;
  if (partes.some(function (parte) { return !parte.seccion; })) return;

  var reducir = window.matchMedia("(prefers-reduced-motion: reduce)");
  var enComputador = window.matchMedia("(min-width: 1100px)");
  var actual = -1;
  var vivo = null; // el riel de letras, mientras la ventana da para mostrarlo

  // Deja marcada la parte actual en las dos listas. Devuelve si cambió.
  function marcarActual(i) {
    if (i === actual) return false;
    actual = i;
    [enlacesRiel, enlacesHoja].forEach(function (lista) {
      lista.forEach(function (enlace, k) {
        if (k === i) enlace.setAttribute("aria-current", "true");
        else enlace.removeAttribute("aria-current");
      });
    });
    return true;
  }

  // ---------- Cabecera: la parte actual y el avance de la lectura ----------

  var rotulo = cabecera.querySelector(".cabecera__actual");
  var rotuloNum = cabecera.querySelector(".cabecera__num");
  var rotuloNombre = cabecera.querySelector(".cabecera__nombre");
  var avance = cabecera.querySelector(".cabecera__avance i");

  function leido() {
    var recorrido = raiz.scrollHeight - window.innerHeight;
    return recorrido > 0 ? Math.min(1, window.scrollY / recorrido) : 0;
  }

  // La última parte cuyo borde superior ya pasó del 35 % de la ventana, bajo la cabecera.
  function seccionActual() {
    var alto = cabecera.offsetHeight;
    var limite = alto + (window.innerHeight - alto) * 0.35;
    var i = 0;
    partes.forEach(function (parte, k) {
      if (parte.seccion.getBoundingClientRect().top <= limite) i = k;
    });
    return i;
  }

  function mostrarParte(i) {
    if (!marcarActual(i)) return;
    rotuloNum.textContent = partes[i].num;
    rotuloNombre.textContent = partes[i].nombre;
    if (reducir.matches) return;
    rotulo.classList.remove("cabecera__actual--entra");
    void rotulo.offsetWidth; // reinicia la animación de entrada
    rotulo.classList.add("cabecera__actual--entra");
  }

  // Con el riel vivo, la parte actual la decide el riel; si no, la regla del 35 %.
  function actualizar() {
    avance.style.width = leido() * 100 + "%";
    mostrarParte(vivo ? vivo.actualizar() : seccionActual());
  }

  var cuadroPedido = false;
  function alDesplazar() {
    if (cuadroPedido) return;
    cuadroPedido = true;
    requestAnimationFrame(function () {
      cuadroPedido = false;
      actualizar();
    });
  }

  // ---------- Riel de letras (computador) ----------
  // Cada letra de cada nombre es un elemento que nunca se reemplaza: solo cambia de sitio, de
  // giro, de tamaño y de color entre cuatro poses: próxima, vertical, actual y leída.

  // Medidas en px sobre letras dibujadas a BASE; cada pose las escala.
  var BASE = 36;
  var ANCHO_TITULO = 184; // ancho útil del título actual
  var DERECHA = 60; // del borde derecho del riel al borde del texto
  var EJE = 41; // del borde derecho del riel al eje de la palabra vertical
  var E_LISTA = 13 / BASE;
  var E_VERTICAL = 19 / BASE;
  var FILA = 18;
  var ARRIBA = 30;
  var ABAJO = 26;
  var ALTO_LINEA = 38;
  var ALTO_NUM = 32;
  var HUECO = 12;
  var TRAMO = 220; // px de desplazamiento que dura el paso de vertical a horizontal
  var ESCALON = 1.5; // cuánto se retrasa la primera letra respecto a la última
  var TAU = 75; // ms: constante de tiempo con la que cada letra alcanza su destino
  var GRIS = [163, 172, 183];
  var CELESTE = [143, 171, 207];
  var AZUL = [20, 61, 104];

  function limitar(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }
  function fuera(t) { return 1 - Math.pow(1 - t, 3); }
  function suave(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function mezcla(a, b, tx, ty, t) {
    return {
      x: a.x + (b.x - a.x) * tx,
      y: a.y + (b.y - a.y) * ty,
      giro: a.giro + (b.giro - a.giro) * t,
      escala: a.escala + (b.escala - a.escala) * t,
      color: a.color.map(function (v, i) { return v + (b.color[i] - v) * t; }),
    };
  }
  function nuevo(etiqueta, clase) {
    var el = document.createElement(etiqueta);
    el.className = clase;
    el.setAttribute("aria-hidden", "true");
    return el;
  }

  function crearRiel() {
    var capa = nuevo("div", "riel__capa");
    var numero = nuevo("span", "riel__num");
    var linea = nuevo("i", "riel__linea");
    var regla = nuevo("div", "riel__regla");
    var marca = nuevo("div", "riel__marca");
    var porcentaje = document.createElement("b");
    marca.appendChild(porcentaje);

    var palabras = partes.map(function (parte, k) {
      var palabra = { k: k, enlace: enlacesRiel[k], letras: [], visibles: [], encima: false };
      Array.from(parte.nombre).forEach(function (caracter) {
        if (!caracter.trim()) {
          palabra.letras.push({ espacio: true });
          return;
        }
        var letra = { el: document.createElement("span") };
        letra.el.className = "riel__letra";
        letra.el.dataset.parte = k;
        letra.el.textContent = caracter;
        capa.appendChild(letra.el);
        palabra.letras.push(letra);
        palabra.visibles.push(letra);
      });
      return palabra;
    });
    [capa, numero, linea, regla, marca].forEach(function (el) { riel.appendChild(el); });
    riel.classList.add("riel--vivo");

    var alto = 0;
    var xDerecha = 0;
    var xEje = 0;
    var pintado = -1;
    var pedido = 0;
    var antes = 0;

    function medir() {
      var espacio = BASE * 0.26;
      alto = riel.clientHeight;
      xDerecha = riel.clientWidth - DERECHA;
      xEje = riel.clientWidth - EJE;
      pintado = -1;
      palabras.forEach(function (p) {
        var x = 0;
        p.letras.forEach(function (l) {
          l.w = l.espacio ? espacio : l.el.offsetWidth;
          l.c = x + l.w / 2; // centro de la letra con el nombre en una sola línea
          x += l.w;
        });
        p.ancho = x;

        // El título se parte por palabras, llenando cada línea; si aun así no cabe, se achica.
        var anchos = [0];
        var fila = 0;
        var usado = 0;
        var grupo = [];
        function colocar() {
          if (!grupo.length) return;
          var w = grupo.reduce(function (suma, l) { return suma + l.w; }, 0);
          if (usado > 0 && usado + espacio + w > ANCHO_TITULO) {
            fila += 1;
            usado = 0;
          } else if (usado > 0) {
            usado += espacio;
          }
          grupo.forEach(function (l) {
            l.linea = fila;
            l.cl = usado + l.w / 2; // centro de la letra dentro de su línea
            usado += l.w;
          });
          anchos[fila] = usado;
          grupo = [];
        }
        p.letras.forEach(function (l) {
          if (l.espacio) colocar();
          else grupo.push(l);
        });
        colocar();

        p.anchos = anchos;
        p.escala = Math.min(1, ANCHO_TITULO / Math.max(1, Math.max.apply(null, anchos)));
        p.escalaLista = Math.min(E_LISTA, (xDerecha - 14) / Math.max(1, x));
        p.yLeida = ARRIBA + p.k * FILA;
        p.yProxima = alto - ABAJO - (palabras.length - 1 - p.k) * FILA;
        p.yNum = ARRIBA + p.k * FILA - FILA / 2 + HUECO;
        p.yTitulo = p.yNum + ALTO_NUM;
        p.altoTitulo = anchos.length * ALTO_LINEA * p.escala;
      });
    }

    // Las poses de una letra.
    function enLista(p, l, y) {
      var e = p.escalaLista;
      return { x: xDerecha - (p.ancho - l.c) * e, y: y, giro: 0, escala: e, color: p.encima ? AZUL : GRIS };
    }
    function grande(p, l) {
      var e = p.escala;
      return {
        x: xDerecha - (p.anchos[l.linea] - l.cl) * e,
        y: p.yTitulo + (l.linea + 0.5) * ALTO_LINEA * e,
        giro: 0,
        escala: e,
        color: AZUL,
      };
    }
    // Vertical: se lee de abajo arriba y cuelga del borde superior de su sección.
    function vertical(p, l, arriba) {
      return {
        x: xEje,
        y: arriba + 14 + (p.ancho - l.c) * E_VERTICAL,
        giro: -90,
        escala: E_VERTICAL,
        color: p.encima ? AZUL : CELESTE,
      };
    }

    // En un título de varias líneas, las letras de las líneas de arriba no pueden llegar desde
    // abajo: cruzarían la última línea, que se arma primero. Recorren un carril en escuadra,
    // a velocidad constante para no alcanzarse: suben por la orilla, doblan, corren por encima
    // de su línea y al final bajan a su puesto.
    function porArriba(a, b, t) {
      var alza = ALTO_LINEA * 0.8 * b.escala;
      var carril = b.y - alza;
      var tramoVertical = Math.abs(a.y - carril);
      var tramoHorizontal = Math.abs(a.x - b.x);
      var andado = limitar(t / 0.8) * (tramoVertical + tramoHorizontal);
      var enOrilla = andado < tramoVertical;
      var doblando = suave(limitar((andado - tramoVertical + 24) / 48));
      var letra = mezcla(a, b, 0, 0, doblando);
      letra.x = enOrilla ? a.x : a.x + (b.x > a.x ? 1 : -1) * (andado - tramoVertical);
      letra.y = enOrilla ? a.y + (carril > a.y ? 1 : -1) * andado : carril;
      letra.y += alza * suave(limitar((t - 0.8) / 0.2));
      return letra;
    }

    // El enlace real de cada parte queda sobre su palabra: es la zona de clic y de foco.
    function colocarEnlace(p, esActual, sube, arriba, leida) {
      var e = p.enlace.style;
      if (esActual) {
        e.left = xDerecha - ANCHO_TITULO + "px";
        e.width = ANCHO_TITULO + "px";
        e.top = p.yTitulo + "px";
        e.height = p.altoTitulo + "px";
      } else if (sube) {
        e.left = xEje - 14 + "px";
        e.width = "28px";
        e.top = arriba + 8 + "px";
        e.height = p.ancho * E_VERTICAL + 12 + "px";
      } else {
        e.left = "14px";
        e.width = xDerecha - 8 + "px";
        e.top = (leida ? p.yLeida : p.yProxima) - FILA / 2 + "px";
        e.height = FILA + "px";
      }
    }

    // Calcula a dónde debe ir cada letra según el desplazamiento. Devuelve la parte actual.
    function actualizarRiel() {
      var techo = riel.getBoundingClientRect().top;
      var arriba = partes.map(function (parte) {
        return parte.seccion.getBoundingClientRect().top - techo;
      });
      var quieto = reducir.matches;
      // Cuánto ha avanzado cada título de vertical (0) a horizontal (1).
      var avances = palabras.map(function (p, k) {
        if (k === 0) return 1;
        var v = limitar((p.yTitulo + 20 + TRAMO - arriba[k]) / TRAMO);
        return quieto ? (v >= 0.5 ? 1 : 0) : v;
      });
      var enCurso = 0;
      var enPaso = 1;
      avances.forEach(function (v, k) {
        if (v >= 0.5) enCurso = k;
        if (v > 0 && v < 1) enPaso = v;
      });

      palabras.forEach(function (p, k) {
        var sale = k + 1 < palabras.length ? avances[k + 1] : 0;
        var asoma = !quieto && arriba[k] < alto - 30;
        var sube = k > 0 && sale === 0 && avances[k] < 1 && (avances[k] > 0 || asoma);
        var ultima = p.visibles.length - 1;
        p.visibles.forEach(function (l, j) {
          l.capa = 1;
          if (sale > 0) {
            // El título saliente se encoge hacia la lista de arriba en la primera mitad del paso.
            var q = suave(limitar(sale * 2));
            l.destino = mezcla(grande(p, l), enLista(p, l, p.yLeida), q, q, q);
          } else if (k === 0 || avances[k] >= 1) {
            l.destino = grande(p, l);
            l.capa = 2;
          } else if (sube) {
            // La letra de más arriba, la última del nombre, sale primero. Cada una se corre a la
            // izquierda y después sube a su puesto: así llega desde abajo y no tapa a las demás.
            var orden = ultima > 0 ? (ultima - j) / ultima : 0;
            var t = limitar(avances[k] * (1 + ESCALON) - ESCALON * orden);
            var desde = vertical(p, l, arriba[k]);
            if (l.linea < p.anchos.length - 1) l.destino = porArriba(desde, grande(p, l), t);
            else l.destino = mezcla(desde, grande(p, l), fuera(t), suave(t), suave(t));
            if (t >= 1) l.capa = 2;
          } else {
            l.destino = enLista(p, l, p.yProxima);
          }
        });
        colocarEnlace(p, k === enCurso, sube, arriba[k], k < enCurso);
      });

      // El número y la línea se apagan durante el paso y vuelven en el sitio nuevo.
      var opacidad = 1;
      if (enPaso < 0.4) opacidad = 1 - enPaso / 0.4;
      else if (enPaso < 0.9) opacidad = 0;
      else if (enPaso < 1) opacidad = (enPaso - 0.9) / 0.1;
      numero.style.opacity = opacidad;
      linea.style.opacity = opacidad;
      if (enCurso !== pintado) {
        pintado = enCurso;
        numero.textContent = partes[enCurso].num;
        numero.style.top = palabras[enCurso].yNum + "px";
        linea.style.top = palabras[enCurso].yTitulo + palabras[enCurso].altoTitulo + 8 + "px";
      }

      var corrido = -window.scrollY * 0.5 + "px";
      regla.style.backgroundPosition = "right " + corrido + ", right " + corrido;
      marca.style.top = 20 + leido() * (alto - 60) + "px";
      porcentaje.textContent = Math.round(leido() * 100) + " %";

      if (!pedido) pedido = requestAnimationFrame(cuadro);
      return enCurso;
    }

    // Cada cuadro, las letras se acercan a su destino: por eso el movimiento es fluido y
    // termina un instante después de que la página se detiene.
    function cuadro(ahora) {
      pedido = 0;
      var dt = antes ? Math.min(64, ahora - antes) : 16;
      var paso = reducir.matches ? 1 : 1 - Math.exp(-dt / TAU);
      var sigue = false;
      antes = ahora;
      palabras.forEach(function (p) {
        p.visibles.forEach(function (l) {
          var d = l.destino;
          var a = l.actual;
          if (!a) {
            a = { x: d.x, y: d.y, giro: d.giro, escala: d.escala, color: d.color.slice() };
            l.actual = a;
          }
          ["x", "y", "giro", "escala"].forEach(function (c) {
            var falta = d[c] - a[c];
            if (Math.abs(falta) > (c === "escala" ? 0.002 : 0.15)) {
              a[c] += falta * paso;
              sigue = true;
            } else {
              a[c] = d[c];
            }
          });
          for (var i = 0; i < 3; i += 1) {
            var tono = d.color[i] - a.color[i];
            if (Math.abs(tono) > 1) {
              a.color[i] += tono * paso;
              sigue = true;
            } else {
              a.color[i] = d.color[i];
            }
          }
          if (l.capaPuesta !== l.capa) {
            l.el.style.zIndex = l.capa; // las que ya llegaron van por encima de las que vuelan
            l.capaPuesta = l.capa;
          }
          l.el.style.transform =
            "translate3d(" + a.x.toFixed(2) + "px," + a.y.toFixed(2) + "px,0) translate(-50%,-50%) " +
            "rotate(" + a.giro.toFixed(2) + "deg) scale(" + a.escala.toFixed(3) + ")";
          l.el.style.color =
            "rgb(" + Math.round(a.color[0]) + "," + Math.round(a.color[1]) + "," + Math.round(a.color[2]) + ")";
        });
      });
      if (sigue) pedido = requestAnimationFrame(cuadro);
      else antes = 0;
    }

    medir();
    return {
      actualizar: actualizarRiel,
      medir: medir,
      resaltar: function (k, si) {
        palabras[k].encima = si;
        actualizarRiel();
      },
      quitar: function () {
        if (pedido) cancelAnimationFrame(pedido);
        [capa, numero, linea, regla, marca].forEach(function (el) { el.remove(); });
        riel.classList.remove("riel--vivo");
        enlacesRiel.forEach(function (enlace) { enlace.removeAttribute("style"); });
      },
    };
  }

  // El riel de letras existe solo con 1100 px o más; al cambiar la ventana se vuelve a medir.
  function ajustarRiel() {
    if (enComputador.matches && !vivo) {
      vivo = crearRiel();
    } else if (!enComputador.matches && vivo) {
      vivo.quitar();
      vivo = null;
    } else if (vivo) {
      vivo.medir();
    }
    actualizar();
  }

  // Un enlace bajo el cursor o con el foco del teclado pone su palabra en azul.
  enlacesRiel.forEach(function (enlace, k) {
    ["mouseenter", "focus"].forEach(function (evento) {
      enlace.addEventListener(evento, function () { if (vivo) vivo.resaltar(k, true); });
    });
    ["mouseleave", "blur"].forEach(function (evento) {
      enlace.addEventListener(evento, function () { if (vivo) vivo.resaltar(k, false); });
    });
  });

  window.addEventListener("scroll", alDesplazar, { passive: true });
  window.addEventListener("resize", ajustarRiel);
  window.addEventListener("load", ajustarRiel);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(ajustarRiel);
  ajustarRiel();

  // ---------- Hoja de secciones (tableta y celular) ----------

  var hoja = document.querySelector("dialog.hoja");
  var botonSecciones = cabecera.querySelector(".cabecera__secciones");
  if (hoja && botonSecciones && typeof hoja.showModal === "function") {
    botonSecciones.addEventListener("click", function () { hoja.showModal(); });
    hoja.querySelector(".hoja__cerrar").addEventListener("click", function () { hoja.close(); });
    enlacesHoja.forEach(function (enlace) {
      enlace.addEventListener("click", function () { hoja.close(); });
    });
    // Un toque fuera de la hoja cae sobre el fondo oscurecido, que es del propio <dialog>.
    hoja.addEventListener("click", function (evento) {
      var caja = hoja.getBoundingClientRect();
      var fuera = evento.clientY < caja.top || evento.clientX < caja.left || evento.clientX > caja.right;
      if (evento.target === hoja && fuera) hoja.close();
    });
  } else {
    raiz.classList.add("sin-hoja");
  }
})();
