import streamlit as st
import pdfplumber
from openai import OpenAI

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

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
    
    if st.button("Analyze Board Meeting"):
        with st.spinner("Analyzing transcript..."):
            extracted_text = extract_text_with_pdfplumber(uploaded_file)
            
            response = client.responses.create(
                model="o4-mini",
                input=f'''
                    You are an expert in board meetings and performance of non-executive board members in their duties. 
                    You have the following tasks:

                    Bias Detection
                    - ⁠Monitor for cognitive bias patterns:
                        * Anchoring: "We said $10M last quarter, so let's stick close to that"
                        * Confirmation: Only discussing data that supports a predetermined conclusion
                        * Availability: Over-weighting recent events or easily recalled examples
                        * Groupthink: Lack of dissenting voices or premature consensus

                    Devil's Advocate
                    - ⁠Generate real-time counterarguments:
                        * "What if the market conditions change?"
                        * "Have we considered the regulatory risks?"
                        * "What evidence contradicts this assumption?"
                        * Surfaces alternative interpretations of the same data

                    Decision Pattern Analysis
                    - ⁠Track decision-making patterns:
                        * Who speaks most vs. least
                        * How quickly decisions are reached
                        * Whether dissenting views are explored
                        * Historical consistency with similar past decisions

                    Evidence Quality Analysis
                    - ⁠Evaluate the strength of arguments:
                        * Are claims backed by data?
                        * Are sources credible and recent?
                        * Are there logical fallacies in reasoning?
                        * Are key stakeholder perspectives missing?

                    Please apply the four above-stated analyses on the following text and then provide your report in the format
                    of the 4 different tasks:

                    {extracted_text}

                    Format your ouput in Markdown style.
                '''
            )

            st.markdown(response.output_text)

            st.download_button(
                "Download Report",
                data=response.output_text,
                file_name=f"{uploaded_file.name}_boardai_analysis.txt",
                mime="text/plain"
            )



