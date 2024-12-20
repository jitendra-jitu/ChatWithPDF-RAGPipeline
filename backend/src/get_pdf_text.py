import PyPDF2

def get_pdf_text(pdf_files):
    text = ""
    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    return text