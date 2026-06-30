import cv2
import numpy as np
import fitz  # PyMuPDF

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_angle_cls=True,
    lang="en",
    show_log=False
)

# ============================================================
# KONSTANTA
# ============================================================

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
PDF_EXTENSION = ".pdf"
PDF_DPI = 200  # DPI untuk konversi PDF → gambar (200 = kualitas baik, tidak terlalu berat)


# ============================================================
# DETEKSI TIPE FILE
# ============================================================

def is_pdf(file_path: str) -> bool:
    """Cek apakah file adalah PDF berdasarkan ekstensi."""
    import os
    ext = os.path.splitext(file_path)[1].lower()
    return ext == PDF_EXTENSION


# ============================================================
# KONVERSI PDF → GAMBAR (numpy array)
# ============================================================

def pdf_to_images(file_path: str, dpi: int = PDF_DPI) -> list[np.ndarray]:
    """
    Konversi setiap halaman PDF menjadi list numpy array (BGR, siap untuk OpenCV/OCR).
    
    Args:
        file_path: Path ke file PDF
        dpi: Resolusi rendering (default 200 DPI — keseimbangan kualitas vs kecepatan)
    
    Returns:
        List of numpy arrays, satu per halaman PDF
    """
    doc = fitz.open(file_path)
    images = []
    
    # Hitung matrix zoom dari DPI (72 DPI adalah DPI standar PDF)
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Render halaman ke pixmap (RGBA)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        
        # Konversi pixmap → numpy array (RGB)
        img_array = np.frombuffer(pixmap.samples, dtype=np.uint8)
        img_array = img_array.reshape(pixmap.height, pixmap.width, pixmap.n)
        
        # Konversi RGB → BGR untuk OpenCV
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        images.append(img_bgr)
    
    doc.close()
    return images


# ============================================================
# PREPROCESS GAMBAR
# ============================================================

def preprocess_image(image_input):
    """
    Preprocess gambar: resize 2x untuk meningkatkan akurasi OCR.
    Menerima path string atau numpy array.
    """
    if isinstance(image_input, str):
        image = cv2.imread(image_input)
        if image is None:
            raise ValueError(f"Gagal membaca gambar: {image_input}")
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


# ============================================================
# OCR CORE
# ============================================================

def extract_text(image_input) -> str:
    """Ekstrak text plain dari gambar (path atau numpy array)."""
    image = preprocess_image(image_input)

    result = ocr.ocr(image, cls=True)
    lines = []

    if result and result[0]:
        for line in result[0]:
            lines.append(line[1][0])

    return "\n".join(lines)


def extract_text_with_boxes(image_input) -> list[dict]:
    """
    Ekstrak text beserta koordinat bounding box dari gambar (path atau numpy array).
    
    Returns:
        List of dict: {text, x, y, confidence}
    """
    image = preprocess_image(image_input)

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
                "confidence": confidence
            })

    rows = sorted(rows, key=lambda d: (d["y"], d["x"]))
    return rows


# ============================================================
# ENTRY POINT TERPADU: FILE PATH (gambar atau PDF)
# ============================================================

def extract_boxes_from_file(
    file_path: str,
    page_mode: str = "first",
    y_offset_per_page: int = 2000
) -> list[dict]:
    """
    Ekstrak bounding boxes dari file gambar atau PDF secara otomatis.
    
    Args:
        file_path   : Path ke file (gambar atau PDF)
        page_mode   : "first"  → hanya halaman pertama (untuk KTP, KP, Akte)
                      "all"    → semua halaman, Y-offset digeser per halaman (untuk KK)
        y_offset_per_page: Offset Y antar halaman saat mode "all" agar tidak overlap
    
    Returns:
        List of dict: {text, x, y, confidence}
    """
    if is_pdf(file_path):
        images = pdf_to_images(file_path)
        
        if not images:
            return []
        
        if page_mode == "first":
            # Ambil hanya halaman pertama
            return extract_text_with_boxes(images[0])
        
        else:  # "all"
            all_boxes = []
            current_y_offset = 0
            
            for page_img in images:
                page_boxes = extract_text_with_boxes(page_img)
                
                # Geser koordinat Y per halaman agar tidak overlap
                for box in page_boxes:
                    box = box.copy()
                    box["y"] = box["y"] + current_y_offset
                    all_boxes.append(box)
                
                # Tambahkan offset untuk halaman berikutnya
                current_y_offset += y_offset_per_page
            
            return all_boxes
    
    else:
        # File gambar biasa
        return extract_text_with_boxes(file_path)


def extract_text_from_image(image_input):
    return extract_text(image_input)