class Patient:
    """Represents a patient record in the MedTriage system."""

    def __init__(
        self,
        patient_id: int,
        name: str,
        age: int,
        symptoms: str = "",
        esi_level: int = 5,
        assigned_bed: str | None = None,
    ):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.symptoms = symptoms
        self.esi_level = esi_level
        self.assigned_bed = assigned_bed

    def __repr__(self) -> str:
        return (
            f"Patient(id={self.patient_id}, name={self.name!r}, "
            f"age={self.age}, esi={self.esi_level}, bed={self.assigned_bed!r})"
        )


class BSTNode:
    """Binary Search Tree node storing a Patient keyed by patient_id."""

    def __init__(self, patient: Patient):
        self.patient = patient
        self.left: BSTNode | None = None
        self.right: BSTNode | None = None