from medtriage.models import Patient
from medtriage.bst import PatientBST

bst = PatientBST()

# 1. إدخال مرضى
patients = [
    Patient(50, "Sara", 30, "Chest pain", esi_level=2),
    Patient(30, "Mona", 25, "Fever", esi_level=4),
    Patient(70, "Noura", 45, "Fracture", esi_level=3),
    Patient(20, "Lama", 22, "Headache", esi_level=4),
    Patient(40, "Rofida", 24, "Dizziness", esi_level=3),
    Patient(60, "Huda", 50, "Shortness of breath", esi_level=2),
    Patient(80, "Amal", 35, "Allergy", esi_level=4),
]

for p in patients:
    bst.insert(p)

print("In-order IDs:", [p.patient_id for p in bst.inorder_traversal()])
print("Search ID 40:", bst.search(40))
print("Search missing ID 99:", bst.search(99))

# 2. اختبار حالات الحذف الثلاث
# حالة 1: حذف عقدة بدون أبناء (20)
print("Delete 0-child (20):", bst.delete(20))
print("After deleting 20:", [p.patient_id for p in bst.inorder_traversal()])

# حالة 2: حذف عقدة بابن واحد (30 - بقي لها 40 فقط)
print("Delete 1-child (30):", bst.delete(30))
print("After deleting 30:", [p.patient_id for p in bst.inorder_traversal()])

# حالة 3: حذف عقدة بابنين (50 - الجذر، له 40 يسار و70 يمين)
print("Delete 2-children (50):", bst.delete(50))
print("After deleting 50:", [p.patient_id for p in bst.inorder_traversal()])

# 3. اختبار الشجرة المائلة (Skewed tree - إدخال تصاعدي متسلسل)
skewed = PatientBST()
for pid in [1, 2, 3, 4, 5]:
    skewed.insert(Patient(pid, f"Patient-{pid}", 20 + pid))
print("Skewed in-order:", [p.patient_id for p in skewed.inorder_traversal()])
print("Skewed search 5:", skewed.search(5))