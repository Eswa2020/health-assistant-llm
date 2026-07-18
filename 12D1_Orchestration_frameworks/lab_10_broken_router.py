# lab_10_broken_router.py  (debugging challenge – fixed)
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Locate the project root (two folders up from this script) and load .env
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")

# Now the key is available
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=1.5)   # deterministic
prompt = ChatPromptTemplate.from_template(
    "Classify as CLINICAL or BILLING: {msg}\nAnswer:"
)
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"msg": "My chest hurts badly"}))