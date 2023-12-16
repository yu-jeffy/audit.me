# audit.me
**audit.me** is a project designed to automate the smart contract auditing process. By leveraging a RAG (Retrieval-Augmented Generation) pipeline in LangChain, the platform enhances the reliability and security of Solidity smart contracts. Using LLM-driven analysis, the platform retrieves relevant information from a vector database of known vulnerabilities and identifies issues in the user's submitted code. Potential fixes are also provided.

This project is currently under development. The RAG system is done. Testing is now underway for efficacy.

### Technical Details

The `doc_db.py` file processes a collection of 430 vulnerable Solidity smart contract examples. It extracts meaningful features from these contracts and uses them to create a Pinecone vector store. This vector store serves as a high-dimensional space where each point represents a unique contract, and the proximity between points corresponds to the similarity between the contracts they represent.

On the other hand, `main.py` is the heart of the LangChain RAG (Retrieval-Augmented Generation) pipeline. It leverages `GPT-4-1106` as the agent. The pipeline takes a user's inputted smart contract and performs a vector search in the Pinecone vector store created by `doc_db.py`. This search identifies vulnerabilities that are similar to those in the inputted contract, and provides them as context to `GPT-4-1106` before answering.
