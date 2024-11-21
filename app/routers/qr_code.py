from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List
from app.schema import QRCodeRequest, QRCodeResponse
from app.services.qr_service import generate_qr_code, list_qr_codes, delete_qr_code
from app.utils.common import decode_filename_to_url, encode_url_to_filename, generate_links
from app.config import QR_DIRECTORY, SERVER_BASE_URL, FILL_COLOR, BACK_COLOR, SERVER_DOWNLOAD_FOLDER
import logging

# Set up router and authentication
router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint to create a QR code
@router.post("/qr-codes/", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED, tags=["QR Codes"])
async def create_qr_code(request: QRCodeRequest, token: str = Depends(oauth2_scheme)):
    """
    Creates a QR code for a given URL and stores it in the configured directory.
    """
    logging.info(f"Creating QR code for URL: {request.url}")
    
    # Encode the URL to a filename-safe base64 string
    encoded_url = encode_url_to_filename(request.url)
    qr_filename = f"{encoded_url}.png"
    qr_code_full_path = QR_DIRECTORY / qr_filename
    qr_code_download_url = f"{SERVER_BASE_URL}/{SERVER_DOWNLOAD_FOLDER}/{qr_filename}"
    
    # Generate HATEOAS links
    links = generate_links("create", qr_filename, SERVER_BASE_URL, qr_code_download_url)

    # Check if QR code already exists
    if qr_code_full_path.exists():
        logging.info(f"QR code already exists: {qr_code_full_path}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "QR code already exists.",
                "qr_code_url": qr_code_download_url,
                "links": links,
            }
        )

    # Generate the QR code
    generate_qr_code(request.url, qr_code_full_path, FILL_COLOR, BACK_COLOR, request.size)
    logging.info(f"QR code created: {qr_code_full_path}")

    # Return success response
    return QRCodeResponse(
        message="QR code created successfully.",
        qr_code_url=qr_code_download_url,
        links=links
    )

# Endpoint to list all QR codes
@router.get("/qr-codes/", response_model=List[QRCodeResponse], tags=["QR Codes"])
async def list_qr_codes_endpoint(token: str = Depends(oauth2_scheme)):
    """
    Lists all available QR codes in the configured directory.
    """
    logging.info("Listing all QR codes.")

    # Get list of QR code files
    qr_files = list_qr_codes(QR_DIRECTORY)
    if not qr_files:
        logging.warning("No QR codes found.")
        return []

    # Generate responses for each QR code
    responses = [
        QRCodeResponse(
            message="QR code available",
            qr_code_url=decode_filename_to_url(qr_file[:-4]),  # Decode filename to URL
            links=generate_links("list", qr_file, SERVER_BASE_URL, f"{SERVER_BASE_URL}/{SERVER_DOWNLOAD_FOLDER}/{qr_file}")
        )
        for qr_file in qr_files
    ]
    return responses

# Endpoint to delete a QR code
@router.delete("/qr-codes/{qr_filename}", status_code=status.HTTP_204_NO_CONTENT, tags=["QR Codes"])
async def delete_qr_code_endpoint(qr_filename: str, token: str = Depends(oauth2_scheme)):
    """
    Deletes a QR code file by its filename.
    """
    logging.info(f"Deleting QR code: {qr_filename}")
    qr_code_path = QR_DIRECTORY / qr_filename

    # Check if file exists
    if not qr_code_path.is_file():
        logging.warning(f"QR code not found: {qr_filename}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )

    # Delete the QR code file
    delete_qr_code(qr_code_path)
    logging.info(f"QR code deleted: {qr_code_path}")

    # Return 204 No Content
    return Response(status_code=status.HTTP_204_NO_CONTENT)
