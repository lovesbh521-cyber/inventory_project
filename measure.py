"""The numbers for the report: lookup times and the price of growth."""

import contextlib
import io
import random
from time import perf_counter

from basic_inventory import Product, Inventory, create_inventory, insert_product
from extended_inventory import find_product, find_product_linear
from file_inventory import load_from_file, save_to_file

SIZES = [2000, 4000, 8000, 16000]
LOOKUPS = 1000
FILENAME = "measure_inventory.csv"


def build(n: int) -> tuple[Inventory, int, int]:
    """Fill an inventory with n products and return it with its doublings and copies."""
    inventory = create_inventory(5)
    doublings = 0
    copies = 0
    for product_id in range(1, n + 1):
        product = Product(product_id, f"Part {product_id}", product_id % 100, 0.5 + product_id % 50)
        if inventory.size == inventory.capacity:
            doublings += 1
            copies += inventory.size
        insert_product(inventory, product)
    return inventory, doublings, copies


def linear_time(inventory: Inventory, ids: list[int]) -> float:
    """Return the seconds that 1,000 lookups by walking the slots take."""
    start = perf_counter()
    for product_id in ids:
        find_product_linear(inventory, product_id)
    return perf_counter() - start


def index_time(inventory: Inventory, ids: list[int]) -> float:
    """Return the seconds that 1,000 lookups through the index take."""
    start = perf_counter()
    for product_id in ids:
        find_product(inventory, product_id)
    return perf_counter() - start


def row(n: int) -> tuple[int, float, float, int, int, int]:
    """Measure one row of the table."""
    inventory, doublings, copies = build(n)
    rng = random.Random(n)
    ids = [rng.randint(1, n) for _ in range(LOOKUPS)]

    seconds_linear = linear_time(inventory, ids)
    seconds_index = index_time(inventory, ids)

    with contextlib.redirect_stdout(io.StringIO()):
        assert save_to_file(inventory, FILENAME) is True
        reloaded = create_inventory(5)
        load_from_file(reloaded, FILENAME)
    assert reloaded.size == inventory.size
    assert reloaded.products[: reloaded.size] == inventory.products[: inventory.size]

    return n, seconds_linear, seconds_index, inventory.capacity, doublings, copies


def main() -> None:
    """Print the measurement table."""
    print(f"   n   linear (s)   index (s)   capacity   doublings   copies")
    for n in SIZES:
        number, seconds_linear, seconds_index, capacity, doublings, copies = row(n)
        print(
            f"{number:>5}   {seconds_linear:>10.6f}   {seconds_index:>9.6f}"
            f"   {capacity:>8}   {doublings:>9}   {copies:>6}"
        )


if __name__ == "__main__":
    main()