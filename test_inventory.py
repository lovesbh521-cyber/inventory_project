"""The tests that show the program does what its specification says."""

import contextlib
import io
import os
import tempfile

from basic_inventory import Product, Inventory, create_inventory, insert_product
from extended_inventory import (
    find_product,
    find_product_linear,
    low_stock,
    most_valuable,
    remove_product,
    sorted_products,
    stock_value,
)
from file_inventory import load_from_file, save_to_file


def product(product_id: int, name: str = "Part", quantity: int = 1, price: float = 1.0) -> Product:
    """Return a product for the tests to place in an inventory."""
    return Product(product_id, name, quantity, price)


def filled(*products: Product) -> Inventory:
    """Return an inventory that starts at capacity 5 and holds these products."""
    inventory = create_inventory(5)
    for item in products:
        insert_product(inventory, item)
    return inventory


def test_create_inventory() -> None:
    """A new inventory has no products, five empty slots, and an empty index."""
    inventory = create_inventory(5)
    assert inventory.size == 0
    assert inventory.capacity == 5
    assert inventory.products == [None, None, None, None, None]
    assert inventory.index == {}


def test_growth() -> None:
    """The sixth product doubles the capacity and keeps all six products in order."""
    items = [product(i, f"Part{i}") for i in range(1, 7)]
    inventory = filled(*items)
    assert inventory.capacity == 10
    assert inventory.size == 6
    assert inventory.products[:6] == items
    assert inventory.products[6:] == [None] * 4


def test_duplicate_id_is_refused() -> None:
    """A second product with an ID that is already there changes nothing."""
    first = product(101, "Ball bearing 6204", 40, 4.5)
    inventory = filled(first)
    before_products = inventory.products[:]
    before_index = dict(inventory.index)
    assert insert_product(inventory, product(101, "Shaft", 5, 12.0)) is False
    assert inventory.size == 1
    assert inventory.products == before_products
    assert inventory.index == before_index


def test_index_and_linear_search_agree() -> None:
    """Both ways of finding a product give the same answer, found or not."""
    inventory = filled(product(101, "Ball bearing 6204"), product(102, "Shaft"))
    for product_id in (101, 102, 999):
        by_index = find_product(inventory, product_id)
        by_slots = find_product_linear(inventory, product_id)
        assert by_index is by_slots
        if product_id == 999:
            assert by_index is None


def test_remove_first_middle_and_last() -> None:
    """Removing any product keeps the order, updates the index, and frees the last slot."""
    inventory = filled(
        product(1, "A"), product(2, "B"), product(3, "C"), product(4, "D")
    )
    assert remove_product(inventory, 1) is True
    assert inventory.products == [inventory.index[2], inventory.index[3], inventory.index[4], None, None]
    assert inventory.size == 3 and inventory.capacity == 5
    assert 1 not in inventory.index

    assert remove_product(inventory, 3) is True
    assert inventory.products[:2] == [inventory.index[2], inventory.index[4]]
    assert inventory.products[2:] == [None, None, None]
    assert 3 not in inventory.index

    assert remove_product(inventory, 4) is True
    assert inventory.products[:1] == [inventory.index[2]]
    assert inventory.products[1:] == [None] * 4
    assert inventory.size == 1
    assert remove_product(inventory, 4) is False


def test_sorting() -> None:
    """Names go from A to Z, numbers go from the largest down, and the slots keep their order."""
    inventory = filled(
        product(1, "Shaft", 5, 12.0),
        product(2, "Ball bearing 6204", 40, 4.5),
        product(3, "Spur gear", 12, 18.9),
    )
    before = inventory.products[:]
    assert [p.name for p in sorted_products(inventory, "name")] == [
        "Ball bearing 6204",
        "Shaft",
        "Spur gear",
    ]
    assert [p.price for p in sorted_products(inventory, "price")] == [18.9, 12.0, 4.5]
    assert [p.quantity for p in sorted_products(inventory, "quantity")] == [40, 12, 5]
    assert [p.id for p in sorted_products(inventory, "value")] == [3, 2, 1]
    assert inventory.products == before


def test_report_numbers() -> None:
    """The count, the stock value, the low stock list, and the most valuable one are right."""
    inventory = filled(
        product(1, "Shaft", 5, 12.0),
        product(2, "Ball bearing 6204", 40, 4.5),
        product(3, "Spur gear", 12, 18.9),
    )
    assert inventory.size == 3
    assert stock_value(inventory) == 5 * 12.0 + 40 * 4.5 + 12 * 18.9
    assert [p.id for p in low_stock(inventory)] == [1]
    assert [p.id for p in low_stock(inventory, level=13)] == [1, 3]
    assert most_valuable(inventory).id == 3
    assert most_valuable(create_inventory(5)) is None


def test_round_trip() -> None:
    """Saving and loading into a new inventory gives back exactly the same products."""
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "inventory.csv")
        inventory = filled(
            product(101, "Ball bearing 6204", 40, 4.5),
            product(102, "Shaft", 5, 12.0),
            product(103, "Spur gear", 12, 18.9),
        )
        with contextlib.redirect_stdout(io.StringIO()):
            assert save_to_file(inventory, filename) is True
            back = create_inventory(5)
            load_from_file(back, filename)
        assert back.size == inventory.size
        assert back.products[: back.size] == inventory.products[: inventory.size]


def test_damaged_lines_are_skipped() -> None:
    """Only the valid lines of a damaged file arrive."""
    content = "\n".join(
        [
            "id,name,quantity,price",
            "101,Ball bearing 6204,40,4.5",
            "102,Shaft,abc,12.0",
            "103,Spur gear,12,-3.0",
            "104,Hex bolt M8,400",
            "105,Bad name!,5,1.0",
            "101,Duplicate ID,1,1.0",
            "106,O-ring 20x2,150,0.3",
        ]
    )
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "inventory.csv")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            f.write(content + "\n")
        inventory = create_inventory(5)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            load_from_file(inventory, filename)
    assert inventory.size == 2
    assert [p.id for p in inventory.products[:2]] == [101, 106]
    assert "Data loaded successfully." in out.getvalue()
    assert "Skipped 5 damaged lines." in out.getvalue()


def test_missing_file_is_not_an_error() -> None:
    """A file that is not there leaves an empty inventory and raises nothing."""
    with tempfile.TemporaryDirectory() as folder:
        filename = os.path.join(folder, "missing.csv")
        inventory = create_inventory(5)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            load_from_file(inventory, filename)
    assert inventory.size == 0
    assert inventory.capacity == 5
    assert inventory.index == {}
    assert "Error opening file for loading!" in out.getvalue()


TESTS = [
    test_create_inventory,
    test_growth,
    test_duplicate_id_is_refused,
    test_index_and_linear_search_agree,
    test_remove_first_middle_and_last,
    test_sorting,
    test_report_numbers,
    test_round_trip,
    test_damaged_lines_are_skipped,
    test_missing_file_is_not_an_error,
]


def run_tests() -> None:
    """Run every test and print one line for each of them."""
    failed = 0
    for test in TESTS:
        try:
            test()
        except AssertionError:
            failed += 1
            print(f"FAIL  {test.__name__}")
        else:
            print(f"ok    {test.__name__}")
    print()
    print(f"{len(TESTS) - failed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
