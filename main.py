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
# llm = ChatOpenAI(temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))
llm = ChatOpenAI(
    temperature=0.3, model_name="gpt-4-1106-preview"
)

################################################
#  vectore store
################################################
# initialize pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),  # find at app.pinecone.io
    environment=os.getenv("PINECONE_ENV"),  # next to api key in console
)

embeddings = OpenAIEmbeddings()

# pinecone_index = pinecone.Index('auditme')
pinecone_index = Pinecone.from_existing_index('auditme', embeddings)

retriever = pinecone_index.as_retriever()

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
template = """You are a Smart Contract auditor agent in a RAG system. 
We have performed a vector search of known smart contract vulnerabilities based on the code in the USER QUESTION.
The results are below:

RELEVANT_VULNERNABILITY: {context}

With this knowledge, answer the USER QUESTION, identifying ALL vulnerabilities line by line, and a possible fixes. Provide code excerpts where possible.
ONLY indentify vulnerabilities in the USER QUESTION, do not analyze the RELEVANT_VULNERNABILITY.

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
    "context": itemgetter("user_question") | retriever | _combine_documents,
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
            import " @openzeppelin / contracts - ethereum - package /
contracts / token / ERC20 / ERC20 .sol";
import " @openzeppelin / contracts - ethereum - package /
contracts / token / ERC20 / IERC20 .sol";
import " @openzeppelin / contracts - ethereum - package /
contracts / token / ERC20 / extensions / IERC20Metadata . sol "
;
import " @openzeppelin / contracts - ethereum - package /
contracts / utils / Context .sol";
import " @openzeppelin / contracts - ethereum - package /
contracts / access / Ownable .sol";
pragma solidity ^0.8.0;
contract AirdropFaucet is Ownable {
uint256 public dripAmount ;
mapping ( address = > bool ) public previousRequestors ;
address public tokenAddress ;
uint256 public lotteryReward ;
event TokensRequested ( address requestor ) ;
event LotteryPlayed ( address player , bool win ) ;
struct Proposal {
string description ;
uint256 yesVotes ;
uint256 noVotes ;
}
mapping ( uint256 = > Proposal ) public proposals ;
mapping ( address = > uint256 ) public depositedBalances ;
uint256 public proposalCount ;
constructor ( address _tokenAddress ) {
tokenAddress = _tokenAddress ;
uint8 decimals = ERC20 ( tokenAddress ) . decimals () ;
dripAmount = 1000 * 10 ** decimals ;
lotteryReward = 5000 * 10 ** decimals ;
}
function requestTokens ( address requestor ) external {
require (
previousRequestors [ requestor ] == true ,
" Address has already requested tokens "
) ;
// Vulnerability : Absense of code logic or sanity
check
ERC20 faucetToken = ERC20 ( tokenAddress ) ;
require (
faucetToken . balanceOf ( address ( this ) ) >
dripAmount ,
" Insufficient funds in faucet "
) ;
// Vulnerability : Reentrancy Vulnerability
// Vulnerability : Unhandled or mishandled
exception
// Transfer token to requestor
( bool success ,) = requestor . call { value :
dripAmount }("") ;
previousRequestors [ requestor ] = true ;
emit TokensRequested ( requestor ) ;
}
// Vulnerability : Transaction / Strategy replay
attacks // Note : This is Included in the 2
Vulnerabilities Set Mutation Test
function transferWithSignature (
address from ,
address to ,
uint256 amount ,
uint256 expiration ,
uint8 v ,
bytes32 r ,
bytes32 s
) external {
require ( block . timestamp < expiration , " Signature
expired ") ;
bytes32 messageHash = keccak256 ( abi . encodePacked (
from , to , amount , expiration ) ) ;
bytes32 prefixedHash = keccak256 ( abi . encodePacked
("\ x19Ethereum Signed Message :\ n32",
messageHash ) ) ;
address signer = ecrecover ( prefixedHash , v , r , s )
;
require ( signer == from , " Invalid signature ") ;
ERC20 ( tokenAddress ) . transferFrom ( from , to , amount
) ;
}
// Vulnerability : Insecure Randomness
// Vulnerability : Front - running attacks
function playLottery ( uint256 guess ) external {
require ( guess >= 1 && guess <= 10 , " Guess must be
between 1 and 10") ;
uint256 randomNumber = uint256 ( blockhash ( block .
number - 1) ) % 10 + 1;
if ( randomNumber == guess ) {
ERC20 ( tokenAddress ) . transfer ( msg . sender ,
lotteryReward ) ;
emit LotteryPlayed ( msg . sender , true ) ;
} else {
emit LotteryPlayed ( msg . sender , false ) ;
}
}
// Vulnerability : Inconsistent access control
// Note : This is Included in the 2 Vulnerabilities
Set Mutation Test
function setLotteryReward ( uint256 _lotteryReward )
external {
lotteryReward = _lotteryReward ;
}
function withdrawTokens () external onlyOwner {
ERC20 faucetToken = ERC20 ( tokenAddress ) ;
uint256 amount = faucetToken . balanceOf ( address (
this ) ) ;
faucetToken . transfer ( msg . sender , amount ) ;
}
function setDripAmount ( uint256 _dripAmount ) external
onlyOwner {
dripAmount = _dripAmount ;
}
function createProposal ( string calldata description )
external {
proposals [ proposalCount ] = Proposal ( description ,
0 , 0) ;
proposalCount ++;
}
// Vulnerability : Governance attacks ( flash loan , etc
.)
function vote ( uint256 proposalId , bool support )
external {
ERC20 token = ERC20 ( tokenAddress ) ;
uint256 voterBalance = token . balanceOf ( msg . sender
) ;
require ( proposalId < proposalCount , " Invalid
proposal ID") ;
if ( support ) {
proposals [ proposalId ]. yesVotes +=
voterBalance ;
} else {
proposals [ proposalId ]. noVotes += voterBalance
;
}
}
// Vulnerability : Other smart contract
vulnerabilities ( Developer oversight )
function depositTokens ( uint256 amount ) external {
ERC20 token = ERC20 ( tokenAddress ) ;
// Transfer the tokens from the user to the
contract
token . transferFrom ( msg . sender , address ( this ) ,
amount ) ;
// Update the internal accounting of the
deposited tokens
// depositedBalances [msg. sender ] += amount ;
}
function setTokenAddress ( address _tokenAddress )
external onlyOwner {
tokenAddress = _tokenAddress ;
}
// Vulnerability : Unbounded operation , including gas
limit and call - stack depth
function batchTransfer ( address [] calldata recipients ,
uint256 [] calldata amounts ) external {
require ( recipients . length == amounts . length , "
Recipients and amounts length mismatch ") ;
ERC20 token = ERC20 ( tokenAddress ) ;
for ( uint256 i = 0; i < recipients . length ; i ++) {
// Transfer tokens without any bounds or gas
limit checks
token . transfer ( recipients [ i ] , amounts [ i ]) ;
}
}
}
            """,
        "chat_history": [],
    }
).content)