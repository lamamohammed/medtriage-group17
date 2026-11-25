from medtriage.models import Patient
from medtriage.node import BinaryTreeNode, GeneralTreeNode
from medtriage.tree import BinaryTree, GeneralTree
from medtriage.bst import PatientBST
from medtriage.stack import LinkedStack
from medtriage.queue import LinkedQueue, PriorityQueue


def build_default_hospital_tree() -> GeneralTree:
    """Build Hospital -> Wings -> Wards -> Beds hierarchy."""
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
    """Build Yes/No symptom decision tree mapping to ESI levels."""
    esi_2 = BinaryTreeNode("High Risk", recommendation="ESI-2: Urgent Care (Priority 2)")
    esi_4 = BinaryTreeNode("Low Risk", recommendation="ESI-4: Standard Care (Priority 4)")
    esi_3 = BinaryTreeNode("Moderate Risk", recommendation="ESI-3: Moderate Care (Priority 3)")
    esi_5 = BinaryTreeNode("Minor Case", recommendation="ESI-5: Non-Urgent (Priority 5)")

    q_chest = BinaryTreeNode("Severe chest pain or breathing difficulty?", left=esi_2, right=esi_4)
    q_fever = BinaryTreeNode("High fever or moderate pain?", left=esi_3, right=esi_5)
    root_q = BinaryTreeNode("Is this an acute/sudden symptom?", left=q_chest, right=q_fever)
    return BinaryTree(root_q)


def _extract_esi_priority(recommendation: str) -> int:
    for part in recommendation.replace(":", " ").split():
        if part.startswith("ESI-") and part[4:].isdigit():
            return int(part[4:])
    return 3


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

    def screen_symptoms_interactive(self) -> tuple[str, int]:
        """Interactive Yes/No symptom screening with LinkedStack backtracking support."""
        current = self.triage_tree.root
        history_stack = LinkedStack()

        while current is not None and not self.triage_tree.is_recommendation(current):
            print(f"\nQuestion: {current.text}")
            ans = input("Answer (yes/no or back to undo step): ").strip().lower()

            if ans in ("back", "undo", "b"):
                prev = history_stack.pop()
                if prev is not None:
                    current = prev
                    print("[Backtracked to previous question]")
                else:
                    print("[Already at the first question]")
                continue

            next_node = self.triage_tree.step(current, ans)
            if next_node is current:
                print("[Invalid input] Please enter 'yes', 'no', or 'back'.")
                continue

            history_stack.push(current)
            current = next_node

        rec = self.triage_tree.get_recommendation(current) or "ESI-3: Moderate Care (Priority 3)"
        priority = _extract_esi_priority(rec)
        print(f"Triage Result -> {rec}")
        return rec, priority

    def screen_symptoms(self, answers: list[str]) -> tuple[str, int]:
        node = self.triage_tree.root
        for ans in answers:
            if node is None or self.triage_tree.is_recommendation(node):
                break
            node = self.triage_tree.step(node, ans)

        rec = self.triage_tree.get_recommendation(node) or "ESI-3: Moderate Care (Priority 3)"
        return rec, _extract_esi_priority(rec)

    def register_patient(
        self,
        patient_id: int,
        name: str,
        age: int,
        answers: list[str] | None = None,
        interactive: bool = False,
    ) -> Patient:
        if interactive:
            rec, priority = self.screen_symptoms_interactive()
        else:
            rec, priority = self.screen_symptoms(answers or [])

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
            self.triage_queue.enqueue(next_patient, priority=next_patient.esi_level)
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

        released_bed = patient.assigned_bed
        if released_bed:
            self.hospital_tree.release_bed(released_bed)
        self.patient_bst.delete(patient_id)
        print(
            f"[Discharged] {patient.name} (ID={patient_id}) released {released_bed} "
            f"| Remaining sorted IDs: {[p.patient_id for p in self.patient_bst.inorder_traversal()]}"
        )

    def search_patient(self, patient_id: int) -> None:
        patient = self.patient_bst.search(patient_id)
        if patient is None:
            print(f"[Search] No patient found with ID {patient_id}.")
        else:
            print(f"[Found] {patient} | Symptoms/Triage: {patient.symptoms}")

    def show_ward_occupancy(self) -> None:
        total = self.hospital_tree.count_total_beds()
        free = self.hospital_tree.count_free_beds()
        occ = self.hospital_tree.occupancy_percentage()
        print("\n=== Ward & Bed Occupancy Summary ===")
        print(f"Total Beds    : {total}")
        print(f"Free Beds     : {free}")
        print(f"Occupied Beds : {total - free}")
        print(f"Occupancy %   : {occ:.1f}%")
        print(f"Active BST IDs: {[p.patient_id for p in self.patient_bst.inorder_traversal()]}")
        print(f"Triage Queue  : {self.triage_queue.items_with_cycles()}")
        print(f"Lab Queue     : {self.lab_queue.to_list()}")
        print(f"Pharmacy Queue: {self.pharmacy_queue.to_list()}")

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


