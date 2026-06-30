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


def partition_table_boxes(boxes):
    """Pisahkan boxes secara spasial menjadi Tabel 1 dan Tabel 2
    berdasarkan koordinat Y yang dideteksi secara dinamis dari konten dokumen.
    Ini memastikan data antar-tabel tidak saling mencemari satu sama lain."""
    y_divider = None
    y_header2 = None
    y_footer = None

    for box in boxes:
        text = normalize_text(box.get("text", ""))
        if not text:
            continue
        t = text.upper()

        # Batas atas Tabel 2: baris header status/hubungan/nama orang tua
        if ("STATUS PERKAWINAN" in t or "STATUS HUBUNGAN" in t
                or "NAMA ORANG TUA" in t or "DOKUMEN IMGRASI" in t
                or "DOKUMEN IMIGRASI" in t):
            y = box["y"]
            if y_divider is None or y < y_divider:
                y_divider = y

        # Batas bawah header Tabel 2: baris nomor kolom (10), (11), ..., (17)
        if re.search(r'\(\d+\)', t) or t in ["14)", "15)", "16)", "17)"]:
            y = box["y"]
            if (y_divider is not None and y > y_divider
                    and y < y_divider + 100
                    and (y_header2 is None or y > y_header2)):
                y_header2 = y

        # Batas footer: baris tanda tangan / tanggal dikeluarkan
        if ("DIKELUARKAN TANGGAL" in t or "KEPALA DINAS" in t
                or "LEMBAR" in t or "PENCATATAN SIPIL" in t):
            y = box["y"]
            if y_footer is None or y < y_footer:
                y_footer = y

    # Fallback jika marker tidak ditemukan
    if y_divider is None:
        y_divider = 800
    if y_header2 is None:
        y_header2 = y_divider + 80
    if y_footer is None:
        y_footer = 1300

    # Tabel 1: semua box DI ATAS baris header Tabel 2
    table1_boxes = [box for box in boxes if box["y"] < y_divider]
    # Tabel 2: box ANTARA baris nomor kolom dan footer
    table2_boxes = [box for box in boxes if y_header2 < box["y"] < y_footer]

    return table1_boxes, table2_boxes


def extract_table1_data(boxes):
    table1_boxes, _ = partition_table_boxes(boxes)
    blocks = extract_table1_blocks(table1_boxes)
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
        # TEMPAT LAHIR & TANGGAL LAHIR
        # ======================
        anggota.tanggal_lahir = extract_tanggal(text)
        tempat_lahir = None

        if anggota.jenis_kelamin and anggota.tanggal_lahir:
            jk_pos = text.find(anggota.jenis_kelamin)
            tl_pos = text.find(anggota.tanggal_lahir)
            if jk_pos != -1 and tl_pos != -1 and jk_pos < tl_pos:
                middle_text = text[jk_pos + len(anggota.jenis_kelamin) : tl_pos].strip()
                middle_text = re.sub(r'^[\d\s\W]+', '', middle_text)
                if middle_text:
                    tempat_lahir = normalize_text(middle_text)

        anggota.tempat_lahir = tempat_lahir

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
    """Ekstrak data Tabel 2 (status perkawinan, hubungan keluarga, nama orang tua)
    menggunakan partisi Y dinamis untuk menghindari kontaminasi dari Tabel 1 dan footer,
    serta pemetaan kolom berdasarkan koordinat X relatif per baris."""
    _, table2_boxes = partition_table_boxes(boxes)
    rows = group_rows(table2_boxes, tolerance=15)
    hasil = []

    for y in sorted(rows):
        row = rows[y]
        row_text = join_row_text(row)
        upper = normalize_text(row_text.upper())
        if not upper:
            continue

        # ==================
        # STATUS PERKAWINAN (kolom kiri, x < 350)
        # Harus ada untuk dianggap baris data yang valid
        # ==================
        status_boxes = [b for b in row if b["x"] < 350]
        status_text = join_row_text(status_boxes)
        status_perkawinan = match_marital_status(status_text)
        if not status_perkawinan:
            continue  # baris kosong / header / footer — lewati

        # ==================
        # STATUS HUBUNGAN KELUARGA (kolom tengah-kiri, 550 <= x < 800)
        # ==================
        hubungan_boxes = [b for b in row if 550 <= b["x"] < 800]
        hubungan_text = join_row_text(hubungan_boxes)
        hubungan_keluarga = match_family_relation(hubungan_text)

        # ==================
        # KEWARGANEGARAAN (kolom tengah, 800 <= x < 1000)
        # ==================
        kwn_boxes = [b for b in row if 800 <= b["x"] < 1000]
        kewarganegaraan = match_nationality(join_row_text(kwn_boxes))

        # ==================
        # NO. PASPOR (1000 <= x < 1220)
        # ==================
        paspor = normalize_text(join_row_text([b for b in row if 1000 <= b["x"] < 1220]))
        if paspor in ["-", ""]:
            paspor = None

        # ==================
        # NO. KITAP (1220 <= x < 1450)
        # ==================
        kitap = normalize_text(join_row_text([b for b in row if 1220 <= b["x"] < 1450]))
        if kitap in ["-", ""]:
            kitap = None

        # ==================
        # NAMA AYAH (1450 <= x < 1900)
        # ==================
        ayah = normalize_text(join_row_text([b for b in row if 1450 <= b["x"] < 1900]))
        if ayah in ["-", ""]:
            ayah = None

        # ==================
        # NAMA IBU (x >= 1900)
        # ==================
        ibu = normalize_text(join_row_text([b for b in row if b["x"] >= 1900]))
        if ibu in ["-", ""]:
            ibu = None

        hasil.append({
            "status_perkawinan": status_perkawinan,
            "hubungan_keluarga": hubungan_keluarga,
            "kewarganegaraan": kewarganegaraan,
            "no_paspor": paspor,
            "no_kitap": kitap,
            "ayah": ayah,
            "ibu": ibu,
        })

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