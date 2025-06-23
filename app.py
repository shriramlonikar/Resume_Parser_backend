from fastapi import FastAPI, File, UploadFile, Form
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

load_dotenv()

import os
import google.generativeai as genai
import fitz

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use Redis/db in production)
storage = {}

input_prompt1 = """
 You are an experienced Technical Human Resource Manager,experience in the field of any one job role from full stack web devolopment, data science, AI and ML, Deep learning, Big data Engineering, Softwear Engineering, System analysis, DEVOPS, Data analyst, your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

async def input_pdf_setup(uploaded_file: UploadFile = File(...)):
    if uploaded_file is not None:
        doc = fitz.open(stream=await uploaded_file.read(), filetype="pdf")
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text()
        doc.close()
        return extracted_text
    else:
        raise FileNotFoundError("No File uploaded")

async def get_gemini_responce(system_prompt: str, pdf_text: str, job_description: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    chat = model.start_chat()

    response = chat.send_message(f"""{system_prompt}

Resume:
{pdf_text}

Job Description:
{job_description}
""")
    return response.text

@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    mode: str = Form("review")
):
    # You can conditionally change prompts if needed
    prompt = input_prompt1 if mode == "review" else input_prompt2

    resume_text = await input_pdf_setup(file)
    result = await get_gemini_responce(prompt, resume_text, job_description)

    return {"response": result}



