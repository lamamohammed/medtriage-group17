from typing import Any
from medtriage.linear_nodes import Node


class LinkedStack:
    """Linked-list stack (LIFO) supporting Undo operations for triage and lab/pharmacy queues."""

    def __init__(self):
        self._top: Node | None = None
        self._size: int = 0

    def is_empty(self) -> bool:
        """Return True if the stack has no elements."""
        return self._top is None

    def __len__(self) -> int:
        return self._size

    def push(self, item: Any) -> None:
        """Push an action or state onto the top of the stack."""
        self._top = Node(item, self._top)
        self._size += 1

    def pop(self) -> Any:
        """Pop and return the most recent item, or None if empty."""
        if self._top is None:
            return None
        popped = self._top.data
        self._top = self._top.next
        self._size -= 1
        return popped

    def peek(self) -> Any:
        """Return the top item without removing it, or None if empty."""
        return self._top.data if self._top is not None else None

    def undo(self) -> Any:
        """Undo the last recorded action (alias for pop)."""
        return self.pop()

    def to_list(self) -> list[Any]:
        """Return items from top to bottom as a list."""
        items: list[Any] = []
        current = self._top
        while current is not None:
            items.append(current.data)
            current = current.next
        return items