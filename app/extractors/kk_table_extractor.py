import re

from app.schemas.kk_response import (
    AnggotaKeluarga
)

from app.utils.kk_normalizer import (
    normalize_text
)

AGAMA_LIST = [

    "ISLAM",
    "KRISTEN",
    "KATOLIK",
    "HINDU",
    "BUDDHA",
    "KONGHUCU"

]


PENDIDIKAN_LIST = [

    "BELUM TAMAT SD/SEDERAJAT",
    "BELUM TAMAT SO/SEDEHAJAT",
    "SD/SEDERAJAT",
    "SD/SEDEHAJAT",
    "SLTP/SEDERAJAT",
    "SLTA/SEDERAJAT",
    "SLTAISEDERAJAT",
    "SLTA SEDERAJAT",
    "DIPLOMA III",
    "DIPLOMA IV/STRATA I",
    "DIPLOMA IVISTRATI",
    "DIPLOMA IVISTRATA",
    "DIPLOMA IVISTRATA I",
    "DIPLOMA IVISTRATAI",
    "STRATA I",
    "STRATA II",
    "STRATA III"

]


PEKERJAAN_LIST = [

    "PEGAWAI NEGERI SIPIL (PNS)",
    "PEGAWAI NEGERI SPIIL (PNS)",
    "PEGAWAI NEGERI SIPIL",
    "PELAJAR/MAHASISWA",
    "PELAJARIMAHASISWA",
    "KARYAWAN SWASTA",
    "WIRASWASTA",
    "PETANI",
    "NELAYAN",
    "MENGURUS RUMAH TANGGA",
    "SENIMAN",
    "PEDAGANG",
    "BURUH",
    "TUKANG",
    "POLISI",
    "TENTARA",
    "PENSIUN"

]


STATUS_PERKAWINAN_LIST = [

    "KAWIN BELUM TERCATAT",
    "BELUM KAWIN",
    "KAWIN"

]


HUBUNGAN_KELUARGA_LIST = [

    "KEPALA KELUARGA",
    "SUAMI",
    "ISTRI",
    "ANAK",
    "FAMILI LAIN",
    "FAMILILAIN"

]

def group_rows(
        boxes,
        tolerance=8
):

    rows = []

    sorted_boxes = sorted(
        boxes,
        key=lambda box: (
            box["y"],
            box["x"]
        )
    )

    for box in sorted_boxes:

        y = box["y"]

        found = False

        for row in rows:

            avg_y = sum(
                item["y"]
                for item in row
            ) / len(row)

            if abs(
                    avg_y - y
            ) <= tolerance:

                row.append(
                    box
                )

                found = True

                break

        if not found:

            rows.append(
                [box]
            )

    result = {}

    for row in rows:

        avg_y = int(
            sum(
                item["y"]
                for item in row
            ) / len(row)
        )

        result[avg_y] = sorted(
            row,
            key=lambda item: item["x"]
        )

    return result

def join_row_text(
        row
):
    
    if not row:
        return ""

    cols = sorted(
        row,
        key=lambda x: x["x"]
    )

    return " ".join(

        item["text"].strip() if item.get("text") else ""

        for item in cols

    )


def find_row_by_keywords(
        rows,
        keywords
):
    for y in sorted(rows):
        row_text = normalize_text(join_row_text(rows[y]).upper())
        if row_text is None:
            continue
        if all(keyword in row_text for keyword in keywords):
            return rows[y]
    return None

def row_has_content(
        text
):
    return bool(text and text.strip() and text.strip() != "-" and text.strip() != ".")


def is_nomor_anggota(
        text
):
    
    if text is None:
        return False

    return bool(

        re.match(

            r'^\d+\s*',

            text.strip()

        )

    )

def extract_nomor(
        text
):
    
    if text is None:
        return None

    match = re.match(

        r'^(\d+)',

        text.strip()

    )

    if match:

        return int(
            match.group(1)
        )

    return None

def extract_nik(
        text
):
    
    if text is None:
        return None

    match = re.search(
        r'\d{16}',
        text
    )

    if match:

        return match.group()

    return None

def extract_tanggal(
        text
):
    
    if text is None:
        return None

    match = re.search(

        r'\d{2}-\d{2}-\d{4}',

        text

    )

    if match:

        return match.group()

    return None

