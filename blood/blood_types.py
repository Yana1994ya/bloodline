from typing import List

AVAILABLE_TYPES = (
    "A+",
    "O+",
    "B+",
    "AB+",
    "A-",
    "O-",
    "B-",
    "AB-"
)

AVAILABLE_TYPES_CHOICES = list(map(lambda x: (x, x), AVAILABLE_TYPES))

CAN_DONATE = [
    ("O-", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
    ("O+", ["A+", "B+", "AB+", "O+"]),
    ("A-", ["A+", "A-", "AB+"]),
    ("A+", ["A+", "AB+"]),
    ("B-", ["B+", "B-", "AB+", "AB-"]),
    ("B+", ["B+", "AB+"]),
    ("AB-", ["AB+", "AB-"]),
    ("AB+", ["AB+"])
]


def compatible_blood_types(blood_type: str) -> List[str]:
    if blood_type == "A+":
        return ["A+", "A-", "O+", "O-"]
    elif blood_type == "A-":
        return ["A-", "O-"]
    elif blood_type == "B+":
        return ["B+", "B-", "O+", "O-"]
    elif blood_type == "B-":
        return ["B-", "O-"]
    elif blood_type == "AB+":
        return list(AVAILABLE_TYPES)
    elif blood_type == "AB-":
        return ["AB-", "A-", "B-", "O-"]
    elif blood_type == "O+":
        return ["O+", "O-"]
    elif blood_type == "O-":
        return ["O-"]


POPULATION_BLOOD_TYPE_DISTRIBUTION = "pop"
