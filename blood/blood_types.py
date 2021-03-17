from frozendict import frozendict

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

CAN_DONATE = frozendict({
    "O-": frozenset({"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}),
    "O+": frozenset({"A+", "B+", "AB+", "O+"}),
    "A-": frozenset({"A+", "A-", "AB+"}),
    "A+": frozenset({"A+", "AB+"}),
    "B-": frozenset({"B+", "B-", "AB+", "AB-"}),
    "B+": frozenset({"B+", "AB+"}),
    "AB-": frozenset({"AB+", "AB-"}),
    "AB+": frozenset({"AB+"})
})

MAX_BLOOD_AGE_DAYS = 30
HIGH_PRIORITY_DAYS = 20


def _can_receive():
    result = {}

    for donor_type, recipient_types in CAN_DONATE.items():
        for recipient_type in recipient_types:
            if recipient_type not in result:
                result[recipient_type] = set()

            result[recipient_type].add(donor_type)

    return frozendict(map(lambda pair: (pair[0], frozenset(pair[1])), result.items()))


CAN_RECEIVE = _can_receive()

POPULATION_BLOOD_TYPE_DISTRIBUTION = "pop"
