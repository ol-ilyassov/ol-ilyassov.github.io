#!/usr/bin/env python3
"""Генерирует статические страницы товаров product/<slug>/index.html из products.json.

GitHub Pages отдаёт только статические файлы, поэтому для каждого slug
создаётся отдельная папка. Параметр ?setcity=... обрабатывается на клиенте (city.js).

Дополнительно генерируется 404.html: для любого другого /product/<slug>/
он показывает шаблонную страницу товара, иначе — «не найдено» и список товаров.

Запуск из корня репозитория:  python3 scripts/build_products.py
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://ol-ilyassov.github.io"
OUT = ROOT / "product"


def money(n):
    return f"{n:,}".replace(",", " ") + " ₸"


def page(p):
    e = html.escape
    url = f"{SITE}/product/{p['slug']}/"
    availability = "InStock" if p["in_stock"] else "OutOfStock"
    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["title"],
        "description": p["description"],
        "sku": p["slug"],
        "category": p["category"],
        "url": url,
        "offers": {
            "@type": "Offer",
            "url": url,
            "priceCurrency": "KZT",
            "price": str(p["price"]),
            "availability": f"https://schema.org/{availability}",
            "itemCondition": "https://schema.org/NewCondition",
        },
    }
    ld_json = json.dumps(ld, ensure_ascii=False, indent=2).replace("</", "<\\/")
    old = f'<span class="old">{money(p["old_price"])}</span>' if p.get("old_price") else ""
    stock = (
        '<span class="stock">В наличии</span>'
        if p["in_stock"]
        else '<span class="stock out">Нет в наличии</span>'
    )
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{e(p['title'])} — Тестовый магазин</title>
    <meta name="description" content="{e(p['description'])}" />
    <meta name="robots" content="noindex" />
    <link rel="canonical" href="{url}" />
    <link rel="stylesheet" href="/style.css" />
    <script src="/city.js"></script>
    <script type="application/ld+json">
{ld_json}
    </script>
  </head>
  <body>
    <div class="notice">
      Это тестовый сайт. Товары и цены вымышлены, заказы не принимаются.
    </div>

    <header>
      <div class="wrap nav">
        <a class="logo" href="/"><span class="logo-mark">Т</span>Тестовый магазин</a>
        <span class="city-pill">📍 <span data-city-name>Алматы</span></span>
        <a class="btn btn-ghost" href="/#products">Корзина · 0</a>
      </div>
    </header>

    <main>
      <section>
        <div class="wrap">
          <nav class="crumbs muted">
            <a href="/">Главная</a> / <a href="/#catalog">{e(p['category'])}</a> / {e(p['title'])}
          </nav>
          <div class="product">
            <div class="product-img" style="background: {p['gradient']}">{p['icon']}</div>
            <div class="product-info">
              <span class="badge">{e(p['category'])}</span>
              <h1>{e(p['title'])}</h1>
              <p class="muted">{e(p['meta'])}</p>
              <div class="product-price">
                <span class="price">{money(p['price'])}{old}</span>{stock}
              </div>
              <p class="lead">{e(p['description'])}</p>
              <p class="muted">Доставка в город <b data-city-name>Алматы</b> — условная, только для демонстрации.</p>
              <div class="hero-actions">
                <a class="btn btn-primary" href="/#products">Купить</a>
                <a class="btn btn-ghost" href="/">На главную</a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer>
      <div class="wrap foot">
        <span>© Тестовый магазин</span>
        <span>Демонстрационный сайт · не является реальным магазином</span>
      </div>
    </footer>
  </body>
</html>
"""


def card(p):
    e = html.escape
    old = f'<span class="old">{money(p["old_price"])}</span>' if p.get("old_price") else ""
    stock = (
        '<span class="stock">В наличии</span>'
        if p["in_stock"]
        else '<span class="stock out">Нет в наличии</span>'
    )
    return f"""            <a class="card" href="/product/{p['slug']}/">
              <div class="card-img" style="background: {p['gradient']}">{p['icon']}</div>
              <div class="card-body">
                <div class="card-title">{e(p['title'])}</div>
                <div class="card-meta">{e(p['meta'])}</div>
                <div class="card-foot"><span class="price">{money(p['price'])}{old}</span>{stock}</div>
              </div>
            </a>"""