def _prompt_int(prompt: str, min_val: int | None = None) -> int | None:
    raw = input(prompt).strip()
    if not raw.lstrip("-").isdigit():
        print("[Invalid input] Please enter a valid integer.")
        return None
    val = int(raw)
    if min_val is not None and val < min_val:
        print(f"[Invalid input] Value must be >= {min_val}.")
        return None
    return val


def run_demo() -> None:
    print("=== MedTriage Full System Demo ===\n")
    sys = MedTriageSystem()

    sys.register_patient(105, "Noura", 28, ["no", "yes"])       # ESI-3
    sys.register_patient(101, "Salma", 45, ["yes", "yes"])      # ESI-2
    sys.register_patient(110, "Reem", 19, ["no", "no"])        # ESI-5

    print("\n--- Triage Queue Before Aging ---")
    print(sys.triage_queue.items_with_cycles())

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


def run_cli() -> None:
    """Interactive menu-driven CLI for MedTriage."""
    sys = MedTriageSystem()
    while True:
        print("\n================ MedTriage Menu ================")
        print("1. Patient Intake & Symptom Triage")
        print("2. Admit Next Priority Patient & Allocate Bed")
        print("3. View Ward & Bed Occupancy / Queues")
        print("4. Search Patient by ID (BST)")
        print("5. Discharge Patient & Release Bed")
        print("6. Queue Lab / Pharmacy Order")
        print("7. Advance Triage Wait Cycles (+1)")
        print("8. Undo Last Action")
        print("9. Run Automated Demo Scenario")
        print("0. Exit")
        print("=================================================")

        choice = input("Select an option (0-9): ").strip()
        if choice == "1":
            pid = _prompt_int("Patient ID: ", min_val=1)
            if pid is None:
                continue
            name = input("Patient Name: ").strip()
            if not name:
                print("[Invalid input] Name cannot be empty.")
                continue
            age = _prompt_int("Patient Age: ", min_val=0)
            if age is None:
                continue
            sys.register_patient(pid, name, age, interactive=True)
        elif choice == "2":
            sys.admit_next_patient()
        elif choice == "3":
            sys.show_ward_occupancy()
        elif choice == "4":
            pid = _prompt_int("Enter Patient ID to search: ", min_val=1)
            if pid is not None:
                sys.search_patient(pid)
        elif choice == "5":
            pid = _prompt_int("Enter Patient ID to discharge: ", min_val=1)
            if pid is not None:
                sys.discharge_patient(pid)
        elif choice == "6":
            pid = _prompt_int("Patient ID: ", min_val=1)
            if pid is None:
                continue
            dept = input("Department (lab / pharmacy): ").strip().lower()
            order = input("Test or Medication name: ").strip()
            if not order:
                print("[Invalid input] Order description cannot be empty.")
                continue
            if dept == "lab":
                sys.send_to_lab(pid, order)
            elif dept == "pharmacy":
                sys.send_to_pharmacy(pid, order)
            else:
                print("[Invalid input] Choose 'lab' or 'pharmacy'.")
        elif choice == "7":
            sys.triage_queue.tick_wait_cycles()
            print("[Wait Cycles] Incremented wait_cycles for waiting patients.")
            print("Current Triage Queue:", sys.triage_queue.items_with_cycles())
        elif choice == "8":
            sys.undo_last_action()
        elif choice == "9":
            run_demo()
        elif choice == "0":
            print("Exiting MedTriage. Goodbye!")
            break
        else:
            print("[Invalid option] Please choose a number between 0 and 9.")


if __name__ == "__main__":
    run_cli()