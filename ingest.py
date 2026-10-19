import os
import pytesseract
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from PIL import Image
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

file_path = 'data/documents'

load_dotenv()

def load_documents():
    documents = []
    for document in Path(file_path).glob('*.pdf'):
        loader = PyPDFLoader(
            str(document),
        )
        docs = loader.load()
        for doc in docs:
            doc.metadata['source']=document.name
        documents.extend(docs)
    for document in Path(file_path).glob('*.txt'):
        loader = TextLoader(
            str(document),
            encoding='utf-8'
        )
        docs = loader.load()
        for doc in docs:
            doc.metadata['source']=document.name
        documents.extend(docs)
    for document in Path(file_path).glob('*.png'):
        image = Image.open(document)
        text = pytesseract.image_to_string(image)
        if text.strip():
            doc = Document(
                page_content=text,
                metadata={'source':document.name,"file_type": "image",}
            )
        documents.append(text)
    return documents


def chunking(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=550,
        chunk_overlap=60
    )
    chunking = splitter.split_documents(documents)
    return chunking


def vectorstore(chunking):
    embeddings = HuggingFaceEmbeddings(
        model_name='all-MiniLM-L6-V2'
    )
    vector_store = Chroma.from_documents(
        documents=chunking,
        embedding=embeddings,
        persist_directory=os.getenv('ChromaDB_Path'),
        collection_name='private_doc'
    )
    return vector_store

def main():
    documents = load_documents()
    text_splitter = chunking(documents)
    vectorstore(text_splitter)

if __name__=='__main__':
    main()