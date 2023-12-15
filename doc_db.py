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

# other imports
import os
from dotenv import load_dotenv

load_dotenv()

loader = DirectoryLoader('contracts', glob="**/*.sol", show_progress=True) #silent_errors=True

docs = loader.load()

print(f"Number of documents loaded: {len(docs)}")

text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=128, chunk_overlap=0
)


sol_docs = []
for doc_index, doc in enumerate(docs):
    print(f"Processing document {doc_index + 1}/{len(docs)}")
    sol_code = doc.page_content
    
    split_docs = text_splitter.split_text(sol_code)

    # print(split_doc)
    for chunk in split_docs:
        sol_docs.append(Document(page_content=chunk, metadata={}))

print(f"Number of documents after splitting: {len(sol_docs)}")
# for split_doc in sol_docs:
#    print(split_doc)

# embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-ada-002")

# embeddings = embeddings_model.embed_documents(sol_docs)
# print(len(embeddings), len(embeddings[0]))

db = Chroma.from_documents(sol_docs, OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"), model="text-embedding-ada-002"))

# query = "Withdrawal function"
# docs = db.similarity_search(query)
# print(docs[0].page_content)