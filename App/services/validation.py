from langchain_community.document_loaders import PyPDFLoader


class ValidationError(Exception):
    """Raised when an uploaded file fails validation checks."""
    pass


MAX_FILE_SIZE_MB = 5
MIN_EXTRACTABLE_CHARS = 50


def validate_uploaded_file(uploaded_file) -> None:
    """
    Validates a Streamlit UploadedFile object before it's saved to disk.
    Raises ValidationError with a clear message if invalid.
    """
    if uploaded_file is None:
        raise ValidationError("No file was uploaded.")

    if uploaded_file.size == 0:
        raise ValidationError("The uploaded file is empty.")

    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValidationError(
            f"File too large ({file_size_mb:.1f} MB). Max allowed is {MAX_FILE_SIZE_MB} MB."
        )

    if not uploaded_file.name.lower().endswith(".pdf"):
        raise ValidationError("Only PDF files are supported.")


def validate_pdf_has_text(file_path: str) -> None:
    """
    Validates that a saved PDF file actually contains extractable text
    (catches scanned/image-only PDFs). Raises ValidationError if not.
    """
    try:
        pages = PyPDFLoader(file_path).load()
    except Exception as e:
        raise ValidationError(f"Could not read PDF file: {e}")

    total_text = "".join(p.page_content.strip() for p in pages)
    if len(total_text) < MIN_EXTRACTABLE_CHARS:
        raise ValidationError(
            "This PDF has little to no extractable text. "
            "It might be a scanned image — please upload a text-based PDF."
        )