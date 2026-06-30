from fastapi import APIRouter, UploadFile, File

from app.services.ocr_service import extract_boxes_from_file
from app.parsers.ktp_parser import parse_ktp
from app.preprocess.image_preprocess import preprocess_image
from app.schemas.generic_response import (
    GenericResponse,
    ErrorDetail
)

import shutil
import os
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp", ".pdf"}


@router.post("/ocr/ktp", response_model=GenericResponse)
async def ocr_ktp(file: UploadFile = File(...)):
    """
    Extract data from KTP (Kartu Tanda Penduduk).
    Mendukung format: JPG, PNG, BMP, TIFF, WEBP, PDF.
    Untuk PDF, hanya halaman pertama yang diproses.
    """

    try:
        os.makedirs("uploads", exist_ok=True)

        if not file.filename:
            return GenericResponse(
                status="error",
                code=400,
                message="File name is required",
                error=ErrorDetail(
                    code="INVALID_FILE",
                    message="File name cannot be empty"
                )
            )

        # Validasi ekstensi file
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return GenericResponse(
                status="error",
                code=400,
                message=f"Format file tidak didukung: {ext}",
                error=ErrorDetail(
                    code="UNSUPPORTED_FORMAT",
                    message=f"Gunakan salah satu format: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            )

        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Untuk KTP: hanya proses halaman pertama (page_mode="first")
        # Jika gambar biasa, preprocess dulu menggunakan image_preprocess
        # Jika PDF, konversi langsung melalui extract_boxes_from_file
        ocr_start_time = time.time()

        if ext == ".pdf":
            boxes = extract_boxes_from_file(file_location, page_mode="first")
        else:
            processed_path = preprocess_image(file_location)
            boxes = extract_boxes_from_file(processed_path, page_mode="first")

        ocr_elapsed_time = time.time() - ocr_start_time

        if not boxes:
            return GenericResponse(
                status="error",
                code=422,
                message="No text detected in file",
                error=ErrorDetail(
                    code="NO_TEXT_DETECTED",
                    message="OCR could not extract any text from the file"
                )
            )

        # Calculate accuracy percentage
        confidences = [box["confidence"] for box in boxes if "confidence" in box]
        accuracy = (sum(confidences) / len(confidences)) * 100 if confidences else 0.0
        accuracy = round(accuracy, 2)

        result = parse_ktp(boxes)

        return GenericResponse(
            status="success",
            code=200,
            message="KTP data extracted successfully",
            data=result,
            raw_text=boxes,
            accuracy_percentage=accuracy,
            elapsed_time=round(ocr_elapsed_time, 3)
        )

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return GenericResponse(
            status="error",
            code=404,
            message="File not found",
            error=ErrorDetail(
                code="FILE_NOT_FOUND",
                message=str(e)
            )
        )

    except Exception as e:
        logger.error(f"Error processing KTP: {str(e)}")
        return GenericResponse(
            status="error",
            code=500,
            message="Internal server error",
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message=str(e)
            )
        )