import ast
import os
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# --- LLM/SQL libraries ---
from langchain_experimental.sql import SQLDatabaseChain
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.utilities import SQLDatabase

from sqlalchemy.exc import SQLAlchemyError

# -- Load DB URL from environment variable --
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable must be set.")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY_3")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://127.0.0.1:9011/v1")


# -------------------------------
# Pydantic models
# -------------------------------
class SQLChatInput(BaseModel):
    query: str = Field(
        ...,
        description="Your question or task in natural language (e.g. 'Show me the top 10 customers by sales.')",
    )


class SQLChatOutput(BaseModel):
    sql: str = Field(..., description="SQL that was executed")
    answer: str = Field(..., description="Answer to your query, from the database")
    raw_result: Optional[list] = Field(
        None, description="Raw result rows (list of dict/tuples)"
    )


# -------------------------------
# API Setup
# -------------------------------
app = FastAPI(
    title="Chat with SQL API",
    version="1.0.0",
    description=(
        "Chat in natural language with any SQL database using LLMs. "
        "Query and analyze your data conversationally!"
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# SQL cleaning helper
# -------------------------------
def clean_sql(sql_raw: str) -> str:
    """Strip markdown code fences and SQLQuery/SQLResult noise from LLM output."""
    sql = sql_raw.strip()
    # Remove leading/trailing code fences
    if sql.startswith("```sql"):
        sql = sql[6:]
    elif sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]
    sql = sql.strip()
    # Remove SQLQuery: prefix and SQLResult: suffix
    if "SQLQuery:" in sql:
        sql = sql.split("SQLQuery:", 1)[-1].strip()
    if "SQLResult:" in sql:
        sql = sql.split("SQLResult:", 1)[0].strip()
    return sql.strip("` \n\r\t")


# -------------------------------
# LLM + SQL Chain Setup (singleton)
# -------------------------------
def get_chain():
    # Initiate reflected SQLAlchemy DB
    db = SQLDatabase.from_uri(DATABASE_URL)
    # LLM instance: using OpenAI GPT (or swap for your preferred)
    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=OPENAI_API_KEY or "not-needed",
        model="apo/apple",
        openai_api_base=OPENAI_API_BASE,
    )
    sql_chain = SQLDatabaseChain.from_llm(
        llm, db, verbose=True, return_sql=True, return_intermediate_steps=False
    )
    return sql_chain, llm


sql_chain, llm = get_chain()


# -------------------------------
# Schema endpoint
# -------------------------------
@app.get("/schema", summary="Get database schema overview")
def get_db_schema():
    """
    Returns the tables and columns for the currently connected database.
    """
    try:
        db = sql_chain.database
        return db.get_table_info()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve schema info: {e}"
        )


# -------------------------------
# Chatting endpoint
# -------------------------------
@app.post(
    "/chat_sql", response_model=SQLChatOutput, summary="Chat with your SQL database"
)
def chat_sql(data: SQLChatInput):
    """
    Enter a natural language instruction/question, get answer from your database.
    """
    try:
        # Step 1: ask the chain to generate SQL only
        result = sql_chain({"query": data.query})
        sql_raw = result.get("result", "")
        sql_clean = clean_sql(sql_raw)

        # Step 2: execute the cleaned SQL against the database
        raw_string = sql_chain.database.run(sql_clean)
        try:
            raw_result = ast.literal_eval(raw_string)
        except (ValueError, SyntaxError):
            raw_result = raw_string

        # Step 3: ask the LLM to summarize the result
        answer_prompt = (
            f"User question: {data.query}\n"
            f"SQL executed: {sql_clean}\n"
            f"SQL result: {raw_result}\n"
            "Answer concisely in natural language."
        )
        answer = llm.invoke(answer_prompt).content

        return SQLChatOutput(sql=sql_clean, answer=answer, raw_result=raw_result)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
