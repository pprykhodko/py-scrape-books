from collections.abc import Iterator

import scrapy
from scrapy.http import Response


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/page-1.html"]

    def parse(self, response: Response, **kwargs) -> Iterator[scrapy.Request]:
        for book in response.css("article.product_pod"):
            book_url = book.css("h3 a::attr(href)").get()
            yield response.follow(book_url, callback=self._parse_book_info)

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def _parse_book_info(
            self,
            response: Response
    ) -> Iterator[dict[str, str | int | float | None]]:
        yield {
            "title": response.css(".product_main h1::text").get(),
            "price": float(
                response.css(
                    ".product_main .price_color::text"
                ).get().replace("£", "")
            ),
            "amount_in_stock": int(
                response.css(
                    ".product_main .availability::text"
                ).getall()[-1].strip().split()[-2].replace("(", "")
            ),
            "rating": response.css(
                ".product_main .star-rating::attr(class)"
            ).get().split()[1],
            "category": response.css(
                ".breadcrumb > li"
            )[-2].css("a::text").get(),
            "description": response.css(
                "#product_description + p::text"
            ).get(),
            "upc": response.css(".table-striped tr td::text").get()
        }
