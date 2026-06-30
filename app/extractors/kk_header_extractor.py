from app.extractors.kk_table_extractor import (
    group_rows,
    join_row_text
)

from app.utils.normalizer import (
    normalize_text
)

def clean_header_value(
        value
):

    if value is None:
        return None

    value = (
        value
        .replace(":", "")
        .strip()
    )

    if value in [
        "-",
        "-/",
        "/"
    ]:
        return None

    return value

def extract_header_data(boxes):

    result = {}

    rows = group_rows(
        boxes,
        tolerance=10
    )

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

        # ======================
        # NAMA KEPALA KELUARGA
        # ======================

        if "NAMA KEPALA KELUARGA" in upper:

            candidates = [

                box

                for box in row

                if box["x"] >= 500
                and "NAMA KEPALA KELUARGA" not in normalize_text(
                    box["text"]
                ).upper()

            ]

            if candidates:

                result[
                    "kepala_keluarga"
                ] = normalize_text(
                    min(
                        candidates,
                        key=lambda x: x["x"]
                    )["text"]
                )

        # ======================
        # ALAMAT
        # ======================

        elif "ALAMAT" in upper:

            candidates = [

                box

                for box in row

                if 500 <= box["x"] <= 1000

            ]

            if candidates:

                result[
                    "alamat"
                ] = clean_header_value(
                    normalize_text(
                        candidates[0]["text"]
                    )
                )

        # ======================
        # RT/RW
        # ======================

        elif "RT/RW" in upper:

            candidates = [

                box

                for box in row

                if 500 <= box["x"] <= 1000

            ]

            if candidates:

                value = normalize_text(
                    candidates[0]["text"]
                )

                result["rt_rw"] = value.replace(":", "").strip()

        # ======================
        # KODE POS
        # ======================

        elif "KODE POS" in upper:

            candidates = [

                box

                for box in row

                if 500 <= box["x"] <= 1000

            ]

            if candidates:

                result[
                    "kode_pos"
                ] = clean_header_value(
                    normalize_text(
                        candidates[0]["text"]
                    )
                )

        # ======================
        # DESA/KELURAHAN
        # ======================

        if "DESA/KELURAHAN" in upper:

            candidates = [

                box

                for box in row

                if box["x"] >= 1900

            ]

            if candidates:

                result[
                    "desa_kelurahan"
                ] = clean_header_value(
                    normalize_text(
                        candidates[0]["text"]
                    )
                )

        # ======================
        # KECAMATAN
        # ======================

        elif (
                "KECAMAIAN" in upper
                or
                "KECAMATAN" in upper
        ):

            candidates = [

                box

                for box in row

                if box["x"] >= 1900

            ]

            if candidates:

               result[
                "kecamatan"
            ] = clean_header_value(
                normalize_text(
                    candidates[0]["text"]
                )
            )

        # ======================
        # KABUPATEN/KOTA
        # ======================

        elif "KABUPATEN/KOTA" in upper:

            candidates = [

                box

                for box in row

                if box["x"] >= 1900

            ]

            if candidates:

                result[
                    "kabupaten_kota"
                ] = clean_header_value(
                    normalize_text(
                        candidates[0]["text"]
                    )
                )

        # ======================
        # PROVINSI
        # ======================

        elif "PROVINSI" in upper:

            candidates = [

                box

                for box in row

                if box["x"] >= 1900

            ]

            if candidates:

                result[
                    "provinsi"
                ] = clean_header_value(
                    normalize_text(
                        candidates[0]["text"]
                    )
                )

    return result