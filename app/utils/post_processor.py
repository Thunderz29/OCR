import re


def clean_status_perkawinan(status):

    if status is None:
        return None

    status = status.upper()

    if "KAWIN" in status:
        return "KAWIN"

    if "BELUM" in status:
        return "BELUM KAWIN"

    if "CERAI HIDUP" in status:
        return "CERAI HIDUP"

    if "CERAI MATI" in status:
        return "CERAI MATI"

    return status


def clean_pekerjaan(pekerjaan):

    if pekerjaan is None:
        return None

    pekerjaan = pekerjaan.upper()

    pekerjaan = re.sub(r'\d+', '', pekerjaan)

    if "KARYAWAN" in pekerjaan and "SWASTA" in pekerjaan:
        return "KARYAWAN SWASTA"

    return pekerjaan.strip()


def clean_kecamatan(kecamatan):

    if kecamatan is None:
        return None

    return kecamatan.replace(".", "").replace("_", "").strip()