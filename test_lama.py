from medtriage.node import BinaryTreeNode, GeneralTreeNode
from medtriage.tree import BinaryTree, GeneralTree

# 1. اختبار GeneralTree (الأسرة ونسبة الإشغال والتخصيص والتحرير)
hosp = GeneralTreeNode("MedTriage ED", "hospital")
wing = GeneralTreeNode("North Wing", "wing")
ward = GeneralTreeNode("Trauma-A", "ward")
b1 = GeneralTreeNode("Bed-1", "bed", is_occupied=False)
b2 = GeneralTreeNode("Bed-2", "bed", is_occupied=False)

gtree = GeneralTree(hosp)
gtree.add_child(hosp, wing)
gtree.add_child(wing, ward)
gtree.add_child(ward, b1)
gtree.add_child(ward, b2)

print("Total beds:", gtree.count_total_beds())
print("Free beds before:", gtree.count_free_beds())
print("Occupancy % before:", gtree.occupancy_percentage())

assigned = gtree.allocate_first_free_bed()
print("Allocated bed:", assigned)
print("Free beds after allocate:", gtree.count_free_beds())
print("Occupancy % after allocate:", gtree.occupancy_percentage())

gtree.release_bed(assigned)
print("Free beds after release:", gtree.count_free_beds())
print("Occupancy % after release:", gtree.occupancy_percentage())

# 2. اختبار BinaryTree (فرز الأعراض نعم/لا)
leaf_yes = BinaryTreeNode("Severe chest pain", recommendation="ESI-2: Urgent Cardiac Care")
leaf_no = BinaryTreeNode("Mild symptoms", recommendation="ESI-4: Standard Triage")
root_q = BinaryTreeNode("Is the patient having chest pain?", left=leaf_yes, right=leaf_no)

btree = BinaryTree(root_q)
step1 = btree.step(btree.root, "yes")
print("Step 1 node:", step1.text)
print("Is recommendation?:", btree.is_recommendation(step1))
print("Recommendation:", btree.get_recommendation(step1))





# 3. حالات حافة (شجرة فارغة + امتلاء جميع الأسرة + إجابة No)
empty_tree = GeneralTree(None)
print("Empty tree total beds:", empty_tree.count_total_beds())
print("Empty tree occupancy %:", empty_tree.occupancy_percentage())
print("Empty tree allocate:", empty_tree.allocate_first_free_bed())

# تعبئة كل الأسرة في gtree
print("Allocate 2nd bed:", gtree.allocate_first_free_bed())
print("Allocate when full:", gtree.allocate_first_free_bed())
print("Occupancy % when full:", gtree.occupancy_percentage())

# تجربة مسار No في BinaryTree
step_no = btree.step(btree.root, "no")
print("Step No node:", step_no.text, "| Rec:", btree.get_recommendation(step_no))



# للتاكد من امتلاء الاسره 
print("Allocate when truly full:", gtree.allocate_first_free_bed())