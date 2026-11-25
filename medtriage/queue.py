from typing import Any
from medtriage.linear_nodes import Node, PriorityNode


class LinkedQueue:
    """FIFO linked queue used for lab and pharmacy service lines."""

    def __init__(self):
        self._front: Node | None = None
        self._rear: Node | None = None
        self._size: int = 0

    def is_empty(self) -> bool:
        return self._front is None

    def __len__(self) -> int:
        return self._size

    def enqueue(self, item: Any) -> None:
        """Add item to the rear of the queue."""
        new_node = Node(item)
        if self._rear is None:
            self._front = self._rear = new_node
        else:
            self._rear.next = new_node
            self._rear = new_node
        self._size += 1

    def dequeue(self) -> Any:
        """Remove and return item from the front of the queue, or None if empty."""
        if self._front is None:
            return None
        removed = self._front.data
        self._front = self._front.next
        if self._front is None:
            self._rear = None
        self._size -= 1
        return removed

    def peek(self) -> Any:
        """Return the front item without removing it, or None if empty."""
        return self._front.data if self._front is not None else None

    def to_list(self) -> list[Any]:
        items: list[Any] = []
        current = self._front
        while current is not None:
            items.append(current.data)
            current = current.next
        return items


class PriorityQueue:
    """
    Priority queue (lower priority value = higher urgency, e.g., ESI 1 > ESI 5)
    with wait_cycles anti-starvation aging.
    """

    def __init__(self, aging_threshold: int = 3):
        self._head: PriorityNode | None = None
        self._size: int = 0
        self.aging_threshold = aging_threshold

    def is_empty(self) -> bool:
        return self._head is None

    def __len__(self) -> int:
        return self._size

    def _effective_priority(self, node: PriorityNode) -> int:
        """Boost priority (lower number) as wait_cycles reaches aging_threshold."""
        boost = node.wait_cycles // self.aging_threshold
        return max(1, node.priority - boost)

    def enqueue(self, item: Any, priority: int = 5) -> None:
        """Insert item ordered by effective priority (tie-breaker: FIFO)."""
        new_node = PriorityNode(data=item, priority=priority, wait_cycles=0)
        self._size += 1

        if self._head is None or self._effective_priority(new_node) < self._effective_priority(self._head):
            new_node.next = self._head
            self._head = new_node
            return

        current = self._head
        while (
            current.next is not None
            and self._effective_priority(current.next) <= self._effective_priority(new_node)
        ):
            current = current.next

        new_node.next = current.next
        current.next = new_node

    def tick_wait_cycles(self) -> None:
        """Increment wait_cycles for all waiting nodes and re-order to prevent starvation."""
        if self._head is None:
            return

        nodes: list[PriorityNode] = []
        current = self._head
        while current is not None:
            nxt = current.next
            current.next = None
            current.wait_cycles += 1
            nodes.append(current)
            current = nxt

        # Sort by effective priority ascending, preserving relative order on ties
        nodes.sort(key=lambda n: self._effective_priority(n))

        self._head = None
        tail: PriorityNode | None = None
        for n in nodes:
            if self._head is None:
                self._head = tail = n
            else:
                tail.next = n  # type: ignore[union-attr]
                tail = n

    def dequeue(self) -> Any:
        """Remove and return highest-urgency item, or None if empty."""
        if self._head is None:
            return None
        removed = self._head.data
        self._head = self._head.next
        self._size -= 1
        return removed

    def peek(self) -> Any:
        return self._head.data if self._head is not None else None

    def items_with_cycles(self) -> list[tuple[Any, int, int]]:
        """Return list of (data, base_priority, wait_cycles) from front to back."""
        result: list[tuple[Any, int, int]] = []
        current = self._head
        while current is not None:
            result.append((current.data, current.priority, current.wait_cycles))
            current = current.next
        return result