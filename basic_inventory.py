"""Products, the inventory, and the dialogs that fill it."""

import re
from dataclasses import dataclass, field
from typing import Callable, Optional, TypeVar

from dynamic_inventory import grow_slots

T = TypeVar("T")

NAME_PATTERN = re.compile(r"[\w .-]{1,49}")

MENU = """
1. Add Product
2. Display Products
3. Save and Exit
4. Find Product
5. Display Sorted
6. Remove Product
7. Inventory Report
"""

HEADER = "ID\tName\t\tQuantity\tPrice"


@dataclass
class Product:
    id: int
    name: str
    quantity: int
    price: float

    def value(self) -> float:
        """Stock value of this product: quantity times price."""
        return float(self.quantity) * float(self.price)


@dataclass
class Inventory:
    products: list[Optional[Product]] = field(default_factory=list)
    size: int = 0
    capacity: int = 0
    index: dict[int, Product] = field(default_factory=dict)


def create_inventory(capacity: int) -> Inventory:
    """Return an empty inventory whose block of slots has room for capacity products."""
    return Inventory([None] * capacity, 0, capacity, {})


def valid_name(text: str) -> bool:
    """Say whether text is a product name of 1 to 49 allowed characters."""
    return NAME_PATTERN.fullmatch(text) is not None


def ask(prompt: str, convert: Callable[[str], T], check: Callable[[T], bool] = lambda v: True) -> T:
    """Ask until the answer converts and passes check, then return it."""
    while True:
        text = input(prompt).strip()
        try:
            value = convert(text)
        except ValueError:
            print("Please enter a valid value.")
            continue
        if check(value):
            return value
        print("Value out of range.")


def make_float(text: str) -> float:
    """Convert text to a float, accepting a decimal comma such as 4,50."""
    return float(text.replace(",", ".") if "," in text else text)


def insert_product(inventory: Inventory, product: Product) -> bool:
    """Store the product in the next free slot and in the index, refusing a duplicate ID."""
    if product.id in inventory.index:
        return False
    if inventory.size == inventory.capacity:
        grow_slots(inventory)
    inventory.products[inventory.size] = product
    inventory.index[product.id] = product
    inventory.size += 1
    return True


def ask_product_id(inventory: Inventory) -> int:
    """Ask for a positive product ID that the inventory does not hold yet."""
    while True:
        product_id = ask("Enter product ID: ", int, lambda v: v > 0)
        if product_id in inventory.index:
            print("Product ID already exists.")
            continue
        return product_id


def add_product(inventory: Inventory) -> None:
    """Ask for a product's fields and insert it."""
    product_id = ask_product_id(inventory)
    name = ask("Enter product name: ", str, valid_name)
    quantity = ask("Enter quantity: ", int, lambda v: v >= 0)
    price = ask("Enter price: ", make_float, lambda v: v >= 0.0)
    if insert_product(inventory, Product(product_id, name, quantity, price)):
        print("Product added successfully!")


def format_product(product: Product) -> str:
    """Return the one line of tab-separated text that shows the product."""
    return f"{product.id}\t{product.name}\t\t{product.quantity}\t\t{product.price:.2f}"


def list_products(products: list[Product]) -> None:
    """Print a product list with an empty line before it."""
    print()
    print("Product List:")
    print(HEADER)
    for product in products:
        print(format_product(product))