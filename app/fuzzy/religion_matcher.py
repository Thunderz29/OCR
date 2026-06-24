from rapidfuzz import process


RELIGIONS = [
    "ISLAM",
    "KRISTEN",
    "KATOLIK",
    "HINDU",
    "BUDDHA",
    "KONGHUCU"
]


def match_religion(value):

    if value is None:
        return None

    result = process.extractOne(
        value,
        RELIGIONS
    )

    if result:
        return result[0]

    return value