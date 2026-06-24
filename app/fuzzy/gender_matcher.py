from rapidfuzz import process


GENDERS = [
    "LAKI-LAKI",
    "PEREMPUAN"
]


def match_gender(value):

    if value is None:
        return None

    result = process.extractOne(
        value,
        GENDERS
    )

    if result:
        return result[0]

    return value