"""Growth of the inventory's block of slots."""

from typing import Any, Optional


def grow_slots(inventory: Any) -> int:
    """Double the block of slots and return the number of products copied."""
    new_block: list[Optional[Any]] = [None] * (2 * inventory.capacity)
    for i in range(inventory.size):
        new_block[i] = inventory.products[i]
    inventory.products = new_block
    inventory.capacity = 2 * inventory.capacity
    return inventory.size


def free_inventory(inventory: Any) -> None:
    """Release every slot and every index entry of the inventory."""
    inventory.products.clear()
    inventory.products.extend([None] * inventory.capacity)
    inventory.index.clear()
    inventory.size = 0
