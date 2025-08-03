import streamlit as st
import pdfplumber
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

response = client.responses.create(
    model="gpt-4.1",
    input="Write a one-sentence bedtime story about a unicorn."
)

st.text(response.output_text)

def extract_text_with_pdfplumber(pdf_file):
    """Extract text using pdfplumber with better formatting"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            all_text = []
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    all_text.append(f"--- Page {i + 1} ---\n{page_text}\n")
                else:
                    all_text.append(f"--- Page {i + 1} ---\n[No text found on this page]\n")
            
            return "\n".join(all_text)
    except Exception as e:
        return f"Error extracting text: {str(e)}"

st.title("BoardAI")

st.subheader("Have your smartest non-exec in the room with you.")

st.text('''
    BoardAI is an llm-powered tool for evaluating the performance of your board meetings. Identify gaps, uncover risks and constantly improve.
        
    How it works:
        1. Record a transcript of your latest board meeting.
        2. Upload your transcript and click on 'analyze'.
        3. BoardAI identifies potential improvements and provides a report.
''')

st.subheader("Upload a trancript:")

uploaded_file = st.file_uploader("",type="pdf")

if uploaded_file is not None:
    st.success("PDF uploaded successfully!")
    
    if st.button("Extract Text"):
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_with_pdfplumber(uploaded_file)
            
            st.subheader("Extracted Text")
            st.text_area("Text", extracted_text, height=400)
            
            st.download_button(
                "Download Text",
                data=extracted_text,
                file_name=f"{uploaded_file.name}_extracted.txt",
                mime="text/plain"
            )

