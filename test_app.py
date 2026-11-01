from unittest.mock import MagicMock, patch
import io
from app import (
    extract_text_from_pdf,
    truncate_document,
    build_summary_prompt,
    build_risk_prompt,
    build_checklist_prompt,
    build_qa_prompt,
    run_gemini_query,
    MAX_DOC_CHARS,
)

def test_truncate_document_under_limit():
    short_text = "Rental agreement between Party A and Party B."
    assert truncate_document(short_text) == short_text

def test_truncate_document_over_limit():
    long_text = "A" * (MAX_DOC_CHARS + 500)
    result = truncate_document(long_text)
    assert len(result) == MAX_DOC_CHARS

def test_build_summary_prompt():
    doc = "Rent: 15,000 INR per month."
    prompt = build_summary_prompt(doc)
    assert doc in prompt
    assert "plain english" in prompt.lower()

def test_build_risk_prompt():
    doc = "Security deposit non-refundable under any circumstance."
    prompt = build_risk_prompt(doc)
    assert doc in prompt
    assert "risks" in prompt.lower() or "flag" in prompt.lower()

def test_build_checklist_prompt():
    doc = "Agreement valid for 11 months."
    prompt = build_checklist_prompt(doc)
    assert doc in prompt
    assert "checklist" in prompt.lower()

def test_build_qa_prompt():
    doc = "Notice period is 30 days."
    query = "What is the notice period?"
    prompt = build_qa_prompt(doc, query)
    assert doc in prompt
    assert query in prompt

@patch("app.genai.GenerativeModel")
def test_run_gemini_query_success(mock_model_class):
    mock_instance = MagicMock()
    mock_instance.generate_content.return_value.text = "This is a clean summary."
    mock_model_class.return_value = mock_instance

    with patch("app.api_key", "test-key-12345"):
        result = run_gemini_query("Summarize this document")
        assert result == "This is a clean summary."

@patch("app.genai.GenerativeModel")
def test_run_gemini_query_exception_handling(mock_model_class):
    mock_instance = MagicMock()
    mock_instance.generate_content.side_effect = RuntimeError("Quota limit reached")
    mock_model_class.return_value = mock_instance

    with patch("app.api_key", "test-key-12345"):
        result = run_gemini_query("Analyze clauses")
        assert "Service error encountered" in result
        assert "Quota limit reached" in result
