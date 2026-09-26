# LegalEase AI

A GenAI-powered assistant that helps Indian tenants understand rental agreements before signing.

## Features
- **Simplify**: Plain-English summary of the agreement
- **Risk Flags**: Highlights unusual, vague, or unfair clauses
- **Checklist**: Auto-generated pre-signing questions to ask the landlord
- **Q&A**: Ask specific questions, answered strictly from the uploaded document

## Tech Stack
- Streamlit (frontend/backend)
- Google Gemini API (`gemini-flash-lite-latest`) via `google-generativeai` SDK
- PyPDF2 for PDF text extraction

## Setup
```bash
pip install -r requirements.txt
```
Create a `.env` file with:
