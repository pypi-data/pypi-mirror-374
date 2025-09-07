import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

import pytz
import requests
from bs4 import BeautifulSoup

from .utils import BREAK_TIME, FMS_BASE_URL, RETRY_PERIOD, fix_json


@dataclass
class Variant:
    """A class to hold details of a variant of an item."""

    id: int
    name: str
    price: str
    available: bool
    quantity: int
    created_at: datetime


@dataclass(frozen=True)
class Period:
    """A class to hold a period of time"""

    start_time: datetime
    end_time: datetime


@dataclass
class ItemDetails:
    """A class to hold details of an item."""

    id: int
    title: str
    vendor: str
    image_urls: list[str]
    link: str
    product_type: str
    published_at: datetime
    created_at: datetime
    variants: list[Variant]
    preorder_period: Period | None = None


class FindMeStoreItemList:
    """A class to scrape the Find Me Store (FMS) list from the specified URL."""

    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            }
        )

    def get_items(
        self, fill_quantity: bool = True, fill_preorder_period: bool = False
    ) -> list[ItemDetails]:
        """Fetches items from the FMS list and optionally fills their quantities."""
        if fill_preorder_period and not fill_quantity:
            raise ValueError("Preorder period is requiring quantity to work.")
        items = self._fetch_items()
        if fill_quantity:
            self._fill_quantities(items)
        if fill_preorder_period:
            self._fill_preorder_period(items)
        return items

    def _fill_preorder_period(self, items: list[ItemDetails]):
        """Fills the preorder period for possibly preorder items. Need the quantity be filled before calling this."""
        for item in items:
            maybe_preorder = False
            for variant in item.variants:
                if variant.quantity > 5000:
                    # This is just a guess
                    maybe_preorder = True
                    break
            if maybe_preorder:
                time.sleep(BREAK_TIME)
                period = self._fetch_preorder_period(item.link)
                if period:
                    item.preorder_period = period

    def _fetch_items(self) -> list[ItemDetails]:
        """Fetches all items from the FMS list."""
        all_items: list[ItemDetails] = []
        page = 1
        while True:
            try:
                # Fetch the first page of products
                items = self._fetch_products(page)
                all_items.extend(items)
                if not items:
                    break  # No products found, exit the loop
                page += 1
            except ValueError as e:
                print(f"Error fetching products: {e}")
                break  # Exit the loop on error

        # Sort items by publish time
        all_items.sort(key=lambda item: item.published_at, reverse=True)

        return all_items

    def _fill_quantities(self, items: list[ItemDetails]) -> None:
        """Fills the quantities for each variant in the items."""
        quantities: Mapping[int, int] = {}
        page = 1
        while True:
            try:
                # Fetch quantities from the search API
                q = self._fetch_quantities(page)
                quantities.update(q)
                if not q:
                    break
                page += 1
            except ValueError as e:
                print(f"Error fetching quantities: {e}")
                break

        for item in items:
            for variant in item.variants:
                variant.quantity = max(quantities.get(variant.id, 0), -1)

    def _fetch_quantities(self, page: int) -> Mapping[int, int]:
        """Fetches the quantities from search API. Returns a mapping of variant IDs to quantities."""
        while True:
            res = self._session.get(
                f"{FMS_BASE_URL}/search?view=preorderjson&q=*&page={page}"
            )
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                print(
                    f"Rate limit exceeded, waiting {RETRY_PERIOD}s before retrying page {page}..."
                )
                time.sleep(RETRY_PERIOD)
            else:
                raise ValueError(
                    f"Failed to fetch search result at page {page}: [{res.status_code}] {res.text}"
                )
        return {
            variant["id"]: variant["inventory_quantity"]
            for product in json.loads(fix_json(res.text))
            for variant in product.get("variants", [])
            if variant["available"]
        }

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parses a timestamp string into a datetime object."""
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z").astimezone(pytz.utc)

    def _parse_product(self, product: dict) -> ItemDetails:
        """Parses a product dictionary into an ItemDetails object."""
        id = product["id"]
        title = product["title"]
        vendor = product.get("vendor", "Unknown Vendor")
        image_urls = [image["src"] for image in product.get("images", [])]
        link = f"{FMS_BASE_URL}/products/{product['handle']}"
        product_type = product.get("product_type", "Unknown Type")
        published_at = self._parse_timestamp(product["published_at"])
        created_at = self._parse_timestamp(product["created_at"])
        variants = [
            Variant(
                id=variant["id"],
                name=variant["title"] if variant["title"] != "Default Title" else "",
                price=variant["price"],
                available=variant["available"],
                quantity=0,
                created_at=self._parse_timestamp(variant["created_at"]),
            )
            for variant in product.get("variants", [])
        ]
        return ItemDetails(
            id,
            title,
            vendor,
            image_urls,
            link,
            product_type,
            published_at,
            created_at,
            variants,
        )

    def _fetch_products(self, page: int) -> list[ItemDetails]:
        """Fetches the products from the FMS list."""
        while True:
            res = self._session.get(
                f"{FMS_BASE_URL}/products.json?limit=250&page={page}"
            )
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                print(
                    f"Rate limit exceeded, waiting {RETRY_PERIOD}s before retrying page {page}..."
                )
                time.sleep(RETRY_PERIOD)
            else:
                raise ValueError(
                    f"Failed to fetch products at page {page}: [{res.status_code}] {res.text}"
                )
        products = res.json().get("products", [])
        return [self._parse_product(product) for product in products]

    def _unify_hyphen_symbol(self, text: str) -> str:
        """Unifies the tilde and hyphen symbols."""
        return re.sub(r"\s*[〜~-]\s*", "-", text).strip()

    def _extract_period(self, text: str) -> Period:
        """Extracts a periods from a string and returns it as datetime objects."""
        text = self._unify_hyphen_symbol(text)

        matches = re.findall(
            r"(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{1,2}-\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{1,2})",
            text,
        )

        if len(matches) != 1:
            raise ValueError(f"Failed to match periods from '{text}'")

        start_str, end_str = matches[0].split("-", 1)

        try:
            jptz = pytz.timezone("Asia/Tokyo")
            start_date = jptz.localize(
                datetime.strptime(f"{start_str.strip()}", "%Y年%m月%d日 %H:%M")
            ).astimezone(pytz.utc)
            end_date = jptz.localize(
                datetime.strptime(f"{end_str.strip()}", "%Y年%m月%d日 %H:%M")
            ).astimezone(pytz.utc)
            return Period(start_date, end_date)
        except ValueError as e:
            raise ValueError(f"Error parsing date from '{text}': {e}")

    def _fetch_preorder_period(self, link: str) -> Period | None:
        """Fetches the preorder period from the product page."""
        while True:
            res = self._session.get(link)
            if res.status_code == 200:
                break
            elif res.status_code == 429:
                print(
                    f"Rate limit exceeded, waiting {RETRY_PERIOD}s before retrying link {link}..."
                )
                time.sleep(RETRY_PERIOD)
            else:
                raise ValueError(
                    f"Failed to fetch product page {link}: [{res.status_code}] {res.text}"
                )

        soup = BeautifulSoup(res.text, "html.parser")
        order_term_elem = soup.select_one("p.orderTerm")
        if not order_term_elem:
            print(f"No order term found from {link}")
            return None

        order_term = order_term_elem.get_text(strip=True)

        try:
            return self._extract_period(order_term)
        except ValueError as e:
            print(f"Failed to extract period for {link}: {e}")
            return None


if __name__ == "__main__":
    fms = FindMeStoreItemList()

    items = fms.get_items(fill_quantity=True, fill_preorder_period=True)
    for item in items:
        print(f"Item: {item.title} (ID: {item.id})")
        print(f"  Vendor: {item.vendor}")
        print(f"  Link: {item.link}")
        print(f"  Published at: {item.published_at}")
        if item.preorder_period:
            print(
                f"  Preorder period: {item.preorder_period.start_time.strftime('%Y/%m/%d %H:%M')} - {item.preorder_period.end_time.strftime('%Y/%m/%d %H:%M')}"
            )
        print(f"  Variants:")
        for variant in item.variants:
            print(
                f"    - Variant ID: {variant.id}, Name: {variant.name}, Price: {variant.price}, Available: {variant.available}, Quantity: {variant.quantity}"
            )
        print()
    print(f"Total items fetched: {len(items)}")
