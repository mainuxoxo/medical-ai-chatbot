from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from datetime import datetime

# Modular LangChain imports
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Initialize Flask app
app = Flask(__name__)
load_dotenv()  # Load .env environment variables

# Custom Jinja filter for datetime formatting
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%I:%M %p'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

# Set Hugging Face API token securely
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Inference client setup
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=os.environ["HUGGINGFACEHUB_API_TOKEN"]
)

# System prompt for the assistant
system_prompt = (
    "You are MediBot, an intelligent AI assistant trained on medical documents and literature. You assist users by answering health and medical-related questions using only the information provided in uploaded research papers, clinical guidelines, or medical documents.\n\n"
    "Your audience includes:\n"
    "- **Doctors** seeking quick summaries or clarification.\n"
    "- **Medical students** looking to deepen their understanding.\n"
    "- **General patients** needing clear and simple explanations.\n\n"
    "Instructions:\n"
    "- Tailor your response to the complexity of the question: use technical terms for professionals, but explain clearly and simply for patients.\n"
    "- Do **not** speculate or generate answers beyond the provided documents.\n"
    "- If information is missing, say: *\"That information is not available in the documents you've uploaded.\"*\n"
    "- Avoid giving direct medical advice or diagnoses. Encourage users to consult a healthcare provider for personal health concerns.\n"
    "- Be respectful, accurate, and concise.\n\n"
    "{context}"
)

retriever = None

# Dummy retriever fallback
class DummyRetriever:
    def get_relevant_documents(self, query):
        return []

# Load and process PDF files
def load_pdf_file(directory):
    loaders = [PyPDFLoader(os.path.join(directory, file)) for file in os.listdir(directory) if file.endswith(".pdf")]
    pages = []
    for loader in loaders:
        pages.extend(loader.load())
    return pages

# Split and embed documents
def process_documents(pages):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(pages)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}  # Force CPU usage
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore.as_retriever()

# Home route
@app.route("/")
def home():
    global retriever
    data_dir = "./data"

    if retriever is None:
        if os.path.exists(data_dir):
            pages = load_pdf_file(data_dir)
            retriever = process_documents(pages)
        else:
            print("Warning: './data' folder not found. No documents loaded.")
            retriever = DummyRetriever()

    return render_template("medibot.html", now=datetime.now())

# Handle chat requests 
@app.route("/ask", methods=["POST"])
def ask():
    global retriever
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get relevant documents
    docs = retriever.get_relevant_documents(question)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Construct a cleaner prompt to avoid extra generated questions
    prompt = f"{system_prompt.replace('{context}', context)}\n\nQuestion: {question}\nAnswer:"

    # Send the prompt to Hugging Face with stop sequences to prevent continuation
    response = client.text_generation(
        prompt=prompt,
        max_new_tokens=500,
        temperature=0.7,
        stop_sequences=["User:", "Question:"]
    )

    return jsonify({"answer": response.strip()})


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
