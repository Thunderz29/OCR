import re

from app.schemas.kp_response import KpResponse

from app.extractors.kk_table_extractor import (
    group_rows
)

from app.utils.text_utils import (
    normalize_text
)


def join_row_text(row):

    cols = sorted(
        row,
        key=lambda x: x["x"]
    )

    return " ".join(
        item["text"].strip()
        for item in cols
        if item.get("text")
    )


def parse_kp(boxes):

    data = KpResponse()

    rows = group_rows(
        boxes,
        tolerance=40
    )

    lines = []

    for y in sorted(rows):

        line = normalize_text(
            join_row_text(
                rows[y]
            )
        )

        if line:
            lines.append(
                line.upper().strip()
            )

    print("\n===== KP LINES =====")

    for line in lines:
        print(line)

    # =====================
    # EXTRACT PER LINE
    # =====================

    for line in lines:

        # -------------------
        # NAMA
        # -------------------
        match = re.search(
            r'^NAMA\s*[:]?\s+(.+)$',
            line
        )

        if match:

            data.nama = (
                match.group(1)
                .strip()
            )

        # -------------------
        # NISN
        # -------------------
        match = re.search(
            r'^NISN\s*[:]?\s*(\d{10})$',
            line
        )

        if match:

            data.nisn = (
                match.group(1)
            )

        # -------------------
        # NIS
        # -------------------
        match = re.search(
            r'^NIS\s*[:]?\s*(\d+)$',
            line
        )

        if match:

            data.nis = (
                match.group(1)
            )

        # -------------------
        # TTL
        # -------------------
        match = re.search(
            r'^TEMPAT.*?LAHIR\s*[:]?\s*(.+?)[,.]?\s*(\d{1,2}[\s\-/]+[A-Z0-9]+[\s\-/]+\d{4})$',
            line
        )

        if match:

            data.tempat_lahir = (
                match.group(1)
                .strip()
            )

            data.tanggal_lahir = (
                match.group(2)
                .strip()
            )

        # -------------------
        # ALAMAT
        # -------------------
        match = re.search(
            r'^ALAMAT\s*[:]?\s+(.+)$',
            line
        )

        if match:

            data.alamat = (
                match.group(1)
                .strip()
            )

        # -------------------
        # KELAS
        # -------------------
        match = re.search(
            r'^KELAS\s*[:]?\s+(.+)$',
            line
        )

        if match:

            data.kelas = (
                match.group(1)
                .strip()
            )

        # -------------------
        # TINGKAT
        # -------------------
        match = re.search(
            r'^TINGKAT\s*[:]?\s+(.+)$',
            line
        )

        if match:

            data.tingkat = (
                match.group(1)
                .strip()
            )

        # -------------------
        # JURUSAN
        # -------------------
        match = re.search(
            r'^JURUSAN\s*[:]?\s+(.+)$',
            line
        )

        if match:

            data.program_studi = (
                match.group(1)
                .strip()
            )

        # -------------------
        # TAHUN AJARAN
        # -------------------
        match = re.search(
            r'^TAHUN AJARAN\s*[:]?\s+(.+)$',
            line
        )

        if match:

            data.tahun_ajaran = (
                match.group(1)
                .strip()
            )

    # =====================
    # TANGGAL TERBIT
    # =====================

    for line in lines:

        if "KEPALA SEKOLAH" in line or "LAHIR" in line:
            continue

        match = re.search(
            r'(\d{1,2})\s*([A-Z]+)\s*(\d{4})',
            line
        )

        if match:

            data.tanggal_terbit = (
                f"{match.group(1)} "
                f"{match.group(2)} "
                f"{match.group(3)}"
            )

    # =====================
    # KEPALA SEKOLAH
    # =====================

    for i, line in enumerate(lines):

        if "KEPALA SEKOLAH" in line:

            for j in range(
                i + 1,
                min(
                    i + 6,
                    len(lines)
                )
            ):

                candidate = lines[j]

                if (
                    "NIP" in candidate
                    or len(candidate) < 5
                    or candidate == "SMKNS"
                    or candidate == "ML"
                ):
                    continue

                data.kepala_sekolah = candidate
                break

    return data