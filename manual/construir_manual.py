#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Genera manual/index.html a partir de manual/fuente-manual.txt.

La fuente es el unico archivo que se edita a mano. Para regenerar:
    python manual/construir_manual.py
Opciones: --fuente RUTA, --salida RUTA, --verificar

Directivas de la fuente, una por linea, con la forma "CLAVE: valor".
Cabecera: TITULO, LEDE, TAGS (separadas por |), ACTUALIZADO.
Menu: NAVGRUPO: etiqueta / NAV: ancla | etiqueta | palabras [| sub].
Estructura: DIVISOR, SECCION: ancla [| clase], KICKER, H2, INTRO,
H3: titulo | ancla.
Contenido: P, NOTA, CAP, LISTA (lineas "- "), STEPPER (pasos con >),
SHOT: archivo | alt | url, MARCAS: 1:izq,arriba | 2:izq,arriba,
PASO: titulo | texto, TABLA (lineas con |), CARRUSEL: id, SLIDE: etiqueta | url,
GCAT, TERMINO: nombre [-> seccion] | definicion, FCAT, PREGUNTA: p | r,
CONTACTO: texto | url, FINCONTACTO.
En el texto se admite negrita con dobles asteriscos, codigo con comillas
invertidas y enlaces con corchetes y parentesis.
"""
import argparse
import html
import os
import re
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.abspath(__file__))

# Cloudflare (Scrape Shield) ofusca los correos y solo se reconstruyen con JS.
# Estos comentarios lo desactivan para que el texto quede en el HTML servido.
EMAIL_OFF_INI = "<!--email_off-->"
EMAIL_OFF_FIN = "<!--/email_off-->"

ERRORES = []


def error(msg):
    ERRORES.append(msg)


def parcial(nombre):
    """Lee un fragmento HTML reutilizable de manual/parciales (logotipo, lupa)."""
    ruta = os.path.join(RAIZ, "parciales", nombre)
    try:
        with open(ruta, encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def esc(t):
    return html.escape(t, quote=False)


def ancla(texto, usadas=None):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60] or "seccion"
    if usadas is not None:
        base, n = t, 2
        while t in usadas:
            t = "%s-%d" % (base, n)
            n += 1
        usadas.add(t)
    return t


def inline(t):
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               lambda m: '<a href="%s">%s</a>'
               % (html.escape(html.unescape(m.group(2)), quote=True), m.group(1)), t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t


def partes(valor, n=None):
    p = [x.strip() for x in valor.split("|")]
    if n:
        p += [""] * (n - len(p))
        p = p[:n]
    return p


def leer(ruta):
    doc = {"meta": {}, "nav": [], "bloques": []}
    grupo = None
    with open(ruta, encoding="utf-8") as fh:
        lineas = fh.read().splitlines()
    i = 0
    pendiente = None
    while i < len(lineas):
        linea = lineas[i].strip()
        i += 1
        if pendiente:
            es_lista = pendiente["tipo"] == "lista" and linea.startswith("- ")
            es_tabla = pendiente["tipo"] == "tabla" and linea.startswith("|")
            if es_lista or es_tabla:
                pendiente["filas"].append(linea[2:].strip() if es_lista else linea)
                continue
            doc["bloques"].append(pendiente)
            pendiente = None
        if not linea or linea.startswith("#"):
            continue
        m = re.match(r"^([A-Z0-9_]+):\s*(.*)$", linea)
        if not m:
            error("Linea %d sin directiva: %r" % (i, linea[:70]))
            continue
        clave, valor = m.group(1), m.group(2).strip()
        if clave in ("TITULO", "LEDE", "TAGS", "ACTUALIZADO"):
            doc["meta"][clave] = valor
        elif clave == "NAVGRUPO":
            grupo = {"etiqueta": valor, "items": []}
            doc["nav"].append(grupo)
        elif clave == "NAV":
            anc, etiqueta, claves, sub = partes(valor, 4)
            if grupo is None:
                grupo = {"etiqueta": "", "items": []}
                doc["nav"].append(grupo)
            grupo["items"].append({"ancla": anc, "etiqueta": etiqueta,
                                   "claves": claves, "sub": sub == "sub"})
        elif clave in ("LISTA", "TABLA"):
            pendiente = {"tipo": clave.lower(), "filas": []}
        else:
            doc["bloques"].append({"tipo": clave.lower(), "valor": valor})
    if pendiente:
        doc["bloques"].append(pendiente)
    return doc


class Render:
    def __init__(self, doc):
        self.doc = doc
        self.out = []
        self.usadas = set()
        self.nivel = 2
        self.en_seccion = False
        self.en_carrusel = False
        self.en_slide = False
        self.pasos_abiertos = False
        self.paso_n = 0
        self.en_dl = False
        self.en_contacto = False
        self.shot_valor = None
        self.pos_figura = None
        self.tabs = []
        self.cid = ""

    def w(self, s, ind=2):
        self.out.append(" " * ind + s)

    def ind(self):
        if self.en_slide:
            return 8
        return 4 if self.en_seccion else 2

    def cerrar_dl(self):
        if self.en_dl:
            self.w("</dl>", self.ind())
            self.en_dl = False

    def cerrar_contacto(self):
        if self.en_contacto:
            self.w("</div>", self.ind())
            self.en_contacto = False

    def cerrar_pasos(self):
        if self.pasos_abiertos:
            self.w("</div>", self.ind())
            self.pasos_abiertos = False

    def cerrar_slide(self):
        if self.en_slide:
            self.cerrar_pasos()
            self.en_slide = False
            self.w("</div>", 6)

    def cerrar_carrusel(self):
        self.cerrar_slide()
        if self.en_carrusel:
            self.w("</div>", 6)
            tabs = "".join('<button class="car-tab%s" data-i="%d">%s</button>'
                           % (" active" if i == 0 else "", i, esc(t))
                           for i, t in enumerate(self.tabs))
            marca = '<div class="car-tabs" data-car="%s"></div>' % self.cid
            for k, linea in enumerate(self.out):
                if marca in linea:
                    self.out[k] = linea.replace(marca, '<div class="car-tabs">%s</div>' % tabs)
                    break
            self.w('<div class="dots" id="%sDots"></div>' % self.cid, 4)
            self.w("</div>", 4)
            self.en_carrusel = False

    def cerrar_seccion(self):
        self.cerrar_pasos()
        self.cerrar_dl()
        self.cerrar_contacto()
        self.cerrar_carrusel()
        if self.en_seccion:
            self.w("</section>", 2)
            self.en_seccion = False
            self.nivel = 2

    def figura(self, valor, marcas=None):
        archivo, alt, url, estilo = partes(valor, 4)
        barra = ""
        if url:
            barra = ('<div class="bar"><span class="cdot r"></span><span class="cdot y"></span>'
                     '<span class="cdot g"></span><span class="urlbar">%s</span></div>' % esc(url))
        img = ('<img src="../assets/img/manual/%s" alt="%s" loading="lazy" decoding="async">'
               % (html.escape(archivo, quote=True), html.escape(alt, quote=True)))
        marks = ""
        if marcas:
            trozos = []
            for p in partes(marcas):
                mm = re.match(r"^(\S+)\s*:\s*([\d.]+)\s*,\s*([\d.]+)$", p)
                if not mm:
                    error("MARCAS mal formadas: %r" % p)
                    continue
                trozos.append('<span class="mark" style="left:%s%%;top:%s%%">%s</span>'
                              % (mm.group(2), mm.group(3), esc(mm.group(1))))
            marks = "".join(trozos)
        est = ' style="%s"' % html.escape(estilo, quote=True) if estilo else ""
        return ('<figure class="shot"%s>%s<div class="imgwrap">%s%s</div></figure>'
                % (est, barra, img, marks))

    def sidebar(self):
        o = self.out
        o.append('<aside class="sidebar" id="sidebar">')
        o.append('  <div class="sb-head">')
        marca = parcial("marca.html")
        o.append('    <a class="brand" href="https://cileo.io" aria-label="Cileo">%s<small>Manual</small></a>'
                 % marca)
        o.append('    <div class="search">')
        lupa = parcial("buscar.html")
        if lupa:
            o.append('      %s' % lupa)
        o.append('      <input id="navSearch" type="text" placeholder="Buscar sección" autocomplete="off">')
        o.append("    </div>")
        o.append("  </div>")
        o.append('  <nav class="sb-nav" id="sbNav">')
        for g in self.doc["nav"]:
            ind = 4
            if g["etiqueta"]:
                o.append('    <div class="sb-group">')
                o.append('      <div class="g-label">%s</div>' % esc(g["etiqueta"]))
                ind = 6
            for it in g["items"]:
                o.append('%s<a href="#%s"%s data-t="%s">%s</a>'
                         % (" " * ind, html.escape(it["ancla"], quote=True),
                            ' class="sub"' if it["sub"] else "",
                            html.escape(it["claves"], quote=True), esc(it["etiqueta"])))
            if g["etiqueta"]:
                o.append("    </div>")
        o.append("  </nav>")
        o.append('  <div class="sb-cta">')
        o.append('    <a class="gl" href="#glosario">📖 Glosario</a>')
        o.append('    <a class="fq" href="#faq">💬 FAQ</a>')
        o.append("  </div>")
        o.append("</aside>")

    def flush_shot(self):
        if self.shot_valor:
            self.w(self.figura(self.shot_valor), self.ind())
            self.shot_valor = None

    def bloque(self, b):
        t = b["tipo"]
        v = b.get("valor", "")
        if t != "marcas":
            self.flush_shot()
        if t != "paso":
            self.cerrar_pasos()
        if t not in ("termino", "gcat"):
            self.cerrar_dl()
        if t != "contacto":
            self.cerrar_contacto()

        if t == "divisor":
            self.cerrar_seccion()
            self.w('<div class="divider"><span>%s</span></div>' % esc(v))
        elif t == "seccion":
            self.cerrar_seccion()
            anc, clase = partes(v, 2)
            if anc in self.usadas:
                error("Ancla de seccion repetida: %s" % anc)
            self.usadas.add(anc)
            clase_attr = ' class="%s"' % esc(clase) if clase else ""
            self.w('<section id="%s"%s>' % (html.escape(anc, quote=True), clase_attr))
            self.en_seccion = True
            self.nivel = 2
        elif t == "kicker":
            self.w('<p class="kicker">%s</p>' % inline(v), self.ind())
        elif t == "h2":
            # Dentro de una seccion el ancla ya la da la propia seccion; un id
            # aqui solo duplicaria anclas (#dashboard y #dashboard-2).
            if self.en_seccion:
                self.w("<h2>%s</h2>" % inline(v), self.ind())
            else:
                self.w('<h2 id="%s">%s</h2>' % (ancla(v, self.usadas), inline(v)), self.ind())
            self.nivel = 2
        elif t == "h3":
            self.cerrar_carrusel()
            titulo, anc = partes(v, 2)
            if anc:
                if anc in self.usadas:
                    error("Ancla repetida: %s" % anc)
                self.usadas.add(anc)
            else:
                anc = ancla(titulo, self.usadas)
            self.w('<h3 class="sub" id="%s">%s</h3>'
                   % (html.escape(anc, quote=True), inline(titulo)), self.ind())
            self.nivel = 3
        elif t == "intro":
            self.w('<p class="intro">%s</p>' % inline(v), self.ind())
        elif t == "p":
            self.w("<p>%s</p>" % inline(v), self.ind())
        elif t == "nota":
            self.w('<p class="callout">%s</p>' % inline(v), self.ind())
        elif t == "cap":
            self.w('<p class="cap">%s</p>' % inline(v), self.ind())
        elif t == "stepper":
            trozos = [x.strip() for x in v.split(">") if x.strip()]
            flecha = '<span class="arrow">&rarr;</span>'
            cuerpo = flecha.join('<span class="s">%s</span>' % esc(x) for x in trozos)
            self.w('<div class="stepper">%s</div>' % cuerpo, self.ind())
        elif t == "shot":
            self.shot_valor = v
        elif t == "marcas":
            if not self.shot_valor:
                error("MARCAS sin SHOT previo")
            else:
                self.w(self.figura(self.shot_valor, v), self.ind())
                self.shot_valor = None
        elif t == "paso":
            if not self.pasos_abiertos:
                self.w('<div class="steps">', self.ind())
                self.pasos_abiertos = True
                self.paso_n = 0
            self.paso_n += 1
            titulo, texto = partes(v, 2)
            h = min(self.nivel + 1, 6)
            plantilla = '<div class="step"><div class="b">%d</div><div><h%d>%s</h%d><p>%s</p></div></div>'
            self.w(plantilla % (self.paso_n, h, inline(titulo), h, inline(texto)), self.ind() + 2)
        elif t == "lista":
            ind = self.ind()
            self.w("<ul>", ind)
            for f in b["filas"]:
                self.w("<li>%s</li>" % inline(f), ind + 2)
            self.w("</ul>", ind)
        elif t == "tabla":
            ind = self.ind()
            filas = [[c.strip() for c in f.strip().strip("|").split("|")] for f in b["filas"]]
            self.w('<div class="tablewrap"><table>', ind)
            if filas:
                cab = "".join("<th>%s</th>" % inline(c) for c in filas[0])
                self.w("<thead><tr>%s</tr></thead>" % cab, ind + 2)
                self.w("<tbody>", ind + 2)
                for f in filas[1:]:
                    cel = "".join("<td>%s</td>" % inline(c) for c in f)
                    self.w("<tr>%s</tr>" % cel, ind + 4)
                self.w("</tbody>", ind + 2)
            self.w("</table></div>", ind)
        elif t == "carrusel":
            self.cerrar_carrusel()
            self.cid = v or "dashCar"
            self.tabs = []
            cid = html.escape(self.cid, quote=True)
            self.w('<div class="carousel" id="%s">' % cid, 4)
            self.w('<div class="car-head">', 6)
            self.w('<div class="car-tabs" data-car="%s"></div>' % cid, 8)
            prev = '<button class="car-btn" id="carPrev" aria-label="Anterior">&lsaquo;</button>'
            sig = '<button class="car-btn" id="carNext" aria-label="Siguiente">&rsaquo;</button>'
            self.w('<div class="car-nav">%s%s</div>' % (prev, sig), 8)
            self.w("</div>", 6)
            self.w('<div class="track" id="%sTrack">' % cid, 6)
            self.en_carrusel = True
        elif t == "slide":
            if not self.en_carrusel:
                error("SLIDE fuera de CARRUSEL")
                return
            self.cerrar_slide()
            etiqueta, url = partes(v, 2)
            self.tabs.append(etiqueta)
            self.w('<div class="slide">', 6)
            self.en_slide = True
            if etiqueta:
                extra = ""
                if url:
                    extra = ' &middot; <span class="surl">%s</span>' % esc(url)
                self.w('<p class="slabel">Vista %s%s</p>' % (esc(etiqueta), extra), 8)
        elif t == "gcat":
            self.w('<div class="gcat">%s</div>' % esc(v), self.ind())
        elif t == "termino":
            nombre, definicion = partes(v, 2)
            ref = ""
            mm = re.match(r"^(.*?)\s*->\s*(.+)$", nombre)
            if mm:
                nombre, ref = mm.group(1).strip(), mm.group(2).strip()
            if not self.en_dl:
                self.w("<dl>", self.ind())
                self.en_dl = True
            r = ' <span class="ref">&rarr; %s</span>' % esc(ref) if ref else ""
            self.w("<dt>%s%s</dt><dd>%s</dd>" % (esc(nombre), r, inline(definicion)), self.ind() + 2)
        elif t == "fcat":
            self.w('<div class="fcat">%s</div>' % esc(v), self.ind())
        elif t == "pregunta":
            pregunta, respuesta = partes(v, 2)
            self.w('<details><summary>%s</summary><div class="ans">%s</div></details>'
                   % (inline(pregunta), inline(respuesta)), self.ind())
        elif t == "contacto":
            if not self.en_contacto:
                self.w('<div class="contact">', self.ind())
                self.en_contacto = True
            texto, url = partes(v, 2)
            self.w('<a href="%s">%s</a>' % (html.escape(url, quote=True), esc(texto)), self.ind() + 2)
        elif t == "fincontacto":
            pass
        else:
            error("Directiva desconocida: %s" % t.upper())

    def construir(self):
        meta = self.doc["meta"]
        o = self.out
        o.append("<!doctype html>")
        o.append('<html lang="es">')
        o.append("<head>")
        o.append('<meta charset="utf-8">')
        o.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
        o.append("<title>%s</title>" % esc(meta.get("TITULO", "Manual Cileo")))
        o.append('<meta name="description" content="%s">'
                 % html.escape(meta.get("LEDE", "")[:300], quote=True))
        o.append('<link rel="icon" type="image/svg+xml" href="../assets/img/main/favicon.svg" />')
        o.append('<link href="../assets/css/fonts.css" rel="stylesheet" />')
        o.append('<link href="../assets/css/main.css" rel="stylesheet" />')
        o.append('<link href="../assets/css/manual.css" rel="stylesheet" />')
        o.append("</head>")
        o.append("<body>")
        o.append(EMAIL_OFF_INI)
        o.append('<button class="menu-btn" id="menuBtn" aria-label="Menú">☰ Menú</button>')
        o.append('<div class="backdrop" id="backdrop"></div>')
        self.sidebar()
        o.append("<main>")
        self.w('<p class="hero-eyebrow">Documentación de producto</p>')
        self.w("<h1>%s</h1>" % esc(meta.get("TITULO", "Manual Cileo")))
        if meta.get("LEDE"):
            self.w('<p class="lede">%s</p>' % inline(meta["LEDE"]))
        if meta.get("TAGS"):
            tags = "".join('<span class="tag">%s</span>' % esc(x) for x in partes(meta["TAGS"]))
            self.w('<div class="meta">%s</div>' % tags)
        if meta.get("ACTUALIZADO"):
            self.w('<p class="cap">Actualizado: %s</p>' % esc(meta["ACTUALIZADO"]))
        for b in self.doc["bloques"]:
            self.bloque(b)
        self.flush_shot()
        self.cerrar_seccion()
        o.append("</main>")
        o.append('<script src="../assets/js/manual.js"></script>')
        o.append(EMAIL_OFF_FIN)
        o.append("</body>")
        o.append("</html>")
        return "\n".join(o) + "\n"


def normalizar(t):
    """Compara texto sin que estorben los espacios que deja el quitar etiquetas."""
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s+([,.;:)!?])", lambda m: m.group(1), t)
    t = re.sub(r"([(])\s+", lambda m: m.group(1), t)
    return t.strip()


def verificar(fuente_txt, html_txt):
    niveles = [int(m.group(1)) for m in re.finditer(r"<h([1-6])[ >]", html_txt)]
    prev = 0
    for n in niveles:
        if prev and n > prev + 1:
            error("Salto de encabezado h%d a h%d" % (prev, n))
        prev = n
    ids = re.findall(r' id="([^"]+)"', html_txt)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        error("Anclas duplicadas: %s" % ", ".join(dup))
    for destino in sorted(set(re.findall(r'href="#([^"]+)"', html_txt))):
        if destino not in ids:
            error("Enlace interno sin destino: #%s" % destino)
    if EMAIL_OFF_INI not in html_txt or EMAIL_OFF_FIN not in html_txt:
        error("Falta el envoltorio email_off")
    # El JS de la pagina busca estos ganchos; si falta uno, la pagina se rompe en
    # silencio (asi se rompio el carrusel una vez).
    for gancho in ("menuBtn", "backdrop", "sidebar", "sbNav", "navSearch",
                   "dashCar", "carPrev", "carNext"):
        if (' id="%s"' % gancho) not in html_txt:
            error("Falta el id que usa manual.js: %s" % gancho)
    for clase in (".track", ".dots"):
        if ('class="%s"' % clase.lstrip(".")) not in html_txt:
            error("Falta el elemento con clase %s dentro del carrusel" % clase)
    for et in ("section", "div", "details", "dl", "table", "figure", "main", "aside", "ul", "nav"):
        a = len(re.findall(r"<%s[ >]" % et, html_txt))
        c = len(re.findall(r"</%s>" % et, html_txt))
        if a != c:
            error("Etiqueta %s desbalanceada: %d aperturas, %d cierres" % (et, a, c))
    visible = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html_txt)
    visible = html.unescape(re.sub(r"<[^>]+>", " ", visible))
    visible = normalizar(visible)
    omitir = ("NAV", "NAVGRUPO", "SECCION", "SHOT", "MARCAS", "CARRUSEL",
              "TAGS", "ACTUALIZADO", "CONTACTO", "TITULO", "STEPPER")
    faltan = []
    for linea in fuente_txt.splitlines():
        linea = linea.strip()
        m = re.match(r"^([A-Z0-9_]+):\s*(.*)$", linea)
        if not m or m.group(1) in omitir:
            continue
        valor = m.group(2)
        if m.group(1) == "H3":
            valor = valor.split("|")[0]
        for trozo in re.split(r"\s*\|\s*", valor):
            trozo = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", trozo)
            trozo = trozo.replace("**", "").replace("`", "")
            trozo = re.sub(r"\s*->\s*", " → ", trozo)
            trozo = normalizar(trozo)
            if len(trozo) < 15:
                continue
            if trozo not in visible:
                faltan.append(trozo[:70])
    for f in faltan[:12]:
        error("Texto de la fuente ausente en el HTML: %s" % f)
    if len(faltan) > 12:
        error("y %d fragmentos mas" % (len(faltan) - 12))
    return {"encabezados": len(niveles), "anclas": len(set(ids))}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera el manual de Cileo desde su fuente de texto.")
    ap.add_argument("--fuente", default=os.path.join(RAIZ, "fuente-manual.txt"))
    ap.add_argument("--salida", default=os.path.join(RAIZ, "index.html"))
    ap.add_argument("--verificar", action="store_true")
    a = ap.parse_args(argv)
    fuente_txt = open(a.fuente, encoding="utf-8").read()
    doc = leer(a.fuente)
    html_txt = Render(doc).construir()
    st = verificar(fuente_txt, html_txt)
    print("Secciones: %d  encabezados: %d  anclas: %d  imagenes: %d"
          % (html_txt.count("<section"), st["encabezados"], st["anclas"], html_txt.count("<img ")))
    print("Tamano del HTML: %.1f KB" % (len(html_txt.encode("utf-8")) / 1024.0))
    if ERRORES:
        print("")
        print("%d ERROR(ES):" % len(ERRORES))
        for e in ERRORES:
            print("  - %s" % e)
        return 1
    print("Verificacion OK")
    if not a.verificar:
        with open(a.salida, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(html_txt)
        print("Escrito: %s" % a.salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
