from typing import Optional


class GeneralTreeNode:
    """Models hospital -> wing -> ward -> bed hierarchy using explicit links."""

    def __init__(
        self,
        name: str,
        node_type: str,
        is_occupied: bool = False,
        first_child: Optional["GeneralTreeNode"] = None,
        next_sibling: Optional["GeneralTreeNode"] = None,
    ) -> None:
        self.name = name
        self.node_type = node_type
        self.is_occupied = is_occupied
        self.first_child = first_child
        self.next_sibling = next_sibling

    def __repr__(self) -> str:
        return (
            f"GeneralTreeNode(name={self.name!r}, type={self.node_type!r}, "
            f"occupied={self.is_occupied})"
        )


class BinaryTreeNode:
    """Models Yes/No symptom screening decision tree node."""

    def __init__(
        self,
        text: str,
        left: Optional["BinaryTreeNode"] = None,
        right: Optional["BinaryTreeNode"] = None,
        recommendation: Optional[str] = None,
    ) -> None:
        self.text = text
        self.left = left
        self.right = right
        self.recommendation = recommendation

    def is_leaf(self) -> bool:
        """Returns True if this node has no Yes/No child branches."""
        return self.left is None and self.right is None

    def __repr__(self) -> str:
        return f"BinaryTreeNode(text={self.text!r}, recommendation={self.recommendation!r})"