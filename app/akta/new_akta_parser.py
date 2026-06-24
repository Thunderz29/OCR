import re

from app.schemas.akta_response import AktaResponse


MONTH_MAP = {
    "JANUARI": "01",
    "FEBRUARI": "02",
    "MARET": "03",
    "APRIL": "04",
    "MEI": "05",
    "JUNI": "06",
    "JULI": "07",
    "AGUSTUS": "08",
    "SEPTEMBER": "09",
    "OKTOBER": "10",
    "NOVEMBER": "11",
    "DESEMBER": "12"
}


DAY_MAP = {
    "SATU": "01",
    "DUA": "02",
    "TIGA": "03",
    "EMPAT": "04",
    "LIMA": "05",
    "ENAM": "06",
    "TUJUH": "07",
    "DELAPAN": "08",
    "SEMBILAN": "09",
    "SEPULUH": "10",
    "SEBELAS": "11",
    "DUA BELAS": "12",
    "TIGA BELAS": "13",
    "EMPAT BELAS": "14",
    "LIMA BELAS": "15",
    "ENAM BELAS": "16",
    "TUJUH BELAS": "17",
    "DELAPAN BELAS": "18",
    "SEMBILAN BELAS": "19",
    "DUA PULUH": "20",
    "DUA PULUH SATU": "21",
    "DUA PULUH DUA": "22",
    "DUA PULUH TIGA": "23",
    "DUA PULUH EMPAT": "24",
    "DUA PULUH LIMA": "25",
    "DUA PULUH ENAM": "26",
    "DUA PULUH TUJUH": "27",
    "DUA PULUH DELAPAN": "28",
    "DUA PULUH SEMBILAN": "29",
    "TIGA PULUH": "30",
    "TIGA PULUH SATU": "31"
}


YEAR_MAP = {
    "SATU": "2021",
    "DUA": "2022",
    "TIGA": "2023",
    "EMPAT": "2024",
    "LIMA": "2025",
    "ENAM": "2026"
}


def group_rows(raw_boxes, tolerance=20):

    boxes = sorted(
        raw_boxes,
        key=lambda x: x["y"]
    )

    rows = []

    for box in boxes:

        found = False

        for row in rows:

            if abs(row[0]["y"] - box["y"]) <= tolerance:
                row.append(box)
                found = True
                break

        if not found:
            rows.append(
                [box]
            )

    for row in rows:

        row.sort(
            key=lambda x: x["x"]
        )

    return rows


def join_rows(rows):

    result = []

    for row in rows:

        text = " ".join(
            item["text"]
            for item in row
        )

        result.append(
            text.strip()
        )

    return result


def normalize_text(text):

    text = text.upper()

    replacements = {
        "DANIBU": "DAN IBU",
        "AYAHAHMAD": "AYAH AHMAD",
        "IBURIKA": "IBU RIKA",
        "PADATANGGAL": "PADA TANGGAL",
        "SATU.LAKI-LAKI": "SATU LAKI-LAKI",
        "LAKI LAKI": "LAKI-LAKI"
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new
        )

    while "  " in text:
        text = text.replace(
            "  ",
            " "
        )

    return text


def parse_new_akta(raw_boxes):

    data = AktaResponse()

    rows = group_rows(raw_boxes)

    lines = join_rows(rows)

    text = " ".join(lines)

    text = normalize_text(text)

    #
    # NOMOR AKTA
    #
    nomor_match = re.search(
        r"\d{4}-LT-\d{8}-\d+",
        text
    )

    if nomor_match:
        data.nomor_akta = nomor_match.group()

    #
    # TEMPAT LAHIR
    #
    tempat_match = re.search(
        r"BAHWA DI (.+?) PADA",
        text
    )

    if tempat_match:

        data.tempat_lahir = (
            tempat_match.group(1)
            .strip()
            .title()
        )

    #
    # JENIS KELAMIN
    #
    if "LAKI-LAKI" in text:
        data.jenis_kelamin = "LAKI-LAKI"

    elif "PEREMPUAN" in text:
        data.jenis_kelamin = "PEREMPUAN"

    #
    # NAMA ANAK
    #
    candidate_names = []

    blacklist = [
        "REPUBLIK",
        "INDONESIA",
        "PENCATATAN",
        "KELAHIRAN",
        "NOVEMBER",
        "TAHUN",
        "DINAS",
        "NIP",
        "WARGANEGARA",
        "REGISTRY",
        "OFFICE",
        "CERTIFICATE"
    ]

    for line in lines:

        upper = line.upper()

        if len(line.split()) < 2:
            continue

        if upper != line:
            continue

        skip = False

        for word in blacklist:

            if word in upper:
                skip = True
                break

        if skip:
            continue

        if (
                "AYAH" in upper
                or "IBU" in upper
                or "DAN" in upper
        ):
            continue

        candidate_names.append(
            line
        )

    if candidate_names:

        data.nama_anak = (
            max(
                candidate_names,
                key=len
            )
            .title()
        )

    #
    # AYAH
    #
    ayah_match = re.search(
        r"AYAH\s+(.+?)\s+DAN\s+IBU",
        text
    )

    if ayah_match:

        data.nama_ayah = (
            ayah_match.group(1)
            .strip()
            .title()
        )

    #
    # IBU
    #
    ibu_match = re.search(
        r"IBU\s+(.+?)\s+(?:KUTIPAN|KUTPAN|DIBLITAR|THE EXCERPT)",
        text
    )

    if ibu_match:

        data.nama_ibu = (
            ibu_match.group(1)
            .strip()
            .title()
        )

    #
    # HARI
    #
    day = None

    for key, value in DAY_MAP.items():

        if f"PADA TANGGAL {key}" in text:

            day = value
            break

    #
    # BULAN
    #
    month = None

    for key, value in MONTH_MAP.items():

        if key in text:

            month = value
            break

    #
    # TAHUN
    #
    year = None

    year_match = re.search(
        r"DUA RIBU DUA PULUH (SATU|DUA|TIGA|EMPAT|LIMA|ENAM)",
        text
    )

    if year_match:

        year = YEAR_MAP.get(
            year_match.group(1)
        )

    if (
            day
            and month
            and year
    ):

        data.tanggal_lahir = (
            f"{day}-{month}-{year}"
        )

    return data