def normalize_text(text):

    if text is None:
        return None

    text = text.strip()

    mapping = {

        # ======================
        # Pendidikan
        # ======================

        "SO/SEDEHAJAT": "SD/SEDERAJAT",
        "SD/SEDEHAJAT": "SD/SEDERAJAT",

        "BELUM TAMAT SO/SEDEHAJAT":
            "BELUM TAMAT SD/SEDERAJAT",

        "BELUM TAMAT SD/SEDEHAJAT":
            "BELUM TAMAT SD/SEDERAJAT",

        "SLTAISEDERAJAT":
            "SLTA/SEDERAJAT",

        "SLTAISEDERAJAT ":
            "SLTA/SEDERAJAT",

        "SLTA/SEDEHAJAT":
            "SLTA/SEDERAJAT",

        "DIPLOMA IVISTRATA1":
            "DIPLOMA IV/STRATA I",

        "DIPLOMA IVISTRATA I":
            "DIPLOMA IV/STRATA I",

        "DIPLOMA IVISTRATAI":
            "DIPLOMA IV/STRATA I",

        # ======================
        # Pekerjaan
        # ======================

        "PEGAWAI NEGERI SPIIL (PNS)":
            "PEGAWAI NEGERI SIPIL (PNS)",

        "PEGAWAI NEGERI SPIIL":
            "PEGAWAI NEGERI SIPIL",

        "PELAJARIMAHASISWA":
            "PELAJAR/MAHASISWA",

        "PELAJARI MAHASISWA":
            "PELAJAR/MAHASISWA",

        # ======================
        # Hubungan keluarga
        # ======================

        "FAMILILAIN":
            "FAMILI LAIN",

        # ======================
        # Golongan darah
        # ======================

        "0":
            "O",

        # ======================
        # Unknown
        # ======================

        "TIDAKTAHU":
            "TIDAK TAHU"

    }

    return mapping.get(
        text.upper(),
        text
    )