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

    st.subheader("1. Upload or Paste Rental Agreement")
    input_method = st.radio(
        "Input source",
        ["Upload PDF", "Paste text"],
        horizontal=True,
        label_visibility="collapsed"
    )

    raw_text = ""
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader(
            "Upload Agreement (PDF)",
            type=["pdf"],
            help="Files are processed directly in-memory and not stored."
        )
        if uploaded_file:
            raw_text = extract_text_from_pdf(uploaded_file)
    else:
        raw_text = st.text_area(
            "Paste full agreement text",
            height=200,
            placeholder="Paste raw contract terms here..."
        )

    if raw_text:
        st.session_state["document_text"] = truncate_document(raw_text)

    doc = st.session_state["document_text"]

    if doc:
        st.divider()
        st.subheader("2. Analyze Document")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📝 Plain Summary", use_container_width=True):
                with st.spinner("Analyzing terms..."):
                    st.session_state["summary_output"] = run_gemini_query(build_summary_prompt(doc))

        with col2:
            if st.button("⚠️ Flag Risks", use_container_width=True):
                with st.spinner("Checking clauses..."):
                    st.session_state["risk_output"] = run_gemini_query(build_risk_prompt(doc))

        with col3:
            if st.button("✅ Pre-signing Checklist", use_container_width=True):
                with st.spinner("Compiling checklist..."):
                    st.session_state["checklist_output"] = run_gemini_query(build_checklist_prompt(doc))

        # Persistent Display of Results
        if st.session_state["summary_output"]:
            st.markdown("### Summary")
            st.info(st.session_state["summary_output"])

        if st.session_state["risk_output"]:
            st.markdown("### Risk Analysis")
            st.warning(st.session_state["risk_output"])

        if st.session_state["checklist_output"]:
            st.markdown("### Actionable Checklist")
            st.success(st.session_state["checklist_output"])

        st.divider()
        st.subheader("3. Inquire on Specific Clauses")
        user_question = st.text_input(
            "Clause inquiry",
            placeholder="e.g., Who covers repairs to plumbing and electrical wiring?",
            label_visibility="collapsed"
        )
        if st.button("Search Agreement") and user_question:
            with st.spinner("Reviewing contract..."):
                st.session_state["qa_output"] = run_gemini_query(build_qa_prompt(doc, user_question))

        if st.session_state["qa_output"]:
            st.markdown("### Answer")
            st.write(st.session_state["qa_output"])

    st.divider()
    st.caption("⚖️ **Disclaimer:** LegalEase AI provides informational summaries based on user input, not legal advice. For binding interpretations, consult an advocate registered with the Bar Council.")

if __name__ == "__main__":
    main()