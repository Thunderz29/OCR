import re


def normalize_text(text: str):

    text = text.upper()

    replacements = {
        "JENISKELAMIN": "JENIS KELAMIN",
        "GOLDARAH": "GOL DARAH",
        "KELDESA": "KEL/DESA",
        "RTRW": "RT/RW",
        "RTIRW": "RT/RW",
        "TEMPATTGL": "TEMPAT/TGL",
        "LAKILAKI": "LAKI-LAKI",
        "KARYAWANSWASTA": "KARYAWAN SWASTA"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r'\s+', ' ', text)

    return text


def clean_value(value):

    if value is None:
        return None

    value = value.strip()

    value = value.lstrip(".:")
    value = value.rstrip(".:")

    value = re.sub(r'\s+', ' ', value)

    return value