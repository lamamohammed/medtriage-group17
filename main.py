from medtriage.models import Patient
from medtriage.node import BinaryTreeNode, GeneralTreeNode
from medtriage.tree import BinaryTree, GeneralTree
from medtriage.bst import PatientBST
from medtriage.stack import LinkedStack
from medtriage.queue import LinkedQueue, PriorityQueue


def build_default_hospital_tree() -> GeneralTree:
    hosp = GeneralTreeNode("MedTriage Hospital", "hospital")
    ed_wing = GeneralTreeNode("Emergency Wing", "wing")
    trauma_ward = GeneralTreeNode("Trauma Ward", "ward")
    obs_ward = GeneralTreeNode("Observation Ward", "ward")

    bed1 = GeneralTreeNode("Bed-101", "bed", is_occupied=False)
    bed2 = GeneralTreeNode("Bed-102", "bed", is_occupied=False)
    bed3 = GeneralTreeNode("Bed-201", "bed", is_occupied=False)

    tree = GeneralTree(hosp)
    tree.add_child(hosp, ed_wing)
    tree.add_child(ed_wing, trauma_ward)
    tree.add_child(ed_wing, obs_ward)
    tree.add_child(trauma_ward, bed1)
    tree.add_child(trauma_ward, bed2)
    tree.add_child(obs_ward, bed3)
    return tree


def build_default_triage_tree() -> BinaryTree:
    esi_2 = BinaryTreeNode("High Risk", recommendation="ESI-2: Urgent Care (Priority 2)")
    esi_4 = BinaryTreeNode("Low Risk", recommendation="ESI-4: Standard Care (Priority 4)")
    esi_3 = BinaryTreeNode("Moderate Risk", recommendation="ESI-3: Moderate Care (Priority 3)")
    esi_5 = BinaryTreeNode("Minor Case", recommendation="ESI-5: Non-Urgent (Priority 5)")

    q_chest = BinaryTreeNode("Severe chest pain or breathing difficulty?", left=esi_2, right=esi_4)
    q_fever = BinaryTreeNode("High fever or moderate pain?", left=esi_3, right=esi_5)
    root_q = BinaryTreeNode("Is this an acute/sudden symptom?", left=q_chest, right=q_fever)
    return BinaryTree(root_q)


