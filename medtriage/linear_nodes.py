from typing import Any


class Node:
    """Singly linked node for linear data structures (stack and queue)."""

    def __init__(self, data: Any, next_node: "Node | None" = None):
        self.data = data
        self.next: Node | None = next_node

    def __repr__(self) -> str:
        return f"Node(data={self.data!r})"


class PriorityNode:
    """Node for priority queue supporting priority level and anti-starvation wait_cycles."""

    def __init__(
        self,
        data: Any,
        priority: int = 5,
        wait_cycles: int = 0,
        next_node: "PriorityNode | None" = None,
    ):
        self.data = data
        self.priority = priority
        self.wait_cycles = wait_cycles
        self.next: PriorityNode | None = next_node

    def __repr__(self) -> str:
        return (
            f"PriorityNode(data={self.data!r}, priority={self.priority}, "
            f"wait_cycles={self.wait_cycles})"
        )