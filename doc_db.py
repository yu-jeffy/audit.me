# sqlite fix for python 3.10.2
# https://docs.trychroma.com/troubleshooting#sqlite
import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# langchain imports
from langchain.docstore.document import Document
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import JSONLoader

# other imports
import os
from dotenv import load_dotenv
import json
from pathlib import Path
from pprint import pprint

load_dotenv()


################################################
# load documents
################################################

# load solidity smart contracts
loader = DirectoryLoader('contracts', glob="**/*.sol", show_progress=True) #silent_errors=True

sol_docs = loader.load()

print(f"Number of Solidity contracts loaded: {len(sol_docs)}")

# load json files
json_loader = JSONLoader(
    file_path='contracts/vulns.jsonl',
    jq_schema='.body',
    text_content=False,
    json_lines=True)

json_docs = json_loader.load()

# full array of all documents
sol_docs.extend(json_docs)

docs = sol_docs

print(f"Number of total documents loaded: {len(docs)}")

################################################
#  split documents into chunks
################################################
text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=256, chunk_overlap=0
)

doc_chunks = []

for doc_index, doc in enumerate(docs):
    print(f"Processing document {doc_index + 1}/{len(docs)}")
    sol_code = doc.page_content
    
    split_docs = text_splitter.split_text(sol_code)

    for chunk in split_docs:
        doc_chunks.append(Document(page_content=chunk, metadata={}))

print(f"Number of documents after splitting: {len(doc_chunks)}")

################################################
#  create embeddings
################################################
# embedding function
# embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-ada-002")

# embeddings = embeddings_model.embed_documents(sol_docs)

################################################
#  create vector db (embeddings performed by function)
################################################
print("Creating vector database...")
db = Chroma.from_documents(doc_chunks, OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-ada-002"))

