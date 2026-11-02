# 📄 LegalEase AI: Indian Rental Agreement Literacy Assistant
## Build note
Built with AI-assisted development (live-coded with AI tools).
My role: solo 
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)](https://streamlit.io/)
[![Gemini API](https://img.shields.io/badge/Model-Gemini%201.5%20Flash-4E75F6.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An AI-powered legal document interpreter built to help everyday tenants navigate complex residential leases, identify unfair terms, and clarify contractual obligations before signing.

---

## 🎯 The Problem
Residential lease agreements in India frequently include ambiguous maintenance clauses, asymmetric termination penalties, and arbitrary security deposit forfeiture conditions. Most tenants sign without reading dense legal text due to confusing terminology.

## 💡 Solution Architecture
LegalEase AI processes PDFs or raw text in-memory, normalizes document context, and executes specialized system-prompt queries using **Google Gemini 1.5 Flash**:
- **Plain-English Summarization:** Distills rent schedules, notice periods, and payment responsibilities.
- **Risk Detection Engine:** Flags one-sided clauses, excessive penalty rates, and hidden liabilities.
- **Pre-Signing Checklist:** Suggests critical questions to clarify with landlords prior to signing.
- **Grounded Q&A:** Answers user queries strictly based on provided text to eliminate hallucinations.

---

## 🛠️ Tech Stack
- **Frontend / UI:** Streamlit
- **LLM Engine:** Google Gemini Flash (`google-generativeai` SDK)
- **Document Ingestion:** `pypdf`
- **Testing Suite:** `pytest` (with mocked API fixtures)

---

## 🚀 Quickstart Guide

### 1. Clone the repository
```bash
git clone [https://github.com/MONOMOY29/legal-ease-ai.git](https://github.com/MONOMOY29/legal-ease-ai.git)
cd legal-ease-ai
