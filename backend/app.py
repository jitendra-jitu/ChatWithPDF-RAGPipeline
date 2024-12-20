import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables (Google API key)
load_dotenv()
os.getenv("GOOGLE_API_KEY")

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])  # Allow React frontend only

# Define the folder to store PDF files temporarily
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16 MB

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Allowed file types
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Utility functions for processing PDFs
def get_pdf_text(pdf_files):
    text = ""
    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'pdfFiles' not in request.files:
        return jsonify({"message": "No files part"}), 400
    pdf_files = request.files.getlist('pdfFiles')
    filenames = []
    for pdf in pdf_files:
        if pdf and allowed_file(pdf.filename):
            filename = secure_filename(pdf.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf.save(filepath)
            filenames.append(filepath)
        else:
            return jsonify({"message": "Invalid file type. Only PDF allowed."}), 400

    # Process PDFs and save vector store
    raw_text = get_pdf_text(filenames)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)

    return jsonify({"message": "Files uploaded and processed successfully."})

@app.route('/ask', methods=['POST'])
def ask_question():
    user_question = request.json.get('question')
    if not user_question:
        return jsonify({"message": "No question provided"}), 400

    # Load vector store and perform similarity search
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = new_db.similarity_search(user_question)

    # Get the conversational chain and get the response
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    return jsonify({"answer": response["output_text"]})

if __name__ == "__main__":
    app.run(debug=True)
