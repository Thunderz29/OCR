import re

from rapidfuzz import fuzz

from app.schemas.ktp_response import KtpResponse

from app.fuzzy.gender_matcher import (
    match_gender
)

from app.fuzzy.religion_matcher import (
    match_religion
)

from app.fuzzy.marital_status_matcher import (
    match_marital_status
)

from app.fuzzy.occupation_matcher import (
    match_occupation
)

from app.fuzzy.nationality_matcher import (
    match_nationality
)

from app.utils.text_utils import (
    normalize_text,
    clean_value
)

from app.utils.validator import (
    validate_nik
)

def find_value_by_label(
        boxes,
        labels,
        threshold=80,
        y_tolerance=35
):

    if isinstance(
            labels,
            str
    ):
        labels = [labels]

    label_box = None
    best_score = 0

    # mencari label terbaik
    for item in boxes:

        text = item["text"].upper()

        for label in labels:

            score = fuzz.partial_ratio(
                label.upper(),
                text
            )

            if score > best_score:

                best_score = score
                label_box = item

    if label_box is None:
        return None

    if best_score < threshold:
        return None

    candidates = []

    for item in boxes:

        # hanya yang di kanan label
        if item["x"] <= label_box["x"]:
            continue

        # satu baris yang sama
        if abs(
                item["y"] -
                label_box["y"]
        ) > y_tolerance:
            continue

        candidates.append(
            item
        )

    candidates.sort(
        key=lambda x: x["x"]
    )

    value = " ".join(
        item["text"]
        for item in candidates
    )

    return clean_value(
        normalize_text(
            value
        )
    )    


def parse_ktp(boxes):

    data = KtpResponse()

    # ==========================
    # NIK
    # ==========================

    for item in boxes:

        text = item["text"]

        nik_match = re.search(
            r"\d{16}",
            text
        )

        if nik_match:

            nik = validate_nik(
                nik_match.group()
            )

            if nik:

                data.nik = nik
                break

    # ==========================
    # NAMA
    # ==========================

    data.nama = find_value_by_label(
        boxes,
        ["NAMA"]
    )

    # ==========================
    # TEMPAT TANGGAL LAHIR
    # ==========================

    ttl = find_value_by_label(
        boxes,
        [
            "TEMPAT/TGL LAHIR",
            "TEMPAT LAHIR"
        ]
    )

    if ttl:

        tanggal_match = re.search(
            r"\d{2}[-/]\d{2}[-/]\d{4}",
            ttl
        )

        if tanggal_match:

            tanggal = tanggal_match.group()

            data.tanggal_lahir = tanggal

            tempat = ttl.replace(
                tanggal,
                ""
            )

            tempat = (
                tempat
                .replace(",", "")
                .strip()
            )

            data.tempat_lahir = tempat

    # ==========================
    # JENIS KELAMIN
    # ==========================

    jk = find_value_by_label(
        boxes,
        [
            "JENIS KELAMIN"
        ]
    )

    if jk:

        jk_match = re.search(
            r"LAKI[\s\-]?LAKI|PEREMPUAN",
            jk
        )

        if jk_match:

            data.jenis_kelamin = (
                match_gender(
                    jk_match.group()
                )
            )

    # ==========================
    # GOL DARAH
    # ==========================

    for item in boxes:

        text = normalize_text(
            item["text"]
        )

        if text is None:
            continue

        text = text.upper()

        if "GOL" in text and "DARAH" in text:

            gol_match = re.search(
                r"(AB|A|B|O)$",
                text
            )

            if gol_match:

                data.gol_darah = (
                    gol_match.group()
                )

    # ==========================
    # ALAMAT
    # ==========================

    data.alamat = find_value_by_label(
        boxes,
        ["ALAMAT"]
    )

    # ==========================
    # RT RW
    # ==========================

    rt_rw = find_value_by_label(
        boxes,
        ["RT/RW"]
    )

    if rt_rw:

        rt_match = re.search(
            r"\d{1,3}\s*/\s*\d{1,3}",
            rt_rw
        )

        if rt_match:

            data.rt_rw = (
                rt_match.group()
                .replace(
                    " ",
                    ""
                )
            )

    # ==========================
    # KELURAHAN
    # ==========================

    data.kelurahan = find_value_by_label(
        boxes,
        [
            "KEL/DESA",
            "KELURAHAN"
        ]
    )

    # ==========================
    # KECAMATAN
    # ==========================

    data.kecamatan = find_value_by_label(
        boxes,
        [
            "KECAMATAN"
        ]
    )

    # ==========================
    # AGAMA
    # ==========================

    agama = find_value_by_label(
        boxes,
        [
            "AGAMA"
        ]
    )

    if agama:

        data.agama = (
            match_religion(
                agama
            )
        )

    # ==========================
    # STATUS PERKAWINAN
    # ==========================

    for item in boxes:

        text = normalize_text(
            item["text"]
        )

        if text is None:
            continue

        text = text.upper()

        if (
                "STATUS" in text
                and
                "PERKAWINAN" in text
        ):

            status = re.sub(
                r".*PERKAWINAN",
                "",
                text
            )

            status = (
                status
                .replace(":", "")
                .strip()
            )

            data.status_perkawinan = (
                match_marital_status(
                    status
                )
            )

            break
    # ==========================
    # PEKERJAAN
    # ==========================

    pekerjaan = find_value_by_label(
        boxes,
        [
            "PEKERJAAN"
        ]
    )

    if pekerjaan:

        data.pekerjaan = (
            match_occupation(
                pekerjaan
            )
        )

    # ==========================
    # KEWARGANEGARAAN
    # ==========================

    for item in boxes:

        text = normalize_text(
            item["text"]
        )

        if text is None:
            continue

        text = text.upper()

        if "KEWARGANEGARAAN" in text:

            if "WNI" in text:

                data.kewarganegaraan = (
                    match_nationality(
                        "WNI"
                    )
                )

            elif "WNA" in text:

                data.kewarganegaraan = (
                    match_nationality(
                        "WNA"
                    )
                )

            break
        
    # ==========================
    # BERLAKU HINGGA
    # ==========================

    berlaku = find_value_by_label(
        boxes,
        [
            "BERLAKU HINGGA"
        ]
    )

    if berlaku:

        berlaku = berlaku.upper()

        if "SEUMUR HIDUP" in berlaku:

            data.berlaku_hingga = (
                "SEUMUR HIDUP"
            )

        else:

            tanggal_match = re.search(
                r"\d{2}[-/]\d{2}[-/]\d{4}",
                berlaku
            )

            if tanggal_match:

                data.berlaku_hingga = (
                    tanggal_match.group()
                )

    return data