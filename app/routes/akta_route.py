from fastapi import APIRouter, UploadFile, File
from app.utils.file_validator import validate_upload_file

from app.services.ocr_service import extract_boxes_from_file
from app.parsers.akta_parser import parse_akta
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


@router.post("/ocr/akta", response_model=GenericResponse)
async def ocr_akta(
    file: UploadFile = File(...)
):
    """
    Extract data from Akta Kelahiran (Birth Certificate).
    Mendukung format: JPG, PNG, BMP, TIFF, WEBP, PDF.
    Untuk PDF, hanya halaman pertama yang diproses.
    """

    try:
        os.makedirs("uploads", exist_ok=True)

        # Validasi file: nama, ekstensi, dan ukuran (maks 1 MB)
        validation_error = await validate_upload_file(file)
        if validation_error:
            return validation_error

        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Untuk Akta: hanya halaman pertama (page_mode="first")
        # Akta biasanya 1 halaman, PDF maupun gambar
        ocr_start_time = time.time()
        boxes = extract_boxes_from_file(file_location, page_mode="first")
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

        result = parse_akta(boxes)

        return GenericResponse(
            status="success",
            code=200,
            message="Akta data extracted successfully",
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
        logger.error(f"Error processing Akta: {str(e)})")
        return GenericResponse(
            status="error",
            code=500,
            message="Internal server error",
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message=str(e)
            )
        )