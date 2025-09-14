import json
import scrapy
from urllib.parse import quote
from collections import defaultdict

class CookpadSpider(scrapy.Spider):
    name = "cookpad"
    allowed_domains = ["cookpad.com"]

    keywords = ["ayam", "ikan", "nasi", "kue", "pisang", "diet", "sop buah"]
    max_per_keyword = 100
    keyword_counts = defaultdict(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_titles = set()  # simpan judul unik

    def start_requests(self):
        for kw in self.keywords:
            url = f"https://cookpad.com/id/cari/{quote(kw)}?order=recent&page=1"
            yield scrapy.Request(url, callback=self.parse_list, meta={"keyword": kw, "page": 1})

    def parse_list(self, response):
        keyword = response.meta["keyword"]
        page = response.meta["page"]

        if self.keyword_counts[keyword] >= self.max_per_keyword:
            return

        for recipe in response.css("a.block-link__main::attr(href)").getall():
            if self.keyword_counts[keyword] >= self.max_per_keyword:
                break
            url = response.urljoin(recipe)
            yield scrapy.Request(url, callback=self.parse_recipe, meta={"keyword": keyword})

        if self.keyword_counts[keyword] < self.max_per_keyword:
            next_page = page + 1
            next_url = f"https://cookpad.com/id/cari/{quote(keyword)}?order=recent&page={next_page}"
            yield scrapy.Request(next_url, callback=self.parse_list, meta={"keyword": keyword, "page": next_page})

    def parse_recipe(self, response):
        keyword = response.meta["keyword"]
        if self.keyword_counts[keyword] >= self.max_per_keyword:
            return

        scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
        for s in scripts:
            try:
                data = json.loads(s)
                if isinstance(data, list):
                    for entry in data:
                        if entry.get("@type") == "Recipe":
                            item = self.extract_recipe(entry, keyword, response.url)
                            if item:
                                yield item
                            return
                else:
                    if data.get("@type") == "Recipe":
                        item = self.extract_recipe(data, keyword, response.url)
                        if item:
                            yield item
                        return
            except Exception as e:
                self.logger.debug(f"Gagal parse JSON di {response.url}: {e}")

    def extract_recipe(self, recipe, keyword, url):
        title = recipe.get("name")
        if not title:
            return None

        # cek duplikat judul
        if title in self.seen_titles:
            self.logger.debug(f"Skip duplikat: {title}")
            return None
        self.seen_titles.add(title)

        self.keyword_counts[keyword] += 1
        return {
            "keyword": keyword,
            "url": recipe.get("url") or url,
            "judul": title,
            "bahan": recipe.get("recipeIngredient", []),
            "langkah": [step.get("text") for step in recipe.get("recipeInstructions", []) if isinstance(step, dict)],
        }