class MedTriageSystem:
    """Integrates GeneralTree, BinaryTree, PatientBST, LinkedStack, LinkedQueue, and PriorityQueue."""

    def __init__(self) -> None:
        self.hospital_tree = build_default_hospital_tree()
        self.triage_tree = build_default_triage_tree()
        self.patient_bst = PatientBST()
        self.triage_queue = PriorityQueue(aging_threshold=2)
        self.lab_queue = LinkedQueue()
        self.pharmacy_queue = LinkedQueue()
        self.undo_stack = LinkedStack()

    def screen_symptoms(self, answers: list[str]) -> tuple[str, int]:
        node = self.triage_tree.root
        for ans in answers:
            if node is None or self.triage_tree.is_recommendation(node):
                break
            node = self.triage_tree.step(node, ans)

        rec = self.triage_tree.get_recommendation(node) or "ESI-3: Moderate Care (Priority 3)"
        # Extract ESI priority digit if present (e.g., "ESI-2: ..." -> 2)
        priority = 3
        for part in rec.replace(":", " ").split():
            if part.startswith("ESI-") and part[4:].isdigit():
                priority = int(part[4:])
                break
        return rec, priority

    def register_patient(self, patient_id: int, name: str, age: int, answers: list[str]) -> Patient:
        rec, priority = self.screen_symptoms(answers)
        patient = Patient(
            patient_id=patient_id,
            name=name,
            age=age,
            symptoms=rec,
            esi_level=priority,
        )
        self.patient_bst.insert(patient)
        self.triage_queue.enqueue(patient, priority=priority)
        self.undo_stack.push(("register", patient_id))
        print(f"[Registered] {patient} -> Queued with ESI-{priority}")
        return patient

    def admit_next_patient(self) -> Patient | None:
        next_patient: Patient | None = self.triage_queue.dequeue()
        if next_patient is None:
            print("[Admit] No patients waiting in triage queue.")
            return None

        bed_name = self.hospital_tree.allocate_first_free_bed()
        if bed_name is None:
            print(f"[Admit] No free beds available for {next_patient.name}!")
            return None

        next_patient.assigned_bed = bed_name
        self.undo_stack.push(("admit", next_patient.patient_id, bed_name))
        print(
            f"[Admitted] {next_patient.name} (ID={next_patient.patient_id}) assigned to {bed_name} "
            f"| Occupancy: {self.hospital_tree.occupancy_percentage():.1f}%"
        )
        return next_patient

    def send_to_lab(self, patient_id: int, test_name: str) -> None:
        patient = self.patient_bst.search(patient_id)
        if patient is None:
            print(f"[Lab] Patient ID {patient_id} not found.")
            return
        entry = f"{patient.name} (ID={patient_id}): {test_name}"
        self.lab_queue.enqueue(entry)
        self.undo_stack.push(("lab", entry))
        print(f"[Lab Queued] {entry}")

    def send_to_pharmacy(self, patient_id: int, medication: str) -> None:
        patient = self.patient_bst.search(patient_id)
        if patient is None:
            print(f"[Pharmacy] Patient ID {patient_id} not found.")
            return
        entry = f"{patient.name} (ID={patient_id}): {medication}"
        self.pharmacy_queue.enqueue(entry)
        self.undo_stack.push(("pharmacy", entry))
        print(f"[Pharmacy Queued] {entry}")

    def discharge_patient(self, patient_id: int) -> None:
        patient = self.patient_bst.search(patient_id)
        if patient is None:
            print(f"[Discharge] Patient ID {patient_id} not found.")
            return

        if patient.assigned_bed:
            self.hospital_tree.release_bed(patient.assigned_bed)
        self.patient_bst.delete(patient_id)
        print(
            f"[Discharged] {patient.name} (ID={patient_id}) released {patient.assigned_bed} "
            f"| Remaining sorted IDs: {[p.patient_id for p in self.patient_bst.inorder_traversal()]}"
        )

    def undo_last_action(self) -> None:
        action = self.undo_stack.undo()
        if action is None:
            print("[Undo] Nothing to undo.")
            return

        kind = action[0]
        if kind == "admit":
            _, pid, bed_name = action
            self.hospital_tree.release_bed(bed_name)
            p = self.patient_bst.search(pid)
            if p:
                p.assigned_bed = None
                self.triage_queue.enqueue(p, priority=p.esi_level)
            print(f"[Undo Admit] Released {bed_name} and returned ID={pid} to queue.")
        elif kind == "lab":
            _, entry = action
            kept = [x for x in self.lab_queue.to_list() if x != entry]
            self.lab_queue = LinkedQueue()
            for item in kept:
                self.lab_queue.enqueue(item)
            print(f"[Undo Lab] Removed '{entry}' from lab queue.")
        elif kind == "pharmacy":
            _, entry = action
            kept = [x for x in self.pharmacy_queue.to_list() if x != entry]
            self.pharmacy_queue = LinkedQueue()
            for item in kept:
                self.pharmacy_queue.enqueue(item)
            print(f"[Undo Pharmacy] Removed '{entry}' from pharmacy queue.")
        elif kind == "register":
            _, pid = action
            self.patient_bst.delete(pid)
            print(f"[Undo Register] Removed patient ID={pid} from BST.")


def run_demo() -> None:
    print("=== MedTriage Full System Demo ===\n")
    sys = MedTriageSystem()

    sys.register_patient(105, "Noura", 28, ["no", "yes"])       # ESI-3
    sys.register_patient(101, "Salma", 45, ["yes", "yes"])      # ESI-2
    sys.register_patient(110, "Reem", 19, ["no", "no"])        # ESI-5

    print("\n--- Triage Queue Before Aging ---")
    print(sys.triage_queue.items_with_cycles())

    # Simulate waiting cycles to prevent starvation
    sys.triage_queue.tick_wait_cycles()
    sys.triage_queue.tick_wait_cycles()
    print("\n--- Triage Queue After 2 Wait Cycles ---")
    print(sys.triage_queue.items_with_cycles())

    print("\n--- Admission & Services ---")
    sys.admit_next_patient()
    sys.send_to_lab(101, "Troponin & CBC")
    sys.send_to_pharmacy(101, "Aspirin 100mg")

    print("\n--- Undo Last Pharmacy Action ---")
    sys.undo_last_action()
    print("Pharmacy queue:", sys.pharmacy_queue.to_list())
    print("Lab queue:", sys.lab_queue.to_list())

    print("\n--- Discharge & BST Check ---")
    sys.discharge_patient(101)
    print("Sorted patients in BST:", [p.patient_id for p in sys.patient_bst.inorder_traversal()])
    print(f"Free beds: {sys.hospital_tree.count_free_beds()} / {sys.hospital_tree.count_total_beds()}")


if __name__ == "__main__":
    run_demo()