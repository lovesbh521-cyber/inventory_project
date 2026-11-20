"""Saving the inventory to inventory.csv and loading it back."""

import csv
from typing import Optional

from basic_inventory import Product, Inventory, create_inventory, insert_product, valid_name

FIELDNAMES = ["id", "name", "quantity", "price"]


def save_to_file(inventory: Inventory, filename: str) -> bool:
    """Write the products in slot order to the CSV file and say whether it worked."""
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for product in inventory.products[: inventory.size]:
                writer.writerow(
                    {
                        "id": product.id,
                        "name": product.name,
                        "quantity": product.quantity,
                        "price": product.price,
                    }
                )
    except OSError:
        print("Error opening file for saving!")
        return False
    print("Data saved successfully.")
    return True


def parse_product(row: list[str]) -> Optional[Product]:
    """Turn one CSV row into a product, or return None when the row is damaged."""
    if len(row) != len(FIELDNAMES):
        return None
    try:
        product_id = int(row[0])
        name = row[1]
        quantity = int(row[2])
        price = float(row[3])
    except ValueError:
        return None
    if product_id <= 0 or not valid_name(name) or quantity < 0 or price < 0.0:
        return None
    return Product(product_id, name, quantity, price)


def load_from_file(inventory: Inventory, filename: str) -> None:
    """Fill the inventory from the CSV file, skipping every damaged line."""
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    except OSError:
        print("Error opening file for loading!")
        return

    damaged = 0
    for row in rows[1:] if rows else []:
        product = parse_product(row)
        if product is None or not insert_product(inventory, product):
            damaged += 1
    print("Data loaded successfully.")
    if damaged:
        print(f"Skipped {damaged} damaged lines.")


def new_inventory_from_file(filename: str, capacity: int = 5) -> Inventory:
    """Return a fresh inventory filled from the CSV file."""
    inventory = create_inventory(capacity)
    load_from_file(inventory, filename)
    return inventory