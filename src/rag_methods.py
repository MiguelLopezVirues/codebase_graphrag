from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
import os
from langchain_openai import ChatOpenAI
import os
from langchain.globals import set_verbose
from dotenv import load_dotenv
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()
set_verbose(True)

# Neo4j connection settings
NEO4J_URI = os.getenv('NEO4J_URI_AURADB', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER_AURADB', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASS_AURADB', 'your_password')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from neo4j import GraphDatabase

# Connect to Neo4j AuraDB
URI = NEO4J_URI
AUTH = ("neo4j", NEO4J_PASSWORD)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()


kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USER, password=NEO4J_PASSWORD, database=NEO4J_USER
)



CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Always return the question too.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
Examples: Here are a few examples of generated Cypher statements for particular questions:

# What are the nodes directly related to example_node?
MATCH (node)-[]-(other_nodes)
WHERE node.name = 'example.node'
RETURN other_nodes

# What are the function or method nodes that have a relationship towards example_node?
MATCH (node)<-[]-(other_nodes:Function|Method)
WHERE node.name = 'example.node'
RETURN other_nodes

# What are the function or method nodes that call example_node?
MATCH (node)<-[:CALL]-(other_nodes:Function|Method)
WHERE node.name = 'example.node'
RETURN other_nodes

# What is the file that stores example?
MATCH (node)
WHERE node.name = 'example'
RETURN node.file

# Inside what function or method is example_function defined?
MATCH (node)<-[r:NESTED_IN]-(other_node)
WHERE node.name = 'example_function'
RETURN other_node

The question is:
{question}

Some questions might not ask you to retrieve anything from the database. In those cases, use the chat history to retrieve the relevant information.
Chat History:
{chat_history}"""

QA_GENERATION_TEMPLATE = """You are an assistant specialized in retrieving and interpreting code snippets from a graph database.
Based on the user's question and the provided context, identify relevant pieces of code within the node properties and present them clearly.
Some questions might ask about previous messages. Therefore, always use the chat_history to inform your answers.

Chat_history:
{chat_history}

User's Question:
{question}

Context from Database:
{context}"""


CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question","chat_history"], 
    template=CYPHER_GENERATION_TEMPLATE
)

QA_GENERATION_PROMPT = PromptTemplate(
    input_variables=["question", "context", "chat_history"],
    template=QA_GENERATION_TEMPLATE
)

from langchain.memory.buffer import ConversationBufferMemory  # using buffer memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)


cypher_chain = GraphCypherQAChain.from_llm(
    llm = llm,
    graph=kg,
    verbose=True,
    allow_dangerous_requests=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT, 
    qa_prompt=QA_GENERATION_PROMPT, 
    memory=memory,
    input_key="question"
)


import streamlit as st

def graph_response(question):

    return cypher_chain.run(question)