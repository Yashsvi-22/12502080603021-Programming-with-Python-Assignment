
from html.parser import HTMLParser
import re
import os


class ProductParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current_product = None
        self.current_field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()

        if "product" in classes:
            self.current_product = {}

        elif self.current_product is not None:
            if "name" in classes:
                self.current_field = "name"
                self.current_product.setdefault("name_text", "")

            elif "price" in classes:
                self.current_field = "price"
                self.current_product.setdefault("price_text", "")

            elif "rating" in classes:
                self.current_field = "rating"
                self.current_product.setdefault("rating_text", "")

    def handle_data(self, data):
        if self.current_product is not None and self.current_field:
            key = self.current_field + "_text"
            self.current_product[key] += data.strip() + " "

    def handle_endtag(self, tag):
        if self.current_product is not None:
            if self.current_field:
                self.current_field = None

            if tag == "div":
                name = self.current_product.get("name_text", "").strip()
                price = self.current_product.get("price_text", "").strip()
                rating = self.current_product.get("rating_text", "").strip()

                if name and price and rating:
                    self.products.append({
                        "name": name,
                        "price_text": price,
                        "rating_text": rating
                    })

                self.current_product = None


def normalize_price(price_text):
    cleaned = re.sub(r"[^0-9.]", "", price_text)

    if not cleaned:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def scrape_file(file_path):
    parser = ProductParser()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parser.feed(line)

    return parser.products


def main():
    p, k = map(int, input().split())
    file_paths = [input().strip() for _ in range(p)]

    unique_products = {}

    for file_path in file_paths:
        if not os.path.isfile(file_path):
            print("File not found:", file_path)
            continue

        try:
            products = scrape_file(file_path)

            for product in products:
                name = product["name"]
                price = normalize_price(product["price_text"])

                rating_match = re.search(
                    r"\d+(?:\.\d+)?", product["rating_text"]
                )

                if price is None or not rating_match:
                    continue

                rating = float(rating_match.group())

                cleaned_product = {
                    "name": name,
                    "price": price,
                    "rating": rating
                }

                if name not in unique_products:
                    unique_products[name] = cleaned_product
                else:
                    old = unique_products[name]

                    if (-rating, price, name) < (
                        -old["rating"], old["price"], old["name"]
                    ):
                        unique_products[name] = cleaned_product

        except (OSError, UnicodeError) as error:
            print("Could not read", file_path, ":", error)

    ranked_products = sorted(
        unique_products.values(),
        key=lambda product: (
            -product["rating"],
            product["price"],
            product["name"]
        )
    )

    for product in ranked_products[:k]:
        price = product["price"]

        if price.is_integer():
            price = int(price)

        print(product["name"], price, product["rating"])


if __name__ == "__main__":
    main()
