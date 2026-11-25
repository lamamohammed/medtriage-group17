# medtriage-group17
An integrated Data Structures system built in Python for emergency department triage, symptom screening, patient record lookup, bed allocation, service queues, and action undo support.

## Project Structure

```text
medtriage-group17/
├── medtriage/
│   ├── __init__.py
│   ├── node.py            # GeneralTreeNode & BinaryTreeNode
│   ├── tree.py            # GeneralTree (beds/occupancy) & BinaryTree (Yes/No triage)
│   ├── models.py          # Patient & BSTNode
│   ├── bst.py             # PatientBST (insert, search, inorder, 3 deletion cases)
│   ├── linear_nodes.py    # Node & PriorityNode
│   ├── stack.py           # LinkedStack (LIFO + Undo)
│   └── queue.py           # LinkedQueue (FIFO) & PriorityQueue (wait_cycles aging)
├── main.py                # Integrated MedTriageSystem runner & demo
├── test_lama.py           # Tests for GeneralTree & BinaryTree (including edge cases)
├── test_lama_bst.py       # Tests for PatientBST (0, 1, 2 children + skewed tree)
├── test_lama_linear.py    # Tests for LinkedStack, LinkedQueue & PriorityQueue aging
└── README.md