def fallback(products):
    """404.html: GitHub Pages отдаёт его на любой несуществующий путь.

    /product/<любой-slug>/ → шаблонная страница товара;
    любой другой путь → «страница не найдена».
    В обоих случаях ниже показывается список подготовленных товаров.
    """
    cards = "\n".join(card(p) for p in products)
    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Тестовый магазин</title>
    <meta name="robots" content="noindex" />
    <link rel="stylesheet" href="/style.css" />
    <script src="/city.js"></script>
  </head>
  <body>
    <div class="notice">
      Это тестовый сайт. Товары и цены вымышлены, заказы не принимаются.
    </div>

    <header>
      <div class="wrap nav">
        <a class="logo" href="/"><span class="logo-mark">Т</span>Тестовый магазин</a>
        <span class="city-pill">📍 <span data-city-name>Алматы</span></span>
        <a class="btn btn-ghost" href="/#products">Корзина · 0</a>
      </div>
    </header>

    <main>
      <section id="template" hidden>
        <div class="wrap">
          <nav class="crumbs muted">
            <a href="/">Главная</a> / <a href="/#catalog">Каталог</a> / <span class="js-title"></span>
          </nav>
          <div class="product">
            <div class="product-img" style="background: linear-gradient(135deg, #e5e7eb, #ddd6fe)">📦</div>
            <div class="product-info">
              <span class="badge">Шаблонная страница</span>
              <h1 class="js-title"></h1>
              <p class="muted">Артикул: <code class="js-slug"></code></p>
              <div class="product-price">
                <span class="price">Цена по запросу</span><span class="stock out">Нет данных</span>
              </div>
              <p class="lead">
                Этого товара нет в тестовом каталоге — страница собрана автоматически по адресу.
              </p>
              <p class="muted">Доставка в город <b data-city-name>Алматы</b> — условная, только для демонстрации.</p>
              <div class="hero-actions">
                <a class="btn btn-primary" href="#list">Посмотреть товары</a>
                <a class="btn btn-ghost" href="/">На главную</a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="notfound" hidden>
        <div class="wrap">
          <span class="badge">404</span>
          <h1>Страница не найдена</h1>
          <p class="lead">Такой страницы нет. Посмотрите товары тестового магазина ниже.</p>
        </div>
      </section>

      <section id="list">
        <div class="wrap">
          <div class="section-head">
            <h2>Товары магазина</h2>
            <span class="muted">Цены условные, в тенге</span>
          </div>
          <div class="grid">
{cards}
          </div>
        </div>
      </section>
    </main>

    <footer>
      <div class="wrap foot">
        <span>© Тестовый магазин</span>
        <span>Демонстрационный сайт · не является реальным магазином</span>
      </div>
    </footer>

    <script>
      (function () {{
        var m = location.pathname.match(/^\\/product\\/([^\\/]+)\\/?$/);
        var slug = null;
        if (m) {{
          try {{ slug = decodeURIComponent(m[1]); }} catch (e) {{ slug = m[1]; }}
        }}
        if (!slug) {{
          document.getElementById("notfound").hidden = false;
          return;
        }}
        var words = slug.replace(/[-_]+/g, " ").trim();
        var title = words.charAt(0).toUpperCase() + words.slice(1);
        document.title = title + " — Тестовый магазин";
        document.querySelectorAll(".js-title").forEach(function (el) {{ el.textContent = title; }});
        document.querySelectorAll(".js-slug").forEach(function (el) {{ el.textContent = slug; }});
        document.getElementById("template").hidden = false;
        document.querySelector("#list h2").textContent = "Другие товары";
      }})();
    </script>
  </body>
</html>
"""


def main():
    products = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    (ROOT / "404.html").write_text(fallback(products), encoding="utf-8")
    print("404.html")
    slug_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    if OUT.exists():
        shutil.rmtree(OUT)
    for p in products:
        if not slug_re.match(p["slug"]):
            raise SystemExit(f"Некорректный slug: {p['slug']!r}")
        d = OUT / p["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(page(p), encoding="utf-8")
        print(f"product/{p['slug']}/index.html")


if __name__ == "__main__":
    main()
