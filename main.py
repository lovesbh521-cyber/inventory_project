"""The menu and the dialogs that drive the inventory."""

from basic_inventory import (
    MENU,
    Inventory,
    add_product,
    ask,
    create_inventory,
    format_product,
    list_products,
)
from dynamic_inventory import free_inventory
from extended_inventory import (
    find_product,
    low_stock,
    most_valuable,
    remove_product,
    sorted_products,
    stock_value,
)
from file_inventory import load_from_file, save_to_file

FILENAME = "inventory.csv"
SORT_CHOICES = {"1": "name", "2": "quantity", "3": "price", "4": "value"}


def display_products(inventory: Inventory) -> None:
    """List every product in slot order."""
    list_products(inventory.products[: inventory.size])


def display_sorted(inventory: Inventory) -> None:
    """Ask for a sorting key and list the products by it."""
    key = ask("Sort by (1 name, 2 quantity, 3 price, 4 value): ", str, lambda v: v in SORT_CHOICES)
    list_products(sorted_products(inventory, SORT_CHOICES[key]))


def find_and_show(inventory: Inventory) -> None:
    """Ask for an ID and list that one product, or say it is not there."""
    product_id = ask("Enter product ID: ", int, lambda v: v > 0)
    product = find_product(inventory, product_id)
    if product is None:
        print("Product not found.")
        return
    list_products([product])


def remove_and_confirm(inventory: Inventory) -> None:
    """Ask for an ID, remove that product, and report the result."""
    product_id = ask("Enter product ID: ", int, lambda v: v > 0)
    if remove_product(inventory, product_id):
        print("Product removed.")
    else:
        print("Product not found.")


def show_report(inventory: Inventory) -> None:
    """Print the count, the stock value, the low stock products, and the most valuable one."""
    print()
    print(f"Number of products: {inventory.size}")
    print(f"Total stock value: {stock_value(inventory):.2f}")
    print()
    print("Low stock products:")
    low = low_stock(inventory)
    if low:
        for product in low:
            print(format_product(product))
    else:
        print("None")
    print()
    print("Most valuable product:")
    best = most_valuable(inventory)
    if best is not None:
        print(format_product(best))
    else:
        print("None")


def main() -> None:
    """Run the menu until the user saves and exits or the answers run out."""
    inventory = create_inventory(5)
    load_from_file(inventory, FILENAME)
    while True:
        print(MENU)
        try:
            choice = input("Enter your choice: ").strip()
        except EOFError:
            free_inventory(inventory)
            break
        if choice == "1":
            add_product(inventory)
        elif choice == "2":
            display_products(inventory)
        elif choice == "3":
            save_to_file(inventory, FILENAME)
            free_inventory(inventory)
            break
        elif choice == "4":
            find_and_show(inventory)
        elif choice == "5":
            display_sorted(inventory)
        elif choice == "6":
            remove_and_confirm(inventory)
        elif choice == "7":
            show_report(inventory)
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()