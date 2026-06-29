import re

from app.schemas.kk_response import AnggotaKeluarga
from app.utils.normalizer import normalize_text

# Import Fuzzy Matchers Baru
from app.fuzzy.blood_type_matcher import match_blood_type
from app.fuzzy.education_matcher import match_education
from app.fuzzy.family_relation_matcher import match_family_relation
from app.fuzzy.gender_matcher import match_gender
from app.fuzzy.marital_status_matcher import match_marital_status
from app.fuzzy.nationality_matcher import match_nationality
from app.fuzzy.occupation_matcher import match_occupation
from app.fuzzy.religion_matcher import match_religion


def group_rows(boxes, tolerance=8):
    rows = []
    sorted_boxes = sorted(boxes, key=lambda box: (box["y"], box["x"]))

    for box in sorted_boxes:
        y = box["y"]
        found = False

        for row in rows:
            avg_y = sum(item["y"] for item in row) / len(row)
            if abs(avg_y - y) <= tolerance:
                row.append(box)
                found = True
                break

        if not found:
            rows.append([box])

    result = {}
    for row in rows:
        avg_y = int(sum(item["y"] for item in row) / len(row))
        result[avg_y] = sorted(row, key=lambda item: item["x"])

    return result


def join_row_text(row):
    if not row:
        return ""
    cols = sorted(row, key=lambda x: x["x"])
    return " ".join(item["text"].strip() if item.get("text") else "" for item in cols)


def find_row_by_keywords(rows, keywords):
    for y in sorted(rows):
        row_text = normalize_text(join_row_text(rows[y]).upper())
        if row_text is None:
            continue
        if all(keyword in row_text for keyword in keywords):
            return rows[y]
    return None


def row_has_content(text):
    return bool(text and text.strip() and text.strip() != "-" and text.strip() != ".")


def is_nomor_anggota(text):
    if text is None:
        return False
    return bool(re.match(r'^\d+\s*', text.strip()))


def extract_nomor(text):
    if text is None:
        return None
    match = re.match(r'^(\d+)', text.strip())
    return int(match.group(1)) if match else None


def extract_nik(text):
    if text is None:
        return None
    match = re.search(r'\d{16}', text)
    return match.group() if match else None


def extract_tanggal(text):
    if text is None:
        return None
    match = re.search(r'\d{2}-\d{2}-\d{4}', text)
    return match.group() if match else None


def extract_table1_blocks(boxes):
    rows = group_rows(boxes, tolerance=6)
    blocks = []
    current_block = []
    sudah_ada_nik = False
    mulai = False

    for y in sorted(rows):
        row_text = join_row_text(rows[y])
        upper = normalize_text(row_text.upper())
        if upper is None:
            continue

        if "NAMA LENGKAP" in upper and "NIK" in upper:
            mulai = True
            continue

        if not mulai:
            continue

        if "STATUS HUBUNGAN" in upper or "STATUS PERKAWINAN" in upper:
            break

        if re.fullmatch(r'[\d\-\.\(\)\s]+', upper):
            continue

        nik_match = re.search(r'\d{16}', upper)
        if nik_match:
            if sudah_ada_nik and current_block:
                blocks.append(current_block)
                current_block = []
            sudah_ada_nik = True

        current_block.append(row_text)

    if current_block:
        blocks.append(current_block)

    return blocks


def extract_table2_blocks(boxes):
    rows = group_rows(boxes, tolerance=15)
    blocks = []
    current_block = []
    mulai = False

    for y in sorted(rows):
        row_text = join_row_text(rows[y])
        upper = normalize_text(row_text.upper())
        if upper is None:
            continue

        # Menggunakan fuzzy match status perkawinan sebagai trigger pembacaan tabel bawah
        status_perkawinan = match_marital_status(upper)
        if status_perkawinan:
            mulai = True

        if not mulai:
            continue

        if "DIKELUARKAN TANGGAL" in upper or "KEPALA DINAS" in upper:
            break

        if re.fullmatch(r'[\d\-\.\(\)\s]+', upper):
            continue

        if status_perkawinan:
            if current_block:
                blocks.append(current_block)
                current_block = []

        current_block.append(row_text)

    if current_block:
        blocks.append(current_block)

    return blocks


