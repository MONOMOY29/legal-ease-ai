import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2

# --- Setup ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-flash-lite-latest")

st.set_page_config(page_title="LegalEase AI", page_icon="📄", layout="wide")
st.title("📄 LegalEase AI")
st.caption("Understand your rental agreement before you sign it — powered by Gemini")

MAX_DOC_CHARS = 20000  # safety limit: avoids excessive API cost/abuse from huge uploads


def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF file."""
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def truncate_document(text: str) -> str:
    """Limit document length for cost/efficiency and to prevent abuse."""
    if len(text) > MAX_DOC_CHARS:
        return text[:MAX_DOC_CHARS]
    return text


def build_summary_prompt(doc: str) -> str:
    return f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Summarize the following rental agreement in plain, simple English. Use short bullet points.
Cover: rent amount, deposit, notice period, who pays what, and any unusual terms.

AGREEMENT:
{doc}"""


def build_risk_prompt(doc: str) -> str:
    return f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Review this rental agreement and list any clauses that could be risky, unusual, or unfair to the tenant
(e.g. excessive deposit forfeiture, one-sided termination rights, hidden charges, vague maintenance terms).
For each, explain briefly why it's worth noticing. If nothing stands out, say so.

AGREEMENT:
{doc}"""


def build_checklist_prompt(doc: str) -> str:
    return f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Based on this rental agreement, generate a short checklist of things the tenant should clarify or ask
the landlord about before signing.

AGREEMENT:
{doc}"""


def build_qa_prompt(doc: str, question: str) -> str:
    return f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Answer the user's question using ONLY the agreement text below. If the answer isn't in the document,
say so clearly instead of guessing.

AGREEMENT:
{doc}

QUESTION: {question}"""


@st.cache_data(show_spinner=False)
def get_ai_response(_model, prompt_text: str) -> str:
    """Call the Gemini API and return the response text. Cached to avoid duplicate calls."""
    response = _model.generate_content(prompt_text)
    return response.text


def safe_generate(prompt_text: str) -> str:
    """Wrapper that never leaks raw exceptions/tracebacks to the user."""
    try:
        return get_ai_response(model, prompt_text)
    except Exception:
        return "⚠️ Something went wrong generating this response. Please wait a moment and try again."


# --- Input section ---
st.subheader("1. Upload or paste your agreement")
input_method = st.radio(
    "Choose how you'd like to provide your agreement",
    ["Upload PDF", "Paste text"],
    help="Upload a PDF file or paste the text of your rental agreement directly."
)

document_text = ""
if input_method == "Upload PDF":
    uploaded_file = st.file_uploader(
        "Upload your rental agreement (PDF)",
        type=["pdf"],
        help="Only PDF files are accepted. Your file is not stored after this session ends."
    )
    if uploaded_file:
        document_text = extract_text_from_pdf(uploaded_file)
else:
    document_text = st.text_area(
        "Paste your agreement text here",
        height=250,
        help="Paste the full text of your rental agreement."
    )

if document_text:
    document_text = truncate_document(document_text)
    st.session_state["document_text"] = document_text

if "document_text" in st.session_state and st.session_state["document_text"]:
    st.subheader("2. What do you want to do?")
    col1, col2 = st.columns(2)
    with col1:
        simplify_btn = st.button("📝 Simplify this agreement", help="Get a plain-English summary")
        risk_btn = st.button("⚠️ Flag risky clauses", help="Highlight unusual or unfair terms")
    with col2:
        checklist_btn = st.button("✅ Generate a clarification checklist", help="Get a pre-signing checklist")

    doc = st.session_state["document_text"]

    if simplify_btn:
        with st.spinner("Reading your agreement..."):
            result = safe_generate(build_summary_prompt(doc))
            st.subheader("Plain-English Summary")
            st.write(result)

    if risk_btn:
        with st.spinner("Checking for risky clauses..."):
            result = safe_generate(build_risk_prompt(doc))
            st.subheader("Risk Flags")
            st.write(result)

    if checklist_btn:
        with st.spinner("Building your checklist..."):
            result = safe_generate(build_checklist_prompt(doc))
            st.subheader("Before You Sign — Checklist")
            st.write(result)

    st.divider()
    st.subheader("3. Ask a question about this agreement")
    user_question = st.text_input(
        "Type your question",
        placeholder="e.g. Can my landlord increase rent mid-year?",
        help="Ask anything specific about the uploaded agreement."
    )
    if st.button("Ask") and user_question:
        with st.spinner("Thinking..."):
            result =
