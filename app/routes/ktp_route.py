from fastapi import APIRouter, UploadFile, File
from typing import Optional

from app.services.ocr_service import (
    extract_text_with_boxes,
)
from app.parsers.ktp_parser import parse_ktp
from app.schemas.ktp_response import KtpResponse
from app.preprocess.image_preprocess import preprocess_image
from app.cropper.ktp_cropper import crop_ktp_fields
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


@router.post("/ocr/ktp", response_model=GenericResponse)
async def ocr_ktp(file: UploadFile = File(...)):
    """
    Extract data from KTP (Kartu Tanda Penduduk) image
    """
    
    try:
        os.makedirs("uploads", exist_ok=True)

        file_location = f"uploads/{file.filename}"

        # Validate file
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

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        processed_path = preprocess_image(
            file_location
        )

        # OCR seluruh gambar - measure elapsed time
        ocr_start_time = time.time()
        boxes = extract_text_with_boxes(
            processed_path
        )
        ocr_elapsed_time = time.time() - ocr_start_time

        if not boxes:
            return GenericResponse(
                status="error",
                code=422,
                message="No text detected in image",
                error=ErrorDetail(
                    code="NO_TEXT_DETECTED",
                    message="OCR could not extract any text from the image"
                )
            )

        # Calculate accuracy percentage
        confidences = [box["confidence"] for box in boxes if "confidence" in box]
        accuracy = (sum(confidences) / len(confidences)) * 100 if confidences else 0.0
        accuracy = round(accuracy, 2)

        result = parse_ktp(
            boxes
        )

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