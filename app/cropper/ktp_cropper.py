import cv2


def crop_ktp_fields(image_path):

    image = cv2.imread(image_path)

    height, width = image.shape[:2]

    fields = {}

    # NIK
    fields["nik"] = image[
        int(height * 0.14):int(height * 0.24),
        int(width * 0.20):int(width * 0.80)
    ]

    # Nama
    fields["nama"] = image[
        int(height * 0.23):int(height * 0.32),
        int(width * 0.20):int(width * 0.80)
    ]

    # Tempat/Tanggal Lahir
    fields["ttl"] = image[
        int(height * 0.28):int(height * 0.38),
        int(width * 0.20):int(width * 0.85)
    ]

    # Alamat
    fields["alamat"] = image[
        int(height * 0.38):int(height * 0.52),
        int(width * 0.20):int(width * 0.90)
    ]

    return fields