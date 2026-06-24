from rapidfuzz import process


NATIONALITIES = [
    "WNI",
    "WNA"
]


def match_nationality(value):

    if value is None:
        return None

    result = process.extractOne(
        value,
        NATIONALITIES,
        score_cutoff=70
    )

    if result:
        return result[0]

    return value