def extract_table1_data(boxes):
    blocks = extract_table1_blocks(boxes)
    hasil = []
    nomor = 1

    for rows in blocks:
        anggota = AnggotaKeluarga()
        anggota.no = nomor

        text = normalize_text(" ".join(rows))
        if text is None:
            continue

        anggota.nik = extract_nik(text)
        
        # Menggunakan fuzzy matcher untuk Jenis Kelamin
        anggota.jenis_kelamin = match_gender(text)
        
        # ======================
        # TEMPAT LAHIR
        # ======================
        tempat_lahir = None
        if anggota.jenis_kelamin:
            match = re.search(
                rf'{anggota.jenis_kelamin}\s+([A-Z ]+?)\s+\d{2}-\d{2}-\d{4}',
                text
            )
            if match:
                tempat_lahir = normalize_text(match.group(1))

        anggota.tempat_lahir = tempat_lahir
        anggota.tanggal_lahir = extract_tanggal(text)

        # Menggunakan Fuzzy Matchers untuk data entitas
        anggota.agama = match_religion(text)
        anggota.pendidikan = match_education(text)
        anggota.jenis_pekerjaan = match_occupation(text)
        anggota.golongan_darah = match_blood_type(text)

        if anggota.nik:
            nama_match = re.search(rf'([A-Z\s\.]+?)\s*{anggota.nik}', text)
            if nama_match:
                anggota.nama_lengkap = normalize_text(nama_match.group(1))

        hasil.append(anggota)
        nomor += 1

    return hasil


def extract_table2_data(boxes):
    rows = group_rows(boxes, tolerance=15)
    hasil = []
    current_detail = None

    for y in sorted(rows):
        row = rows[y]
        row_text = join_row_text(row)
        upper = normalize_text(row_text.upper())

        if upper is None:
            continue

        if "DIKELUARKAN TANGGAL" in upper or "KEPALA DINAS" in upper:
            break

        # Menggunakan fuzzy match untuk mendeteksi anggota baru di tabel bawah
        status_perkawinan = match_marital_status(upper)
        if status_perkawinan:
            if current_detail:
                hasil.append(current_detail)

            current_detail = {
                "status_perkawinan": status_perkawinan,
                "hubungan_keluarga": None,
                "kewarganegaraan": None,
                "ayah": None,
                "ibu": None
            }

        if current_detail is None:
            continue

        # Hubungan Keluarga menggunakan Fuzzy Matcher
        hubungan = match_family_relation(upper)
        if hubungan:
            current_detail["hubungan_keluarga"] = hubungan

        # Kewarganegaraan menggunakan Fuzzy Matcher
        kewarganegaraan = match_nationality(upper)
        if kewarganegaraan:
            current_detail["kewarganegaraan"] = kewarganegaraan

        # ==================
        # AYAH (Berdasarkan Koordinat X)
        # ==================
        ayah_text = [box["text"] for box in row if 1450 <= box["x"] < 1900]
        if ayah_text:
            current_detail["ayah"] = normalize_text(" ".join(ayah_text))

        # ==================
        # IBU (Berdasarkan Koordinat X)
        # ==================
        ibu_text = [box["text"] for box in row if box["x"] >= 1900]
        if ibu_text:
            current_detail["ibu"] = normalize_text(" ".join(ibu_text))

    if current_detail:
        hasil.append(current_detail)

    return hasil


def merge_anggota_dan_detail(boxes):
    anggota_list = extract_table1_data(boxes)
    detail_list = extract_table2_data(boxes)

    for i, anggota in enumerate(anggota_list):
        if i >= len(detail_list):
            break

        detail = detail_list[i]
        anggota.status_perkawinan = detail.get("status_perkawinan")
        anggota.hubungan_keluarga = detail.get("hubungan_keluarga")
        anggota.kewarganegaraan = detail.get("kewarganegaraan")
        anggota.no_paspor = detail.get("no_paspor")
        anggota.no_kitap = detail.get("no_kitap")
        anggota.ayah = detail.get("ayah")
        anggota.ibu = detail.get("ibu")

    return anggota_list