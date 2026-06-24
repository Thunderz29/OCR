from rapidfuzz import process


OCCUPATIONS = [
    "KARYAWAN SWASTA",
    "PEGAWAI NEGERI",
    "WIRASWASTA",
    "PELAJAR",
    "MAHASISWA",
    "IBU RUMAH TANGGA",
    "MENGURUS RUMAH TANGGA",
    "PEGAWAI SWASTA"
]


def match_occupation(value):

    if value is None:
        return None

    result = process.extractOne(
        value,
        OCCUPATIONS
    )

    if result:
        return result[0]

    return value