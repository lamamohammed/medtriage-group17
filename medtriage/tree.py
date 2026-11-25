from typing import Optional
from medtriage.node import BinaryTreeNode, GeneralTreeNode


class GeneralTree:
    """General tree representing Hospital -> Wings -> Wards -> Beds."""

    def __init__(self, root: Optional[GeneralTreeNode] = None) -> None:
        self.root = root

    def add_child(self, parent: GeneralTreeNode, child: GeneralTreeNode) -> None:
        """Attaches child to parent using first_child and next_sibling pointers."""
        if parent.first_child is None:
            parent.first_child = child
            return

        current = parent.first_child
        while current.next_sibling is not None:
            current = current.next_sibling
        current.next_sibling = child

    def count_total_beds(
        self, node: Optional[GeneralTreeNode] = None, _first_call: bool = True
    ) -> int:
        """Recursively counts total bed nodes in the subtree."""
        current = self.root if (_first_call and node is None) else node
        if current is None:
            return 0

        is_bed = 1 if current.node_type == "bed" else 0
        child_total = self.count_total_beds(current.first_child, _first_call=False)
        sibling_total = (
            0
            if _first_call
            else self.count_total_beds(current.next_sibling, _first_call=False)
        )
        return is_bed + child_total + sibling_total

    def count_free_beds(
        self, node: Optional[GeneralTreeNode] = None, _first_call: bool = True
    ) -> int:
        """Recursively counts unoccupied bed nodes in the subtree."""
        current = self.root if (_first_call and node is None) else node
        if current is None:
            return 0

        is_free_bed = 1 if (current.node_type == "bed" and not current.is_occupied) else 0
        child_free = self.count_free_beds(current.first_child, _first_call=False)
        sibling_free = (
            0
            if _first_call
            else self.count_free_beds(current.next_sibling, _first_call=False)
        )
        return is_free_bed + child_free + sibling_free

    def occupancy_percentage(
        self, subtree_root: Optional[GeneralTreeNode] = None
    ) -> float:
        """Calculates bed occupancy percentage for the whole tree or a given wing/ward node."""
        target = subtree_root if subtree_root is not None else self.root
        if target is None:
            return 0.0

        total = self.count_total_beds(target, _first_call=True)
        if total == 0:
            return 0.0

        free = self.count_free_beds(target, _first_call=True)
        return ((total - free) / total) * 100.0

    def allocate_first_free_bed(
        self, node: Optional[GeneralTreeNode] = None, _first_call: bool = True
    ) -> Optional[str]:
        """Finds the first unoccupied bed recursively, marks it occupied, and returns its name."""
        current = self.root if (_first_call and node is None) else node
        if current is None:
            return None

        if current.node_type == "bed" and not current.is_occupied:
            current.is_occupied = True
            return current.name

        found_in_child = self.allocate_first_free_bed(
            current.first_child, _first_call=False
        )
        if found_in_child is not None:
            return found_in_child

        if _first_call:
            return None
        return self.allocate_first_free_bed(current.next_sibling, _first_call=False)

    def release_bed(
        self,
        bed_name: str,
        node: Optional[GeneralTreeNode] = None,
        _first_call: bool = True,
    ) -> bool:
        """Finds a bed by name and marks it free (is_occupied = False). Returns True if found."""
        current = self.root if (_first_call and node is None) else node
        if current is None:
            return False

        if current.node_type == "bed" and current.name == bed_name:
            current.is_occupied = False
            return True

        if self.release_bed(bed_name, current.first_child, _first_call=False):
            return True

        if _first_call:
            return False
        return self.release_bed(bed_name, current.next_sibling, _first_call=False)


class BinaryTree:
    """Binary decision tree for Yes/No symptom screening (left = Yes, right = No)."""

    def __init__(self, root: Optional[BinaryTreeNode] = None) -> None:
        self.root = root

    def step(
        self, current: Optional[BinaryTreeNode], answer: str
    ) -> Optional[BinaryTreeNode]:
        """Moves to left (Yes) or right (No) child based on answer; returns None if invalid/end."""
        if current is None:
            return None

        normalized = answer.strip().lower()
        if normalized in ("yes", "y", "نعم"):
            return current.left
        if normalized in ("no", "n", "لا"):
            return current.right
        return current

    def is_recommendation(self, node: Optional[BinaryTreeNode]) -> bool:
        """Returns True if the node reached a triage recommendation (leaf)."""
        if node is None:
            return False
        return node.is_leaf() or node.recommendation is not None

    def get_recommendation(self, node: Optional[BinaryTreeNode]) -> Optional[str]:
        """Returns the triage recommendation text if present on the node."""
        if node is None:
            return None
        return node.recommendation