def extract_gender(
        text
):
    
    if text is None:
        return None

    upper = text.upper()

    if "PEREMPUAN" in upper:

        return "PEREMPUAN"

    if "LAKI-LAKI" in upper:

        return "LAKI-LAKI"

    if "LAK-LAKI" in upper:

        return "LAKI-LAKI"

    return None

def extract_agama(
        text
):
    
    if text is None:
        return None

    upper = text.upper()

    for agama in AGAMA_LIST:

        if agama in upper:

            return agama

    return None

def extract_golongan_darah(
        text
):
    
    if text is None:
        return None

    upper = text.upper()

    if "TIDAK TAHU" in upper:

        return "TIDAK TAHU"

    if "AB" in upper:

        return "AB"

    if upper.strip() == "A":

        return "A"

    if upper.strip() == "B":

        return "B"

    if upper.strip() in [
        "O",
        "0"
    ]:

        return "O"

    return None

def find_keyword(
        text,
        candidates
):

    if text is None:
        return None

    upper = normalize_text(
        text.upper()
    )

    if upper is None:
        return None

    for item in candidates:

        if item in upper:

            return normalize_text(
                item
            )

    return None

def extract_table1_blocks(
        boxes
):

    rows = group_rows(
        boxes,
        tolerance=6
    )

    blocks = []

    current_block = []

    sudah_ada_nik = False

    mulai = False

    for y in sorted(rows):

        row_text = join_row_text(
            rows[y]
        )

        upper = normalize_text(
            row_text.upper()
        )

        if upper is None:
            continue

        # mulai tabel atas
        if (
                "NAMA LENGKAP" in upper
                and
                "NIK" in upper
        ):
            mulai = True
            continue

        if not mulai:
            continue

        # berhenti sebelum tabel bawah
        if (
                "STATUS HUBUNGAN" in upper
                or
                "STATUS PERKAWINAN" in upper
        ):
            break

        if re.fullmatch(
                r'[\d\-\.\(\)\s]+',
                upper
        ):
            continue

        nik_match = re.search(
            r'\d{16}',
            upper
        )

        if nik_match:

            if sudah_ada_nik and current_block:

                blocks.append(
                    current_block
                )

                current_block = []

            sudah_ada_nik = True

        current_block.append(
            row_text
        )

    if current_block:

        blocks.append(
            current_block
        )

    return blocks

def extract_table2_blocks(
        boxes
):

    rows = group_rows(
        boxes,
        tolerance=15
    )

    blocks = []

    current_block = []

    mulai = False

    for y in sorted(rows):

        row_text = join_row_text(
            rows[y]
        )

        upper = normalize_text(
            row_text.upper()
        )

        if upper is None:
            continue

        # mulai membaca tabel bawah ketika menemukan status pertama
        if (
                "KAWIN BELUM TERCATAT" in upper
                or
                "BELUM KAWIN" in upper
        ):
            mulai = True

        if not mulai:
            continue

        # footer
        if (
                "DIKELUARKAN TANGGAL" in upper
                or
                "KEPALA DINAS" in upper
        ):
            break

        # noise
        if re.fullmatch(
                r'[\d\-\.\(\)\s]+',
                upper
        ):
            continue

        # anggota baru
        if (
                "KAWIN BELUM TERCATAT" in upper
                or
                "BELUM KAWIN" in upper
        ):

            if current_block:

                blocks.append(
                    current_block
                )

                current_block = []

        current_block.append(
            row_text
        )

    if current_block:

        blocks.append(
            current_block
        )

    return blocks

