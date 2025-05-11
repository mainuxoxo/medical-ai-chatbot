from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings
from pinecone.grpc import PineconeGRPC as pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPEN_API_KEY = os.environ.get('OPEN_API_KEY')

data_directory = os.path.abspath("data/")
extracted_data = load_pdf_file(data_directory)
	
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

pc = pinecone(api_key=PINECONE_API_KEY)
index_name = "medibot"

# Check if the index already exists
if index_name not in pc.list_indexes():
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        )
    )
    print(f"Index '{index_name}' created.")
else:
    print(f"Index '{index_name}' already exists.")


    # Create the PineconeVectorStore and embed automatically
docsearch = PineconeVectorStore.from_texts(
    texts=[chunk.page_content for chunk in text_chunks],
    embedding=embeddings, 
    index_name=index_name,
)
print("Embeddings upserted into Pinecone index successfully.")

