"""Genera páginas estáticas para Google: una por IA, una por pack, índices, sitemap y robots.
Se ejecuta en cada publicación (GitHub Actions). No hace falta tocarlo al actualizar datos."""
import json, os, html, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("SITE_URL", "https://juandoga.github.io/brujula-ia").rstrip("/")
d = json.load(open(os.path.join(RAIZ, "data", "brujula.json"), encoding="utf-8"))
e = lambda s: html.escape(str(s or ""), quote=True)

GRATIS = {"libre": "Gratis de verdad", "util": "Plan gratis útil", "limitado": "Gratis muy limitado",
          "prueba": "Solo prueba", "no": "De pago"}
MEJOR = {"ordenador": "Mejor en ordenador", "movil": "Mejor en móvil", "ambos": "Móvil y ordenador"}
NIVEL = {1: "Fácil", 2: "Intermedio", 3: "Avanzado"}
MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"]
def fecha(iso):
    try: y, m, dd = map(int, iso.split("-")); return f"{dd} de {MESES[m-1]} de {y}"
    except Exception: return iso or ""

CSS = """:root{--bg:#F4F5F9;--card:#fff;--ink:#11151C;--ink2:#2E3746;--muted:#667085;--rule:#E1E4EC;--accent:#5B3FD9;--soft:#ECE8FD;--ok:#157347;--oks:#DCF3E6;--bad:#A3261F;--bads:#FBE1DE}
@media (prefers-color-scheme:dark){:root{--bg:#0D1016;--card:#161A22;--ink:#F1F3F8;--ink2:#C9CFDB;--muted:#8C95A6;--rule:#272D39;--accent:#9C88FF;--soft:#231D45;--ok:#6FD6A0;--oks:#12291D;--bad:#F59A92;--bads:#3A1614;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink2);font:16px/1.55 "Atkinson Hyperlegible","Segoe UI",system-ui,sans-serif}
.w{max-width:760px;margin:0 auto;padding:20px 16px 60px}a{color:var(--accent)}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:22px}
.logo{font:800 24px "Bricolage Grotesque","Segoe UI",sans-serif;color:var(--ink);text-decoration:none;letter-spacing:-.03em}.logo span{color:var(--accent)}
h1,h2{color:var(--ink);font-family:"Bricolage Grotesque","Segoe UI",sans-serif;line-height:1.15;margin:0}h1{font-size:34px;font-weight:800}h2{font-size:20px;margin:26px 0 8px}
.sub{color:var(--muted);margin:6px 0 16px}.lead{font-size:18px;color:var(--ink)}
.card{background:var(--card);border:1px solid var(--rule);border-radius:14px;padding:16px;margin:12px 0}
.row{display:flex;flex-wrap:wrap;gap:8px}.pill{font-size:13px;font-weight:700;padding:3px 10px;border-radius:999px;background:var(--soft);color:var(--ink)}
.pc{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:520px){.pc{grid-template-columns:1fr}}
.pro{background:var(--oks)}.con{background:var(--bads)}.pro h2{color:var(--ok);margin-top:0}.con h2{color:var(--bad);margin-top:0}
ul{padding-left:1.2em;margin:6px 0}table{width:100%;border-collapse:collapse}td{padding:8px 4px;border-top:1px solid var(--rule);vertical-align:top}td.n{text-align:right;white-space:nowrap;font-weight:700;color:var(--ink)}
.cta{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;font-weight:700;padding:12px 18px;border-radius:12px;margin:8px 8px 0 0}
.small{font-size:13px;color:var(--muted)}.list a{display:block;padding:8px 0;border-top:1px solid var(--rule);text-decoration:none;color:var(--ink);font-weight:700}.list a span{color:var(--muted);font-weight:400;font-size:14px}"""

def pagina(ruta, titulo, desc, cuerpo, canon):
    doc = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{e(canon)}">
