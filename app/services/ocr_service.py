import cv2
import numpy as np

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False
)


def preprocess_image(image_input):

    if isinstance(image_input, str):

        image = cv2.imread(
            image_input
        )

        if image is None:

            raise ValueError(
                f"Gagal membaca gambar: {image_input}"
            )

    else:

        image = image_input.copy()

    image = cv2.resize(
        image,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    return image


def extract_text(
        image_input
):

    image = preprocess_image(
        image_input
    )

    result = ocr.ocr(
        image,
        cls=True
    )

    lines = []

    if result and result[0]:

        for line in result[0]:

            text = line[1][0]

            lines.append(
                text
            )

    return "\n".join(
        lines
    )


def extract_text_with_boxes(
        image_input
):

    image = preprocess_image(
        image_input
    )

    result = ocr.ocr(
        image,
        cls=True
    )

    rows = []

    if result and result[0]:

        for line in result[0]:

            poly = line[0]

            text = line[1][0]
            try:
                confidence = float(line[1][1])
            except (IndexError, TypeError, ValueError):
                confidence = 0.0

            x = min(
                point[0]
                for point in poly
            )

            y = min(
                point[1]
                for point in poly
            )

            rows.append(
                {
                    "text": text,
                    "x": x,
                    "y": y,
                    "confidence": confidence
                }
            )

    rows = sorted(
        rows,
        key=lambda d: (
            d["y"],
            d["x"]
        )
    )

    return rows


def extract_text_from_image(
        image_input
):

    return extract_text(
        image_input
    )