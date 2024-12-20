import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv



from src.get_pdf_text import get_pdf_text
from src.get_text_chunks import get_text_chunks
from src.get_vector_store import get_vector_store
from src.get_conversational_chain import get_conversational_chain
from src.allowed_file import allowed_file


load_dotenv()
os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


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
    raw_text = get_pdf_text(filenames)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)
    return jsonify({"message": "Files uploaded and processed successfully."})

@app.route('/ask', methods=['POST'])
def ask_question():
    user_question = request.json.get('question')
    if not user_question:
        return jsonify({"message": "No question provided"}), 400
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
    return jsonify({"answer": response["output_text"]})

if __name__ == "__main__":
    app.run(debug=True)
