import os
import base64
import logging
import socket
import requests
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.exceptions import ServiceRequestError, HttpResponseError

logger = logging.getLogger(__name__)

def analyze_read(input_data: str, azure_key: str, azure_url: str, is_base64: bool = False):
    """
    Analyze a document (file path / url / base64) using Azure Form Recognizer prebuilt-read.

    Returns:
        lines: list of DocumentLine SDK objects
        angle: float or None
    """
    try:
        socket.gethostbyname("www.google.com")
        requests.get("https://www.google.com", timeout=3)
    except Exception as e:
        logger.error("No internet connection or DNS resolution failed")
        raise RuntimeError("No internet connection or DNS issue, stopping Aadhaar masking") from e
    
    try:
        client = DocumentAnalysisClient(
            endpoint=azure_url,
            credential=AzureKeyCredential(azure_key)
        )

        if is_base64:
            document_bytes = base64.b64decode(input_data)
            poller = client.begin_analyze_document("prebuilt-read", document=document_bytes)
        elif os.path.exists(input_data):
            with open(input_data, "rb") as f:
                poller = client.begin_analyze_document("prebuilt-read", document=f)
        else:
            # assume URL
            poller = client.begin_analyze_document_from_url("prebuilt-read", input_data)

        result = poller.result()

        # Collect lines (from all pages)
        lines = []
        angle = None
        if result.pages:
            for page in result.pages:
                if hasattr(page, "lines"):
                    lines.extend(page.lines)
            angle = result.pages[0].angle if hasattr(result.pages[0], "angle") else None

        return lines, angle

    except (ServiceRequestError, HttpResponseError, requests.RequestException) as e:
        logger.error(f"Azure Form Recognizer request failed: {e}")
        raise RuntimeError("Azure call failed due to network issue, stopping Aadhaar masking") from e
    except Exception as e:
        logger.exception("Unexpected error during Azure OCR")
        raise