import streamlit as st
import os
import dotenv

# check if it's linux so it works on Streamlit Cloud
if os.name == 'posix':
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from src.utils.config import config, logger
from streamlit_helpers import unzip_project
from src.database.database import build_graph, process_graph
from src.rag import RouterChat

dotenv.load_dotenv()

MODELS = [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-4"
]


st.set_page_config(
    page_title="Codebase RAG", 
    page_icon="📚", 
    layout="centered", 
    initial_sidebar_state="expanded"
)


# --- Initial setup ---
if "extracted_path" not in st.session_state:
    st.session_state.extracted_path = None

if "knowledge_graph" not in st.session_state:
    st.session_state.knowledge_graph = False

if "chat_model" not in st.session_state:
    logger.debug("Chat model not in session state.")
    st.session_state.chat_model = None
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! How can I assist you today?"}
]
    

# --- Header ---
st.html("""<h2 style="text-align: center;">📚🔍 <i> Codebase pair programmer Chat </i> 🤖💬</h2>""")


# --- Side Bar LLM API Tokens ---
keys = {}
with st.sidebar:

    st.header("Credentials:")  
    DEFAULT_OPENAI_API_KEY = config.get("OPENAI_API_KEY") or ""  # only for development environment, otherwise it should return None
    with st.popover("🔐 OpenAI"):
        st.markdown("_Disclaimer: None of the introduced credentials are stored._")
        keys["OPENAI_API_KEY"] = st.text_input(
            "Introduce your OpenAI API Key (https://platform.openai.com/):", 
            value=DEFAULT_OPENAI_API_KEY, 
            type="password",
            key="openai_api_key",
        )
    
    with st.popover("🔐 Neo4j AuraDB Credentials"):
        st.markdown("_Disclaimer: None of the introduced credentials are stored._")
        DEFAULT_NEO4J_URI = config.get("NEO4J_URI") or ""  # Only for development environment; otherwise, it should return None
        keys["NEO4J_URI"] = st.text_input(
            "Introduce your Neo4j AuraDB database URI (https://neo4j.com/product/auradb/):", 
            value=DEFAULT_NEO4J_URI, 
            type="password",
            key="neo4j_uri",
        )

        DEFAULT_NEO4J_USER = config.get("NEO4J_USER") or ""  # Only for development environment; otherwise, it should return None
        keys["NEO4J_USER"] = st.text_input(
            "Introduce your Neo4j AuraDB username:", 
            value=DEFAULT_NEO4J_USER, 
            key="neo4j_user",
        )

        DEFAULT_NEO4J_PASSWORD = config.get("NEO4J_PASSWORD") or ""  # Only for development environment; otherwise, it should return None
        keys["NEO4J_PASSWORD"] = st.text_input(
            "Introduce your Neo4j AuraDB password:", 
            value=DEFAULT_NEO4J_PASSWORD, 
            type="password",
            key="neo4j_password",
        )

        DEFAULT_NEO4J_DATABASE = config.get("NEO4J_DATABASE") or ""  # Only for development environment; otherwise, it should return None
        keys["NEO4J_DATABASE"] = st.text_input(
            "Introduce your Neo4j AuraDB database name:", 
            value=DEFAULT_NEO4J_DATABASE, 
            type="password",
            key="neo4j_database",
        )



# --- Main Content ---
missing_keys = {key: value == "" or value is None for key, value in keys.items()}

if any(missing_keys.values()):
    st.warning("\n\n".join([f"⬅️ Please introduce {key_name} to continue..." for key_name, key_value in missing_keys.items() if key_value]))


else:
    # Sidebar
    with st.sidebar:
        # --- Project file upload ---
        st.divider()

        st.header("Codebase RAG Sources")

        # Choose between Neo4j connection and file upload
        use_neo4j = st.toggle(
            label="Use Neo4j pre-existing codebase Knowledge Graph",
            key="neo4j_toggle",
            value=False
        )

        if use_neo4j:
            st.info("Using Neo4j credentials to connect to pre-existing knowledge graph.")

        else:
            st.markdown("If you haven't already, upload your codebase as a ZIP file:")
            
            uploaded_file = st.file_uploader(
                "📄 Upload a ZIP or RAR file of your project's code",
                type=["zip", "rar"],
                accept_multiple_files=False,
                key="codebase_project"
            )

            if uploaded_file:
                unzip_project()

                # Create knowledge graph from the zip file with progress spinner
                processing_placeholder = st.empty()

                if st.session_state.extracted_path and not st.session_state.knowledge_graph:
                    with processing_placeholder.container():
                        with st.spinner('Building Knowledge Graph, pushing to Neo4j and creating embeddings from your code... This may take a few minutes.'):
                            try:
                                logger.debug("Building knowledge_graph.")
                                graph = build_graph(st.session_state.extracted_path)
                                st.success("Knowledge Graph successfully built. Pushing to Neo4j and creating embeddings...")
                                process_graph(graph=graph)
                                st.session_state.knowledge_graph = True

                                st.success("✅ Knowledge Graph successfully built and uploaded to Neo4j!")
                            except Exception as e:
                                logger.error(f"Error building knowledge_graph: {e}")
                                st.warning(f"⚠️ Error building Knowledge Graph.")

        st.divider()

        # --- LLM Model Instantiation ---
        st.header("LLM model selection:")   
        st.selectbox(
            "🤖 Select a Model", 
            options=MODELS,
            key="model",
        )
        model_choice = st.session_state.model.split("/")[0]

        # Instantiate the chat model
        if not st.session_state.chat_model and st.session_state.knowledge_graph:
            logger.debug("Instantiated new chat model")
            st.session_state.chat_model = RouterChat(
            openai_api_key = keys.get("OPENAI_API_KEY"),
            neo4j_uri = keys.get("NEO4J_URI"),
            neo4j_username = keys.get("NEO4J_USER"),
            neo4j_password = keys.get("NEO4J_PASSWORD"),
            neo4j_database = keys.get("NEO4J_DATABASE"),
            neo4j_index_name = config.get("VECTOR_INDEX_NAME",None),
            vector_code_property = config.get("VECTOR_SOURCE_PROPERTY_CODE",None),
            router_prompt_template = config.get("ROUTER_PROMPT", None),
            cypher_augmentation_query = config.get("GRAPH_AUGMENTED_SIMILARITY_QUERY",None),
            vector_qa_system_prompt = config.get("VECTOR_QA_SYSTEM_PROMPT", None),
            cypher_prompt_template = config.get("CYPHER_GENERATION_TEMPLATE", None), 
            graph_qa_prompt_template = config.get("GRAPH_QA_GENERATION_TEMPLATE", None),
            conversational_qa_system_prompt = config.get("CONVERSATIONAL_QA_SYSTEM_PROMPT", None),
            model_name=model_choice
        )


        st.divider()
        st.header("About the Project")
        
        # Profile Image
        st.image("assets/miguel_profile.jpg", width=180, use_container_width="auto")

        # Info
        st.subheader("Created by Miguel López")
        st.write("Feel free to connect with me on LinkedIn or check out the project repo:")
        st.markdown("""
        - [💼 LinkedIn](https://www.linkedin.com/in/miguellopezvirues/)
        - [📂 GitHub Repo](https://github.com/MiguelLopezVirues/codebase_knowledge_graph)
        """)



    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your message"):
        if st.session_state.chat_model:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()

                assistant_response = st.session_state.chat_model.process(prompt)

                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                st.markdown(assistant_response)
            
            logger.debug(st.session_state.chat_model.memory.chat_memory.messages)
        else:
            st.warning("Please introduce your codebase project as a RAG source.")
    
    

    


    