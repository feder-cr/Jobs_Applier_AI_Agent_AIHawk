from invisible_playwright import InvisiblePlaywright

prices = []
with InvisiblePlaywright(seed=7) as browser:
    page = browser.new_page()
    for n in (1, 2, 3):
        page.goto(f"https://books.toscrape.com/catalogue/page-{n}.html",
                  wait_until="domcontentloaded")
        for card in page.locator("article.product_pod").all():
            prices.append(float(card.locator(".price_color").inner_text().lstrip("£")))

print("books:", len(prices))
print("above 40:", sum(1 for p in prices if p > 40.00))
bands = {}
for p in prices:
    lo = int(p // 10) * 10
    bands[f"{lo}-{lo+10}"] = bands.get(f"{lo}-{lo+10}", 0) + 1
for band, count in sorted(bands.items(), key=lambda kv: -kv[1]):
    print(band, count)
