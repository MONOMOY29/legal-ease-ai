import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from pypdf import PdfReader

# --- Environment & Configuration ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

st.set_page_config(
    page_title="LegalEase AI",
    page_icon="📄",
    layout="wide"
)

MAX_DOC_CHARS = 20000  # Safety limit: prevents excessive token consumption

# --- Pure Helper Functions ---
def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF stream."""
    try:
        reader = PdfReader(uploaded_file)
        text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(text).strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def truncate_document(text: str, max_chars: int = MAX_DOC_CHARS) -> str:
    """Trim document to prevent token budget exhaustion."""
    return text[:max_chars] if len(text) > max_chars else text

def build_summary_prompt(doc: str) -> str:
    return (
        "You are an Indian legal literacy assistant for everyday tenants, not an attorney.\n"
        "Summarize this rental agreement in straightforward, plain English using concise bullet points.\n"
        "Cover: rent amount, security deposit & refund rules, notice periods, utility maintenance liability, "
        "and any unusual clauses.\n\n"
        f"AGREEMENT:\n{doc}"
    )

def build_risk_prompt(doc: str) -> str:
    return (
        "You are an Indian legal literacy assistant for everyday tenants, not an attorney.\n"
        "Analyze this agreement and flag clauses that pose risks, excessive forfeiture penalties, "
        "asymmetrical termination clauses, or vague landlord liabilities.\n"
        "Explain clearly why each flag matters in daily life. If clean, explicitly confirm.\n\n"
        f"AGREEMENT:\n{doc}"
    )

def build_checklist_prompt(doc: str) -> str:
    return (
        "You are an Indian legal literacy assistant for everyday tenants.\n"
        "Provide a high-priority, actionable checklist of questions or missing terms the tenant "
        "should demand in writing before executing this agreement.\n\n"
        f"AGREEMENT:\n{doc}"
    )

def build_qa_prompt(doc: str, question: str) -> str:
    return (
        "You are an Indian legal literacy assistant for everyday tenants.\n"
        "Answer the question strictly and solely based on the text provided below. "
        "If the information is not explicitly documented, state that it is not covered.\n\n"
        f"AGREEMENT:\n{doc}\n\n"
        f"QUESTION: {question}"
    )

def run_gemini_query(prompt_text: str, model_name: str = "gemini-2.5-flash") -> str:
    """API wrapper with safe failure fallback."""
    if not api_key:
        return "⚠️ Gemini API Key not found. Please provide GEMINI_API_KEY in your environment or .env file."
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as err:
        return f"⚠️ Service error encountered: {str(err)}"


# --- Main Application Interface ---
def main():
    st.title("📄 LegalEase AI")
    st.caption("Understand your rental agreement before signing — Powered by Google Gemini")

    if not api_key:
        st.warning("⚠️ GEMINI_API_KEY environment variable is not configured. AI features will remain offline.", icon="⚠️")

    # Initialize Session State
    for key in ["summary_output", "risk_output", "checklist_output", "qa_output", "document_text"]:
        if key not in st.session_state:
            st.session_state[key] = ""

    st.subheader("1. Upload or
