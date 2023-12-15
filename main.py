from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import format_document
from langchain_core.messages import AIMessage, HumanMessage, get_buffer_string
from langchain_core.runnables import RunnableParallel
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
from doc_db import db

load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Define a template string for the prompt that will be used to rephrase a question.
_template = """Given the following conversation and a follow up question, 
rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# Define another template string for a prompt that will provide context and ask a question.
template = """Answer the question based only on the following context:
{context}

Question: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

# Use a default prompt template for formatting individual documents when needed.
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

# Create a retriever from the Chroma database, to be used for retrieving relevant documents.
retriever = db.as_retriever()

# Define a function that combines multiple documents into a single string.
def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

# Set up a parallel runnable to process the standalone question rephrasing task.
_inputs = RunnableParallel(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: get_buffer_string(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | ChatOpenAI(temperature=0.3)
    | StrOutputParser(),
)

# Define the context using the standalone question from the previous processing step,
# retrieve documents based on that context/question, and combine them.
_context = {
    "context": itemgetter("standalone_question") | retriever | _combine_documents,
    "question": lambda x: x["standalone_question"],
}

# Combine the inputs and context to form the conversational QA chain.
# This will use the rephrased question to retrieve documents, provide context, and generate an answer.
conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | ChatOpenAI()

# Invoke the conversational QA chain with an initial question and an empty chat history.
# This will process the question, search for relevant context, and attempt to provide an answer.
print(conversational_qa_chain.invoke(
    {
        "question": "Write a withdrawal function in Solidity",
        "chat_history": [],
    }
))