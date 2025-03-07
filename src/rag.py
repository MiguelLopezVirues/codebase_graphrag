from typing import Dict, Any, List, Literal, TypedDict, Optional
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain.chains.router.base import RouterChain, Route
from langchain_core.runnables import Runnable, RunnablePassthrough, RunnableLambda
from langchain_core.runnables.utils import Input, Output
from langchain.chains.conversation.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain_core.messages import AIMessage
from openai import RateLimitError
# -----
from langchain_community.vectorstores import Neo4jVector
from src.utils.config import config, logger


def load_project():
    ...

class RouterChat:
    """
    A router class that directs queries to the appropriate chain based on query content.
    Options include vector search, graph database access, or memory-based conversation.
    """
    
    def __init__(
        self,
        openai_api_key: str,
        neo4j_uri: str,
        neo4j_username: str,
        neo4j_password: str,
        neo4j_database: str,
        neo4j_index_name: str,
        vector_code_property: str,
        router_prompt_template: str,
        cypher_augmentation_query: str,
        vector_qa_system_prompt: str,
        cypher_prompt_template: str, 
        graph_qa_prompt_template: str,
        conversational_qa_system_prompt: str,
        model_name: str = "gpt-4o",
        memory_model_name: str = "gpt-3.5-turbo",
    ):
        """
        Initialize the router with necessary components.
        
        Args:
            documents: List of documents to be indexed in the vector store
            neo4j_uri: URL for Neo4j database connection (optional)
            neo4j_username: Username for Neo4j authentication (optional)
            neo4j_password: Password for Neo4j authentication (optional)
            openai_api_key: API key for OpenAI services (defaults to environment variable)
            model_name: Name of the OpenAI model to use
        """
        # OpenAI API Key
        self.OPENAI_API_KEY = openai_api_key
        
        # Credentials
        self.NEO4J_URI = neo4j_uri
        self.NEO4J_USERNAME = neo4j_username
        self.NEO4J_PASSWORD = neo4j_password
        self.NEO4J_DATABASE = neo4j_database

        # Graph & vector retrieval variables
        self.NEO4J_INDEX_NAME = neo4j_index_name
        self.VECTOR_CODE_PROPERTY = vector_code_property
        self.CYPHER_AUGMENTATION_QUERY = cypher_augmentation_query

        # Prompts
        self.VECTOR_QA_SYSTEM_PROMPT = vector_qa_system_prompt
        self.CYPHER_GENERATION_TEMPLATE = cypher_prompt_template
        self.GRAPH_QA_GENERATION_TEMPLATE = graph_qa_prompt_template
        self.CONVERSATIONAL_QA_SYSTEM_PROMPT = conversational_qa_system_prompt
        
        # Initialize Chat LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=self.OPENAI_API_KEY
        )
        
        # Initialize memory for conversation
        self.memory_llm = ChatOpenAI(
            model=memory_model_name,
            temperature=0,
            api_key=self.OPENAI_API_KEY
        )

        self.memory = ConversationSummaryBufferMemory(
            llm=self.memory_llm,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Set up the router chain
        self.router_chain = self._create_router_chain(router_prompt_template)
        
        # Set up destination chains
        self.routes = self._create_routes()
        
        # Create the multi-route chain
        self.chain = {"topic": self.router_chain, "question": lambda x: x["question"]} | RunnableLambda(self._route)
           
    def _init_vector_store(self) -> None:
        """Initialize the vector store with documents."""
        try:
            logger.info(self.NEO4J_URI)
            self.vector_store = Neo4jVector.from_existing_index(
                OpenAIEmbeddings(),
                url=self.NEO4J_URI,
                username=self.NEO4J_USERNAME,
                password=self.NEO4J_PASSWORD,
                database=self.NEO4J_DATABASE,
                index_name=self.NEO4J_INDEX_NAME,
                text_node_property=self.VECTOR_CODE_PROPERTY,
                retrieval_query=self.CYPHER_AUGMENTATION_QUERY,
            )
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Neo4j vector store: {e}")
            raise
    
    def _init_graph_db(self) -> None:
        """Initialize the Neo4j graph database connection."""
        try:
            self.graph = Neo4jGraph(url=self.NEO4J_URI, 
                                    username=self.NEO4J_USERNAME, 
                                    password=self.NEO4J_PASSWORD, 
                                    database=self.NEO4J_DATABASE)

            CYPHER_GENERATION_PROMPT = PromptTemplate(
                input_variables=["schema", "question","chat_history"], 
                template=self.CYPHER_GENERATION_TEMPLATE
            )

            QA_GENERATION_PROMPT = PromptTemplate(
                input_variables=["question", "context", "chat_history"],
                template=self.GRAPH_QA_GENERATION_TEMPLATE
            )

            self.graph_qa_chain = RunnableLambda(lambda input: {
            "question": input["question"],
            "chat_history": self.memory.chat_memory.messages  
            })| GraphCypherQAChain.from_llm(
                llm = self.llm,
                graph=self.graph,
                verbose=True,
                allow_dangerous_requests=True,
                cypher_prompt=CYPHER_GENERATION_PROMPT, 
                qa_prompt=QA_GENERATION_PROMPT, 
                memory=self.memory,
                validate_cypher = True,
                input_key="question"
            ) | RunnableLambda(lambda output: output["result"])
            logger.info("Neo4j graph initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Neo4j graph: {e}")

    
    def _create_router_chain(self, router_prompt_template: str) -> RouterChain:
        """Create the router chain that determines which destination to use."""
         
        router_prompt = ChatPromptTemplate.from_template(router_prompt_template)
        
        router = (
            router_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        return router
    
    def _create_routes(self) -> List[Route]:
        """Create the destination routes."""

        # Vector chain
        self._init_vector_store()
        self.vector_search_chain = self._create_vector_search_chain()

        # Graph chain
        self._init_graph_db()
        
        # Conversation route
        self.conversation_chain = self._create_conversation_chain()

    def _route(self, info):
        if "vector" in info["topic"].lower():
            return self.vector_search_chain
        elif "graph" in info["topic"].lower():
            return self.graph_qa_chain
        else:
            return self.conversation_chain
    

    def _create_vector_search_chain(self) -> Runnable:
        """Create the vector search chain with structured code context."""
        # Define a template that uses retrieved code context effectively
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.VECTOR_QA_SYSTEM_PROMPT),
            ("human", "{question}"),
            ("system", "Here is relevant code context from the codebase:\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
        ])
        
        # Create the chain
        chain = (
            {"question": RunnablePassthrough(), 
            "context": lambda x: self._get_structured_context(x["question"]),
            "chat_history": lambda _: self.memory.chat_memory.messages}
            | prompt
            | self.llm 
            | StrOutputParser()
        )
        
        return chain

    def _get_structured_context(self, query: str) -> str:
        """Retrieve and format structured code context from Neo4j vector store."""

        docs = self.retriever.invoke(query)
        
        # Format the context with clear section separators
        formatted_contexts = []
        
        for i, doc in enumerate(docs):
            formatted_contexts.append(f"--- CODE ENTITY {i+1} ---\n{doc.page_content}")
            
            # Add metadata if available
            if hasattr(doc, 'metadata') and doc.metadata:
                metadata = doc.metadata
                if metadata:
                    meta_str = "\nMETADATA: " + ", ".join([f"{k}: {v}" for k, v in metadata.items() if k != 'score'])
                    formatted_contexts[-1] += meta_str
        
        return "\n\n" + "\n\n".join(formatted_contexts)
            
    def _create_conversation_chain(self) -> Runnable:
        """Create the conversation chain with memory."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.CONVERSATIONAL_QA_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ])
        
        # Create the chain
        chain = (
            {"question": RunnableLambda(lambda x: x["question"]),
            "chat_history": lambda _: self.memory.chat_memory.messages}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def process(self, question: str) -> str:
        """
        Process a question using the appropriate chain.
        
        Args:
            question: User's question text
            
        Returns:
            Response string from the appropriate chain
        """
        try:
            # Send query to the multi-route chain
            response = self.chain.invoke({"question": question})
            
            # Store messages in memory
            if AIMessage(content=response) not in self.memory.chat_memory.messages:  # Avoid doubled response storage
                self.memory.save_context({"question": question}, {"response": response})
            
            return response
        
        except RateLimitError as e:
            logger.error(f"Token limit error: {e}")
            return f"""The context retrieved to answer this question exceeds the limit of this model. Try narrowing down the context or choosing a bigger model. 
            \n{e}"""

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def close(self) -> None:
        """Close any open connections."""
        if self.graph:
            try:
                self.graph.close()
                logger.info("Neo4j connection closed")
            except Exception as e:
                logger.error(f"Error closing Neo4j connection: {e}")


# Example usage
if __name__ == "__main__":

    # Create the router
    router = RouterChat(
        openai_api_key = config.get("OPENAI_API_KEY"),
        neo4j_uri = config.get("NEO4J_URI",None),
        neo4j_username = config.get("NEO4J_USER", None),
        neo4j_password = config.get("NEO4J_PASSWORD"),
        neo4j_database = config.get("NEO4J_DATABASE",None),
        neo4j_index_name = config.get("VECTOR_INDEX_NAME",None),
        vector_code_property = config.get("VECTOR_SOURCE_PROPERTY_CODE",None),
        router_prompt_template = config.get("ROUTER_PROMPT", None),
        cypher_augmentation_query = config.get("GRAPH_AUGMENTED_SIMILARITY_QUERY",None),
        vector_qa_system_prompt = config.get("VECTOR_QA_SYSTEM_PROMPT", None),
        cypher_prompt_template = config.get("CYPHER_GENERATION_TEMPLATE", None), 
        graph_qa_prompt_template = config.get("GRAPH_QA_GENERATION_TEMPLATE", None),
        conversational_qa_system_prompt = config.get("CONVERSATIONAL_QA_SYSTEM_PROMPT", None),
    )
    
    # Example queries
    queries = [
        """I want the TimeSeriesDifferentiator to be able to implement a pct growth differentiation besides the normal differentiation. Take your time to look at the whole class code to understand it, identify and assess the methods that would need modfication and suggest new methods as well if necessary.
Provide detailed snippets of the neccessary code everywhere it might be needed.""",
        """Can you summarise your last response?"""
    ]
    
    for query in queries:
        logger.debug(router.memory.chat_memory.messages)
        print(f"\nQuery: {query}")
        response = router.process(query)
        print(f"Response: {response}")
    
    # Clean up
    router.close()