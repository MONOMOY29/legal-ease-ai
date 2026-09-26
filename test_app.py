from app import (
    extract_text_from_pdf,
    truncate_document,
    build_summary_prompt,
    build_risk_prompt,
    build_checklist_prompt,
    build_qa_prompt,
    safe_generate,
    MAX_DOC_CHARS,
)


def test_extract_text_from_pdf_is_callable():
    assert callable(extract_text_from_pdf)


def test_truncate_document_under_limit():
    short_text = "hello world"
    assert truncate_document(short_text) == short_text


def test_truncate_document_over_limit():
    long_text = "a" * (MAX_DOC_CHARS + 500)
    result = truncate_document(long_text)
    assert len(result) == MAX_DOC_CHARS


def test_build_summary_prompt_includes_document():
    doc = "Rent is 10000 per month."
    prompt = build_summary_prompt(doc)
    assert doc in prompt
    assert "plain" in prompt.lower()


def test_build_risk_prompt_includes_document():
    doc = "Deposit is non-refundable."
    prompt = build_risk_prompt(doc)
    assert doc in prompt
    assert "risky" in prompt.lower() or "unfair" in prompt.lower()


def test_build_checklist_prompt_includes_document():
    doc = "Notice period is one month."
    prompt = build_checklist_prompt(doc)
    assert doc in prompt
    assert "checklist" in prompt.lower()


def test_build_qa_prompt_includes_question_and_document():
    doc = "Rent due on the 5th."
    question = "When is rent due?"
    prompt = build_qa_prompt(doc, question)
    assert doc in prompt
    assert question in prompt


def test_safe_generate_handles_failure_gracefully(monkeypatch):
    import app

    def broken_get_ai_response(_model, prompt_text):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(app, "get_ai_response", broken_get_ai_response)
    result = safe_generate("any prompt")
    assert "went wrong" in result.lower()


def test_error_handling_present_in_source():
    with open("app.py") as f:
        content = f.read()
    assert "except Exception" in content


def test_model_configured_in_source():
    with open("app.py") as f:
        content = f.read()
    assert "GenerativeModel" in content
