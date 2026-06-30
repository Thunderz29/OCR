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



BIRTH_MONTH_SECTION_KEYWORDS = [
    "NOVEMBER", "OKTOBER", "SEPTEMBER", "AGUSTUS",
    "JULI", "JUNI", "MEI", "APRIL",
    "MARET", "FEBRUARI", "JANUARI", "DESEMBER"
]


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
        "LAKI LAKI": "LAKI-LAKI",
        "KUTIPAN INI DIKELUARKAN": "KUTIPAN DIKELUARKAN",
        "KUTIPANINIDIKELUARKAN": "KUTIPAN DIKELUARKAN",
        "KUTIPAN INI": "KUTIPAN",
        "WESNBORN": "WES BORN",
        "THATIN": "THAT IN",
        "AHMADROZIKIN": "AHMAD ROZIKIN",
        "RIBUDUA": "RIBU DUA",
        "RIBU DUA PULUH": "RIBU DUA PULUH",
        "AY AH": "AYAH",
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
    nama_anak_from_lines = None

    for i, line in enumerate(lines):
        upper = line.upper()
        if upper.startswith("ANAK KE") or upper.startswith("CHILD NO"):
            if i > 0:
                prev = lines[i - 1]
                prev_upper = prev.upper()
                if prev_upper == prev and len(prev.split()) >= 1:
                    nama_anak_from_lines = prev_upper
            break

    if nama_anak_from_lines:
        data.nama_anak = nama_anak_from_lines.title()
    else:
        candidate_names = []

        blacklist = [
            "REPUBLIK", "INDONESIA", "PENCATATAN", "KELAHIRAN",
            "NOVEMBER", "OKTOBER", "SEPTEMBER", "AGUSTUS",
            "JULI", "JUNI", "MEI", "APRIL", "MARET", "FEBRUARI", "JANUARI", "DESEMBER",
            "TAHUN", "DINAS", "NIP", "WARGANEGARA", "REGISTRY", "OFFICE", "CERTIFICATE",
            "NATIONALITY", "EXCERPT", "KUTIPAN", "BERDASARKAN", "BAHWA", "PADA",
            "RIBU", "PULUH"
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
                    or "ANAK" in upper
                    or "-" in upper
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
    # AYAH & IBU
    #
    for line in lines:
        line_upper = line.upper()
        line_upper = line_upper.replace("AY AH", "AYAH")
        line_upper = line_upper.replace("AYAHAHMAD", "AYAH AHMAD")
        line_upper = line_upper.replace("IBURIKA", "IBU RIKA")
        line_upper = line_upper.replace("DANIBU", "DAN IBU")
        
        if "DAN IBU" in line_upper and ("AYAH" in line_upper or "DARI" in line_upper):
            ayah_match = re.search(r"AYAH\s+(.+?)\s+DAN\s+IBU", line_upper)
            if ayah_match:
                data.nama_ayah = ayah_match.group(1).strip().title()
            idx = line_upper.find("DAN IBU")
            if idx != -1:
                ibu_part = line_upper[idx + 7:].strip()
                ibu_part = re.sub(r"[^A-Z\s]", "", ibu_part).strip()
                if ibu_part:
                    data.nama_ibu = ibu_part.title()
            break

    if not data.nama_ayah:
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

    if not data.nama_ibu:
        ibu_match = re.search(
            r"DAN IBU\s+([A-Z]+(?:\s+[A-Z]+)*?)\s+(?:KUTIPAN|KUTPAN|DIBLITAR|THE EXCERPT|CHILD|ANAK KE|MOTHER)",
            text
        )
        if ibu_match:
            data.nama_ibu = (
                ibu_match.group(1)
                .strip()
                .title()
            )


    #
    # TANGGAL LAHIR
    #


    day = None

    lahir_section_match = re.search(
        r"BAHWA DI.+?PADA TANGGAL\s+([A-Z\s]+?)\s+(?:TELAH LAHIR|WES BORN|" +
        "|".join(BIRTH_MONTH_SECTION_KEYWORDS) + r")",
        text
    )

    if lahir_section_match:
        day_candidate = lahir_section_match.group(1).strip()
        for key in sorted(DAY_MAP.keys(), key=len, reverse=True):
            if day_candidate.startswith(key):
                day = DAY_MAP[key]
                break
        if not day:
            day = DAY_MAP.get(day_candidate)
    else:
        for key in sorted(DAY_MAP.keys(), key=len, reverse=True):
            pattern = rf"PADA TANGGAL {re.escape(key)}\s+(?:{chr(124).join(BIRTH_MONTH_SECTION_KEYWORDS)})"
            if re.search(pattern, text):
                day = DAY_MAP[key]
                break

    month = None

    birth_section_match = re.search(
        r"BAHWA DI.+?(?:ANAK KE|CHILD NO)",
        text
    )

    birth_section_text = (
        birth_section_match.group(0)
        if birth_section_match
        else text
    )

    for key, value in MONTH_MAP.items():
        if key in birth_section_text:
            month = value
            break

    year = None

    year_match = re.search(
        r"DUA RIBU DUA PULUH (SATU|DUA|TIGA|EMPAT|LIMA|ENAM)",
        birth_section_text
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