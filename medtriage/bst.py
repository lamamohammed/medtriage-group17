from medtriage.models import BSTNode, Patient


class PatientBST:
    """Binary Search Tree for fast O(log n) patient lookup, insertion, and discharge."""

    def __init__(self):
        self.root: BSTNode | None = None

    def insert(self, patient: Patient) -> None:
        """Insert a new Patient into the BST keyed by patient_id."""
        self.root = self._insert_recursive(self.root, patient)

    def _insert_recursive(self, node: BSTNode | None, patient: Patient) -> BSTNode:
        if node is None:
            return BSTNode(patient)

        if patient.patient_id < node.patient.patient_id:
            node.left = self._insert_recursive(node.left, patient)
        elif patient.patient_id > node.patient.patient_id:
            node.right = self._insert_recursive(node.right, patient)
        else:
            node.patient = patient

        return node

    def search(self, patient_id: int) -> Patient | None:
        """Search for a patient by patient_id. Returns Patient or None."""
        current = self.root
        while current is not None:
            if patient_id == current.patient.patient_id:
                return current.patient
            elif patient_id < current.patient.patient_id:
                current = current.left
            else:
                current = current.right
        return None

    def delete(self, patient_id: int) -> bool:
        """
        Discharge/remove a patient by patient_id handling all 3 BST deletion cases:
        1. Leaf node (0 children)
        2. Node with 1 child
        3. Node with 2 children (replaced with in-order successor)
        Returns True if deleted, False if patient_id not found.
        """
        if self.search(patient_id) is None:
            return False
        self.root = self._delete_recursive(self.root, patient_id)
        return True

    def _delete_recursive(self, node: BSTNode | None, patient_id: int) -> BSTNode | None:
        if node is None:
            return None

        if patient_id < node.patient.patient_id:
            node.left = self._delete_recursive(node.left, patient_id)
        elif patient_id > node.patient.patient_id:
            node.right = self._delete_recursive(node.right, patient_id)
        else:
            # Case 1: 0 children (leaf)
            if node.left is None and node.right is None:
                return None
            # Case 2: 1 child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # Case 3: 2 children -> find in-order successor (min in right subtree)
            successor = self._min_value_node(node.right)
            node.patient = successor.patient
            node.right = self._delete_recursive(node.right, successor.patient.patient_id)

        return node

    def _min_value_node(self, node: BSTNode) -> BSTNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def inorder_traversal(self) -> list[Patient]:
        """Return all patients sorted in ascending order of patient_id."""
        result: list[Patient] = []
        self._inorder_recursive(self.root, result)
        return result

    def _inorder_recursive(self, node: BSTNode | None, result: list[Patient]) -> None:
        if node is not None:
            self._inorder_recursive(node.left, result)
            result.append(node.patient)
            self._inorder_recursive(node.right, result)