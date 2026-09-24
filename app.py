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

# --- Helper: extract text from PDF ---
def extract_text_from_pdf(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Input section ---
st.subheader("1. Upload or paste your agreement")
input_method = st.radio("Choose input method:", ["Upload PDF", "Paste text"])

document_text = ""
if input_method == "Upload PDF":
    uploaded_file = st.file_uploader("Upload your rental agreement (PDF)", type=["pdf"])
    if uploaded_file:
        document_text = extract_text_from_pdf(uploaded_file)
else:
    document_text = st.text_area("Paste your agreement text here", height=250)

# --- Store in session so it persists across button clicks ---
if document_text:
    st.session_state["document_text"] = document_text

# --- Action buttons ---
if "document_text" in st.session_state and st.session_state["document_text"]:
    st.subheader("2. What do you want to do?")
    col1, col2 = st.columns(2)
    with col1:
        simplify_btn = st.button("📝 Simplify this agreement")
        risk_btn = st.button("⚠️ Flag risky clauses")
    with col2:
        checklist_btn = st.button("✅ Generate a clarification checklist")

    doc = st.session_state["document_text"]

    if simplify_btn:
        with st.spinner("Reading your agreement..."):
            prompt = f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Summarize the following rental agreement in plain, simple English. Use short bullet points.
Cover: rent amount, deposit, notice period, who pays what, and any unusual terms.

AGREEMENT:
{doc}"""
            response = model.generate_content(prompt)
            st.subheader("Plain-English Summary")
            st.write(response.text)

    if risk_btn:
        with st.spinner("Checking for risky clauses..."):
            prompt = f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Review this rental agreement and list any clauses that could be risky, unusual, or unfair to the tenant
(e.g. excessive deposit forfeiture, one-sided termination rights, hidden charges, vague maintenance terms).
For each, explain briefly why it's worth noticing. If nothing stands out, say so.

AGREEMENT:
{doc}"""
            response = model.generate_content(prompt)
            st.subheader("Risk Flags")
            st.write(response.text)

    if checklist_btn:
        with st.spinner("Building your checklist..."):
            prompt = f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Based on this rental agreement, generate a short checklist of things the tenant should clarify or ask
the landlord about before signing.

AGREEMENT:
{doc}"""
            response = model.generate_content(prompt)
            st.subheader("Before You Sign — Checklist")
            st.write(response.text)

    st.divider()
    st.subheader("3. Ask a question about this agreement")
    user_question = st.text_input("e.g. 'Can my landlord increase rent mid-year?'")
    if st.button("Ask") and user_question:
        with st.spinner("Thinking..."):
            prompt = f"""You are a legal literacy assistant for everyday renters in India, not a lawyer.
Answer the user's question using ONLY the agreement text below. If the answer isn't in the document,
say so clearly instead of guessing.

AGREEMENT:
{doc}

QUESTION: {user_question}"""
            response = model.generate_content(prompt)
            st.write(response.text)

st.divider()
st.caption("⚠️ This tool provides general information, not legal advice. For serious concerns, consult a qualified lawyer.")