def extract_table1_data(
        boxes
):

    blocks = extract_table1_blocks(
        boxes
    )

    hasil = []

    nomor = 1

    for rows in blocks:

        anggota = AnggotaKeluarga()

        anggota.no = nomor

        text = normalize_text(
            " ".join(
                rows
            )
        )

        if text is None:
            continue

        anggota.nik = extract_nik(
            text
        )

        anggota.jenis_kelamin = (
            extract_gender(
                text
            )
        )
        
        # ======================
        # TEMPAT LAHIR
        # ======================

        tempat_lahir = None

        if anggota.jenis_kelamin:

            if anggota.jenis_kelamin == "LAKI-LAKI":

                match = re.search(
                    r'LAKI-LAKI\s+([A-Z ]+?)\s+\d{2}-\d{2}-\d{4}',
                    text
                )

                if match:

                    tempat_lahir = normalize_text(
                        match.group(1)
                    )

            elif anggota.jenis_kelamin == "PEREMPUAN":

                match = re.search(
                    r'PEREMPUAN\s+([A-Z ]+?)\s+\d{2}-\d{2}-\d{4}',
                    text
                )

                if match:

                    tempat_lahir = normalize_text(
                        match.group(1)
                    )

        anggota.tempat_lahir = (
            tempat_lahir
        )

        anggota.tanggal_lahir = (
            extract_tanggal(
                text
            )
        )

        anggota.agama = (
            extract_agama(
                text
            )
        )

        anggota.pendidikan = (
            find_keyword(
                text,
                PENDIDIKAN_LIST
            )
        )

        anggota.jenis_pekerjaan = (
            find_keyword(
                text,
                PEKERJAAN_LIST
            )
        )

        anggota.golongan_darah = (
            extract_golongan_darah(
                text
            )
        )

        if anggota.nik:

            nama_match = re.search(
                rf'([A-Z\s\.]+?)\s*{anggota.nik}',
                text
            )

            if nama_match:

                anggota.nama_lengkap = (
                    normalize_text(
                        nama_match.group(1)
                    )
                )

        hasil.append(
            anggota
        )

        nomor += 1

    return hasil

def extract_table2_data(
        boxes
):

    rows = group_rows(
        boxes,
        tolerance=15
    )

    hasil = []

    current_detail = None

    for y in sorted(rows):

        row = rows[y]

        row_text = join_row_text(
            row
        )

        upper = normalize_text(
            row_text.upper()
        )

        if upper is None:
            continue

        # footer
        if (
                "DIKELUARKAN TANGGAL" in upper
                or
                "KEPALA DINAS" in upper
        ):
            break

        # anggota baru
        if (
                "KAWIN BELUM TERCATAT" in upper
                or
                "BELUM KAWIN" in upper
        ):

            if current_detail:

                hasil.append(
                    current_detail
                )

            current_detail = {

                "status_perkawinan": find_keyword(
                    upper,
                    STATUS_PERKAWINAN_LIST
                ),

                "hubungan_keluarga": None,

                "kewarganegaraan": None,

                "ayah": None,

                "ibu": None

            }

        if current_detail is None:
            continue

        # hubungan keluarga
        if "KEPALA KELUARGA" in upper:

            current_detail[
                "hubungan_keluarga"
            ] = "KEPALA KELUARGA"

        elif (
                "FAMILILAIN" in upper
                or
                "FAMILI LAIN" in upper
        ):

            current_detail[
                "hubungan_keluarga"
            ] = "FAMILI LAIN"

        # kewarganegaraan
        if "WNI" in upper:

            current_detail[
                "kewarganegaraan"
            ] = "WNI"

        elif "WNA" in upper:

            current_detail[
                "kewarganegaraan"
            ] = "WNA"

        # ==================
        # AYAH
        # ==================

        ayah_text = []

        for box in row:

            if (
                    1450 <= box["x"] < 1900
            ):

                ayah_text.append(
                    box["text"]
                )

        if ayah_text:

            current_detail[
                "ayah"
            ] = normalize_text(
                " ".join(
                    ayah_text
                )
            )

        # ==================
        # IBU
        # ==================

        ibu_text = []

        for box in row:

            if (
                    box["x"] >= 1900
            ):

                ibu_text.append(
                    box["text"]
                )

        if ibu_text:

            current_detail[
                "ibu"
            ] = normalize_text(
                " ".join(
                    ibu_text
                )
            )

    if current_detail:

        hasil.append(
            current_detail
        )

    return hasil

def merge_anggota_dan_detail(
        boxes
):

    anggota_list = extract_table1_data(
        boxes
    )

    detail_list = extract_table2_data(
        boxes
    )

    for i, anggota in enumerate(
            anggota_list
    ):

        if i >= len(
                detail_list
        ):
            break

        detail = detail_list[i]

        anggota.status_perkawinan = (
            detail.get(
                "status_perkawinan"
            )
        )

        anggota.hubungan_keluarga = (
            detail.get(
                "hubungan_keluarga"
            )
        )

        anggota.kewarganegaraan = (
            detail.get(
                "kewarganegaraan"
            )
        )

        anggota.no_paspor = (
            detail.get(
                "no_paspor"
            )
        )

        anggota.no_kitap = (
            detail.get(
                "no_kitap"
            )
        )

        anggota.ayah = (
            detail.get(
                "ayah"
            )
        )

        anggota.ibu = (
            detail.get(
                "ibu"
            )
        )

    return anggota_list