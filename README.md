# audit.me
**audit.me** is a project designed to automate the smart contract auditing process. By leveraging a RAG (Retrieval-Augmented Generation) pipeline in LangChain, the platform enhances the reliability and security of Solidity smart contracts. Using LLM-driven analysis, the platform retrieves relevant information from a vector database of known vulnerabilities and identifies issues in the user's submitted code. There is a prompt option where potential fixes can also be provided.

### Abstract
The rapid growth of Decentralized Finance (DeFi) has been accompanied by substantial financial losses due to smart contract vulnerabilities, underscoring the critical need for effective security auditing. With attacks becoming more frequent, the necessity and demand for auditing services has escalated. This especially creates a financial burden for independent developers and small businesses, who often have limited available funding for these services. Our study builds upon existing frameworks by integrating Retrieval-Augmented Generation (RAG) with large language models (LLMs), specifically employing GPT-4-1106 for its 128k token context window. We construct a vector store of 830 known vulnerable contracts, leveraging Pinecone for vector storage, OpenAI's text-embedding-ada-002 for embeddings, and LangChain to construct the RAG-LLM pipeline. Prompts were designed to provide a binary answer for vulnerability detection. We first test 52 smart contracts 40 times each against a provided vulnerability type, verifying the replicability and consistency of the RAG-LLM. Encouraging results were observed, with a 62.7% success rate in guided detection of vulnerabilities. Second, we challenge the model under a "blind" audit setup, without the vulnerability type provided in the prompt, wherein 220 contracts undergo 40 tests each. This setup evaluates the general vulnerability detection capabilities without hinted context assistance. While the results are promising, we still emphasize the need for human auditing at this time. We provide this study as a proof of concept for a cost-effective smart contract auditing process, moving towards democratic access to security.

### Experiment Design

A comparative study was conducted using similar methodology from [this study](https://arxiv.org/abs/2306.12338). The 52 smart contracts in their testing set will be run against the RAG system with the same GPT-4 parameters, and results will be compared.

Further testing was conducted against the full dataset from this [Systemization of Knowledge paper](https://arxiv.org/abs/2208.13035), which was the original dataset the 52 examples were sampled from.

### Status

The RAG system is complete. Testing has been completed.

Phase One returned an overall efficacy of 62.7 across 2080 queries. Many smart contracts scored a complete 40/40 for detection, while others showed mixed results. A few vulnerabilities were 0/40. We believe these weaknesses can be mitigated through enhancement of the dataset in the vectorstore.

Phase Two testing has been completed. The result analysis is currently in progress.

### Technical Details

The `doc_db.py` file processes a collection of 430 vulnerable Solidity smart contract examples. It extracts meaningful features from these contracts and uses them to create a Pinecone vector store. This vector store serves as a high-dimensional space where each point represents a unique contract, and the proximity between points corresponds to the similarity between the contracts they represent.

On the other hand, `main.py` is the heart of the LangChain RAG (Retrieval-Augmented Generation) pipeline. It leverages `GPT-4-1106` as the agent. The pipeline takes a user's inputted smart contract and performs a vector search in the Pinecone vector store created by `doc_db.py`. This search identifies vulnerabilities that are similar to those in the inputted contract, and provides them as context to `GPT-4-1106` before answering.

A customized version of `main.py` was created for the purpose of testing for our study. This version can be found in `testing/ragllm-pipeline`.