<meta property="og:title" content="{e(titulo)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{e(canon)}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='24' fill='%235B3FD9'/%3E%3Ctext x='50' y='70' font-family='Arial Black,Arial' font-size='60' font-weight='900' text-anchor='middle' fill='%23fff'%3Ec%3C/text%3E%3C/svg%3E">
<style>{CSS}</style></head><body><div class="w">
<div class="top"><a class="logo" href="{SITE}/">Cual<span>ia</span></a><a href="{SITE}/">¿Qué IA uso para esto?</a></div>
{cuerpo}
<p class="small" style="margin-top:36px">Cualia es una guía independiente de herramientas de IA en español, revisada cada semana. Precios orientativos.</p>
</div><!-- Cloudflare Web Analytics --><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "8693430a24394f339b7e26f53a417319"}}'></script><!-- End Cloudflare Web Analytics --></body></html>"""
    destino = os.path.join(RAIZ, ruta)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    open(destino, "w", encoding="utf-8").write(doc)

urls = [(SITE + "/", d["meta"].get("ultimaRevision"))]
por_nombre = {}
for c in d["cats"]:
    for h in c["herramientas"]:
        h["_cat"] = c["nombre"]; por_nombre[h["nombre"]] = h

# Páginas por IA
for c in d["cats"]:
    for h in c["herramientas"]:
        n = h.get("notas", {})
        canon = f"{SITE}/ia/{h['slug']}/"
        packs = [p for p in d.get("packs", []) if any(s["ia"] == h["nombre"] for s in p["pasos"])]
        alternativas = sorted([x for x in c["herramientas"] if x["id"] != h["id"]], key=lambda x: -x["nota"])[:5]
        cuerpo = f"""<p class="small">{e(c['nombre'])} · {e(h['empresa'])}</p>
<h1>{e(h['nombre'])}: qué es, precio y si es gratis</h1>
<p class="sub">Revisado el {fecha(h['actualizado'])}{' · verificado con fuentes' if h.get('verificado') else ''}</p>
<p class="lead">{e(h['desc'])}</p>
<div class="row"><span class="pill">Nota {h['nota']}/100</span><span class="pill">{e(GRATIS.get(h['gratisTipo'],''))}</span><span class="pill">{e(MEJOR.get(h.get('mejorEn'),''))}</span><span class="pill">{e(NIVEL.get(h.get('nivel'),''))}</span></div>
<h2>¿Es gratis {e(h['nombre'])}?</h2><p><b>{e(GRATIS.get(h['gratisTipo'],''))}.</b> {e(h.get('gratisTxt'))}</p>
<h2>Precio</h2><p>{e(h['precioTxt'])} (orientativo).</p>{('<p><b>⚠ Puede costar más:</b> '+e(h.get('consumoTxt'))+'</p>') if h.get('consumo') in ('creditos','uso') else ''}
<div class="pc"><div class="card pro"><h2>Ventajas</h2><ul>{''.join(f'<li>{e(x)}</li>' for x in h.get('pros',[]))}</ul></div>
<div class="card con"><h2>Desventajas</h2><ul>{''.join(f'<li>{e(x)}</li>' for x in h.get('contras',[]))}</ul></div></div>
<h2>Para quién es</h2><p>{e(h['para'])}</p>
<h2>Ejemplos de uso</h2><ul>{''.join(f'<li>{e(x)}</li>' for x in h.get('ejemplos',[]))}</ul>
<h2>Nota de Cualia: {h['nota']}/100</h2><p>Calidad {n.get('calidad')}/10 · Versatilidad {n.get('versatilidad')}/10 · Facilidad {n.get('facilidad')}/10 · Precio {n.get('precio')}/10. <a href="{SITE}/#consejos">Cómo se calcula</a>.</p>
{('<h2>Novedad</h2><p>'+e(h['novedad'])+'</p>') if h.get('novedad') else ''}
{('<h2>Packs que la incluyen</h2><div class="list">'+''.join(f'<a href="{SITE}/pack/{e(p["id"])}/">{e(p["titulo"])} <span>· ≈ {p["total"]} €/mes completo</span></a>' for p in packs)+'</div>') if packs else ''}
<h2>Alternativas a {e(h['nombre'])}</h2><div class="list">{''.join(f'<a href="{SITE}/ia/{e(a["slug"])}/">{e(a["nombre"])} <span>· nota {a["nota"]} · {e(GRATIS.get(a["gratisTipo"],""))}</span></a>' for a in alternativas)}</div>
<p><a class="cta" href="{SITE}/?ia={e(h['slug'])}">Ver ficha completa en Cualia</a>{f'<a class="cta" style="background:var(--soft);color:var(--ink)" href="{e(h.get("afiliado") or h["web"])}" rel="noopener{" sponsored" if h.get("afiliado") else ""}">Ir a {e(h["nombre"])}</a>' if h.get('web') else ''}</p>"""
        titulo = f"{h['nombre']}: precio, si es gratis y alternativas | Cualia"
        desc = f"{h['nombre']} ({c['nombre'].lower()}): {GRATIS.get(h['gratisTipo'],'').lower()}. {h.get('gratisTxt','')} Ventajas, desventajas, precio y alternativas, revisado el {fecha(h['actualizado'])}."
        pagina(f"ia/{h['slug']}/index.html", titulo, desc[:300], cuerpo, canon)
        urls.append((canon, h["actualizado"]))

