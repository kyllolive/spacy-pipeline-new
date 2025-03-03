from PyPDF2 import PdfReader, PdfWriter
import tempfile
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("document_pipeline.log"), logging.StreamHandler()],
)

logger = logging.getLogger("document_pipeline")


def get_pdf_files(pdf_dir):
    """Get a list of all PDF files in the directory."""
    pdf_files = []
    for root, _, files in os.walk(pdf_dir):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    logger.info(f"Found {len(pdf_files)} PDF files")
    return pdf_files


def extract_first_page(pdf_path):
    """
    Extract the first page of a PDF file.
    """
    # Create a temporary file for the first page
    temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(temp_fd)

    # Extract the first page
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()

    if len(pdf_reader.pages) > 0:
        pdf_writer.add_page(pdf_reader.pages[0])

    # Write the first page to the temporary file
    with open(temp_path, "wb") as temp_file:
        pdf_writer.write(temp_file)

    return temp_path


def extract_original_filename(pdf_path):
    """
    Extract the original filename from the PDF path.
    """
    return os.path.basename(pdf_path)


def strip_filename(pdf_path):
    """
    Extract the original filename from the PDF path without the extension.
    """
    if pdf_path.endswith(".pdf"):
        formatted_number = pdf_path[:-4]

        parts = formatted_number.split("-")
        if len(parts) > 1:
            year = parts[0]
            rest = parts[1:]
            return "-".join(rest) + "-" + year
        else:
            return formatted_number
