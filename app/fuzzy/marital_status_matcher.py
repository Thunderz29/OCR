from rapidfuzz import process


STATUSES = [
    "BELUM KAWIN",
    "KAWIN",
    "CERAI HIDUP",
    "CERAI MATI"
]


def match_marital_status(value):

    if value is None:
        return None

    result = process.extractOne(
        value,
        STATUSES
    )

    if result:
        return result[0]

    return value