# Páginas por pack
for p in d.get("packs", []):
    canon = f"{SITE}/pack/{p['id']}/"
    filas = "".join(
        f"<tr><td><b><a href=\"{SITE}/ia/{e(por_nombre[s['ia']]['slug'])}/\">{e(s['ia'])}</a></b><br><span class=\"small\">{e(s['rol'])} · Gratis: {e(s['gratis'])}</span></td>"
        f"<td class=\"n\">{('≈ '+str(s['precio'])+' €/mes<br><span class=small>'+e(s['plan'])+'</span>') if s['precio'] else 'Gratis'}</td></tr>"
        for s in p["pasos"] if s["ia"] in por_nombre)
    cuerpo = f"""<p class="small">Pack de IAs</p><h1>{e(p['titulo'])}: qué IAs usar y cuánto cuesta</h1>
<p class="sub">{e(p['para'])}</p>
<div class="row"><span class="pill">Versión gratis: 0 €</span><span class="pill">Versión completa: ≈ {p['total']} €/mes</span></div>
<h2>Paso a paso</h2><div class="card"><table>{filas}</table></div>
<h2>¿Se puede hacer gratis?</h2><p>{e(p['notaGratis'])}</p>
<p><a class="cta" href="{SITE}/#packs">Ver todos los packs</a></p>"""
    titulo = f"{p['titulo']}: IAs necesarias y precio total | Cualia"
    desc = f"{p['titulo']} con inteligencia artificial: qué IAs usar en cada paso, qué se puede hacer gratis y cuánto cuesta la versión completa (≈ {p['total']} €/mes)."
    pagina(f"pack/{p['id']}/index.html", titulo, desc, cuerpo, canon)
    urls.append((canon, d["meta"].get("ultimaRevision")))

# Índices
lista_ias = "".join(f"<h2>{e(c['nombre'])}</h2><div class=\"list\">" + "".join(
    f"<a href=\"{SITE}/ia/{e(h['slug'])}/\">{e(h['nombre'])} <span>· nota {h['nota']} · {e(GRATIS.get(h['gratisTipo'],''))}</span></a>"
    for h in sorted(c["herramientas"], key=lambda x: -x["nota"])) + "</div>" for c in d["cats"])
pagina("ia/index.html", "Todas las IAs: precios, si son gratis y alternativas | Cualia",
       "Catálogo de 240 herramientas de inteligencia artificial en español: qué incluye de verdad su versión gratis, precio, ventajas y desventajas.",
       f"<h1>Todas las IAs</h1><p class=\"sub\">Revisado el {fecha(d['meta'].get('ultimaRevision'))}</p>{lista_ias}", f"{SITE}/ia/")
urls.append((f"{SITE}/ia/", d["meta"].get("ultimaRevision")))
pagina("pack/index.html", "Packs de IAs para cada proyecto, con precio total | Cualia",
       "Combinaciones de herramientas de IA para hacer un corto, un videoclip, un podcast o un negocio online, con lo que se puede hacer gratis y el precio total.",
       "<h1>Packs de IAs</h1><div class=\"list\">" + "".join(f"<a href=\"{SITE}/pack/{e(p['id'])}/\">{e(p['titulo'])} <span>· ≈ {p['total']} €/mes</span></a>" for p in d.get("packs", [])) + "</div>",
       f"{SITE}/pack/")
urls.append((f"{SITE}/pack/", d["meta"].get("ultimaRevision")))

# Sitemap y robots
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, f in urls:
    sm.append(f"<url><loc>{e(u)}</loc>{f'<lastmod>{e(f)}</lastmod>' if f else ''}</url>")
sm.append("</urlset>")
open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))
open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print(f"Generadas {len(urls)} páginas")
