import os

import cv2
import numpy as np
import fitz

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False,
)


# ============================================================
# KONSTANTA
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
PDF_EXTENSION = ".pdf"
PDF_DPI = 200


# ============================================================
# DETEKSI TIPE FILE
# ============================================================

def is_pdf(file_path: str) -> bool:
    return os.path.splitext(file_path)[1].lower() == PDF_EXTENSION


# ============================================================
# KONVERSI PDF → GAMBAR (numpy array)
# ============================================================

def pdf_to_images(file_path: str, dpi: int = PDF_DPI) -> list[np.ndarray]:
    doc = fitz.open(file_path)
    images = []

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    for page_num in range(len(doc)):
        page = doc[page_num]
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        img_array = np.frombuffer(pixmap.samples, dtype=np.uint8)
        img_array = img_array.reshape(pixmap.height, pixmap.width, pixmap.n)

        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        images.append(img_bgr)

    doc.close()
    return images


# ============================================================
# OCR CORE
# ============================================================

def extract_text(image_input) -> str:
    if isinstance(image_input, str):
        image = cv2.imread(image_input)
        if image is None:
            raise ValueError(f"Gagal membaca gambar: {image_input}")
    else:
        image = image_input

    result = ocr.ocr(image, cls=True)
    lines = []

    if result and result[0]:
        for line in result[0]:
            lines.append(line[1][0])

    return "\n".join(lines)


def extract_text_with_boxes(image_input) -> list[dict]:
    if isinstance(image_input, str):
        image = cv2.imread(image_input)
        if image is None:
            raise ValueError(f"Gagal membaca gambar: {image_input}")
    else:
        image = image_input

    result = ocr.ocr(image, cls=True)
    rows = []

    if result and result[0]:
        for line in result[0]:
            poly = line[0]
            text = line[1][0]
            try:
                confidence = float(line[1][1])
            except (IndexError, TypeError, ValueError):
                confidence = 0.0

            x = min(point[0] for point in poly)
            y = min(point[1] for point in poly)

            rows.append({
                "text": text,
                "x": x,
                "y": y,
                "confidence": confidence,
            })

    rows.sort(key=lambda d: (d["y"], d["x"]))
    return rows


# ============================================================
# ENTRY POINT TERPADU: FILE PATH (gambar atau PDF)
# ============================================================

def extract_boxes_from_file(
    file_path,
    page_mode: str = "first",
    y_offset_per_page: int = 2000,
) -> list[dict]:
    if isinstance(file_path, np.ndarray):
        return extract_text_with_boxes(file_path)

    if is_pdf(file_path):
        images = pdf_to_images(file_path)

        if not images:
            return []

        if page_mode == "first":
            return extract_text_with_boxes(images[0])

        all_boxes = []
        current_y_offset = 0

        for page_img in images:
            page_boxes = extract_text_with_boxes(page_img)
            for box in page_boxes:
                box = box.copy()
                box["y"] = box["y"] + current_y_offset
                all_boxes.append(box)
            current_y_offset += y_offset_per_page

        return all_boxes

    return extract_text_with_boxes(file_path)


def extract_text_from_image(image_input):
    return extract_text(image_input)