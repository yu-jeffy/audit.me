from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI


load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

