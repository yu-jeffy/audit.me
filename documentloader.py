from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter

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
    
    split_doc = text_splitter.split_text(sol_code)

    # print(split_doc)
    sol_docs.extend(split_doc)

print(f"Number of documents after splitting: {len(sol_docs)}")
# for split_doc in sol_docs:
#    print(split_doc)