"""Finding, removing, sorting, and summarizing the inventory."""

from typing import Optional

from basic_inventory import Product, Inventory

SORT_KEYS = {
    "name": lambda p: p.name,
    "quantity": lambda p: p.quantity,
    "price": lambda p: p.price,
    "value": lambda p: p.value(),
}


def find_product(inventory: Inventory, product_id: int) -> Optional[Product]:
    """Return the product with this ID through the index, or None."""
    return inventory.index.get(product_id)


def find_product_linear(inventory: Inventory, product_id: int) -> Optional[Product]:
    """Return the product with this ID by walking the slots, or None."""
    for product in inventory.products[: inventory.size]:
        if product.id == product_id:
            return product
    return None


def remove_product(inventory: Inventory, product_id: int) -> bool:
    """Remove the product, close the gap it leaves, and say whether it was there."""
    for slot in range(inventory.size):
        if inventory.products[slot].id == product_id:
            for shift in range(slot, inventory.size - 1):
                inventory.products[shift] = inventory.products[shift + 1]
            inventory.products[inventory.size - 1] = None
            del inventory.index[product_id]
            inventory.size -= 1
            return True
    return False


def sorted_products(inventory: Inventory, key: str) -> list[Product]:
    """Return a new list sorted by name upwards or by a number downwards."""
    products = list(inventory.products[: inventory.size])
    if key == "name":
        return sorted(products, key=SORT_KEYS["name"])
    return sorted(products, key=SORT_KEYS[key], reverse=True)


def stock_value(inventory: Inventory) -> float:
    """Return the sum of quantity times price over all products."""
    return sum(product.value() for product in inventory.products[: inventory.size])


def low_stock(inventory: Inventory, level: int = 10) -> list[Product]:
    """Return the products whose quantity is below level."""
    return [p for p in inventory.products[: inventory.size] if p.quantity < level]


def most_valuable(inventory: Inventory) -> Optional[Product]:
    """Return the product with the highest stock value, or None for an empty inventory."""
    if inventory.size == 0:
        return None
    return max(inventory.products[: inventory.size], key=lambda p: p.value())
