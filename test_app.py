from app import extract_text_from_pdf

def test_extract_text_from_pdf_is_callable():
    assert callable(extract_text_from_pdf)

def test_model_name_configured():
    with open("app.py") as f:
        content = f.read()
    assert "GenerativeModel" in content

def test_error_handling_present():
    with open("app.py") as f:
        content = f.read()
    assert "except Exception" in content
