import os
import sys
import traceback
from pathlib import Path
import logging

# Ensure we see logging from app modules on stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Ensure project root is on sys.path so `import app` works
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

UPLOADS_DIR = Path("uploads")

def find_image():
    if not UPLOADS_DIR.exists():
        return None
    for ext in ("*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff"):
        files = list(UPLOADS_DIR.glob(ext))
        if files:
            return files[0]
    return None


def main():
    img = find_image()
    if img is None:
        print("NO_UPLOAD_IMAGE_FOUND")
        return

    print(f"Testing image: {img}", flush=True)

    try:
        from app.services import ocr_service
        print("ocr_model is None:", ocr_service.ocr_model is None, flush=True)

        print("Calling init_ocr_model()...", flush=True)
        try:
            ocr_service.init_ocr_model()
            print("init_ocr_model returned; ocr_model is None:", ocr_service.ocr_model is None, flush=True)
        except Exception as e:
            print("init_ocr_model exception:", e, flush=True)
            traceback.print_exc()

        # Only attempt OCR if model initialized
        if ocr_service.ocr_model is not None:
            boxes = ocr_service.extract_text_with_boxes(str(img))
            print("boxes_count:", len(boxes), flush=True)
            for i, b in enumerate(boxes[:10]):
                print(i, b, flush=True)

            text = ocr_service.extract_text(str(img))
            print("extracted_text_sample:\n", text[:800], flush=True)
        else:
            print("Skipping OCR: model not available", flush=True)

    except Exception as e:
        print("ERROR during OCR test:\n", e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
