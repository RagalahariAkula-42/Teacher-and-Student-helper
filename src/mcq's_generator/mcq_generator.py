import os
from dotenv import load_dotenv
import streamlit as st
import pdfplumber
import docx
from fpdf import FPDF
import google.generativeai as genai

load_dotenv('../../.env')
# Set up Google API key for Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Set up Streamlit title and description
st.title("AI-Powered MCQ Generator")
st.write("Upload a file (PDF, DOCX, or TXT) and generate multiple-choice questions (MCQs) based on its content.")

# Function to extract text from various file formats
def extract_text_from_file(file_path):
    ext = file_path.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        with pdfplumber.open(file_path) as pdf:
            text = ''.join([page.extract_text() for page in pdf.pages])
        return text
    elif ext == 'docx':
        doc = docx.Document(file_path)
        text = ' '.join([para.text for para in doc.paragraphs])
        return text
    elif ext == 'txt':
        with open(file_path, 'r') as file:
            return file.read()
    return None

# Function to generate MCQs using Google's Gemini AI model
def Question_mcqs_generator(input_text, num_questions):
    prompt = f"""
    You are an AI assistant helping the user generate multiple-choice questions (MCQs) based on the following text:
    '{input_text}'
    Please generate {num_questions} MCQs from the text. Each question should have:
    - A clear question
    - Four answer options (labeled A, B, C, D)
    - The correct answer clearly indicated
    Format:
    ## MCQ
    Question: [question]
    A) [option A]
    B) [option B]
    C) [option C]
    D) [option D]
    Correct Answer: [correct option]
    """
    response = model.generate_content(prompt).text.strip()
    return response

# Function to save MCQs to a text file
def save_mcqs_to_file(mcqs, filename):
    with open(filename, 'w') as f:
        f.write(mcqs)

# Function to create a PDF from the MCQs
def create_pdf(mcqs, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for mcq in mcqs.split("## MCQ"):
        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)  # Add a line break
    pdf.output(filename)

# Streamlit file uploader
file = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=['pdf', 'docx', 'txt'])

if file:
    num_questions = st.number_input("Number of questions to generate", min_value=1, max_value=20)
    
    # Save the uploaded file to the server temporarily
    temp_file_path = f"temp_{file.name}"
    with open(temp_file_path, 'wb') as f:
        f.write(file.getbuffer())
    
    # Extract text from the uploaded file
    text = extract_text_from_file(temp_file_path)
    
    if text:
        if st.button('Generate MCQs'):
            mcqs = Question_mcqs_generator(text, num_questions)
            txt_filename = f"generated_mcqs_{file.name.rsplit('.', 1)[0]}.txt"
            pdf_filename = f"generated_mcqs_{file.name.rsplit('.', 1)[0]}.pdf"
            
            # Save MCQs to files
            save_mcqs_to_file(mcqs, txt_filename)
            create_pdf(mcqs, pdf_filename)
            
            # Show the results and provide download links
            st.write("### Generated MCQs")
            st.text_area("Generated MCQs", mcqs, height=300)
            
            # Provide download buttons for txt and pdf files
            with open(txt_filename, "r") as txt_file:
                st.download_button("Download as TXT", txt_file, file_name=txt_filename)
            
            with open(pdf_filename, "rb") as pdf_file:
                st.download_button("Download as PDF", pdf_file, file_name=pdf_filename)
    else:
        st.error("Unable to extract text from the uploaded file.")
