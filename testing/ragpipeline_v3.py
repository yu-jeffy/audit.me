import os
import json
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load vulnerability types and descriptions
vulnerability_info = {}
with open('vulnerabilitytypesdescriptions.jsonl', 'r') as f:
    for line in f:
        vulnerability = json.loads(line)
        vulnerability_info[vulnerability['vulnerabilitytype']] = vulnerability['vulnerabilitydescription']

# Initialize LangChain components
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-1106-preview", max_tokens=5)
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENV"))
embeddings = OpenAIEmbeddings()
pinecone_index = Pinecone.from_existing_index('auditme', embeddings)
retriever = pinecone_index.as_retriever()

# Define the prompt template
template = """
You are an AI Smart Contract auditor agent in a RAG system. 
We have performed a vector search of known smart contract vulnerabilities based on the code in the USER QUESTION.
The results are below:

RELEVANT_VULNERNABILITIES: {context}

With this knowledge, review the following smart contract code in USER QUESTION in detail and very thoroughly.
ONLY indentify vulnerabilities in the USER QUESTION, do not analyze the RELEVANT_VULNERNABILITIES.

Think step by step, carefully. 
Is the following smart contract vulnerable to '{vulnerability_type}' attacks? 
Reply with YES or NO only. Do not be verbose. 
Think carefully but only answer with YES or NO! To help you, find here a definition of a '{vulnerability_type}' attack: {vulnerability_description}

USER QUESTION: {question}
"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(
    template
)

# Create the results directory if it doesn't exist
results_dir = '52results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# Process each entry in the 52samplesourcecode.jsonl
with open('52samplesourcecode.jsonl', 'r') as jsonl_input:
    for contract_id, line in enumerate(jsonl_input, start=1):
        entry = json.loads(line)
        address = entry['address']
        source_code = entry['sourcecode']
        attack_types = entry['attacktype'].split(', ')
        print(f"analyzing contract {line} - {address}...")
        
        # Filename for the contract's results
        result_filename = f"{contract_id} - {address}.jsonl"
        result_filepath = os.path.join(results_dir, result_filename)
        
        # Open the result file for this contract
        with open(result_filepath, 'a') as jsonl_output:
            for i in range(38):  # Run each contract 38 times
                print(f"contract {line} - {address}, run {i+1} of 38...")
                results = []
                # Retrieve relevant documents
                docs = retriever.get_relevant_documents(source_code)
                context = [doc.page_content for doc in docs]
                
                for attack_type in attack_types:
                    vulnerability_description = vulnerability_info.get(attack_type, "Description not found.")
                    
                    # Construct the prompt
                    prompt = QA_CHAIN_PROMPT.format(
                        context = json.dumps(context),
                        question = source_code,
                        vulnerability_type = attack_type,
                        vulnerability_description = vulnerability_description
                    )
                    
                    # Run the prompt through the LLM
                    chain = load_qa_chain(llm, chain_type="stuff", prompt=QA_CHAIN_PROMPT)
                    output = chain({"input_documents": docs, "question": source_code}, return_only_outputs=True)
                    
                    # Append the result to the entry
                    results.append({
                        "address": address,
                        "attacktype": attack_type,
                        "result": output
                    })
                
                # Write the updated entry to the output file
                for result in results:
                    jsonl_output.write(json.dumps(result) + '\n')
                    print(f"contract {line} - {address}, run {i+1} of 38 result: {result}")

print("Completed.")