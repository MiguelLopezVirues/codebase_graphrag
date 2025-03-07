# Codebase GraphRAG
[README Work In Progress]

## The project
### Knowledge graph configuration
The codebase is modeled as a knowledge graph. Inside the know Class, function and method definitions and calls are modeled as nodes in the Knowledge Graph.
- Edges: CALL, INHERITS_FROM, NESTED_IN
- Explicit import links from within the project are ignored, modeled as a direct relationship from CALL context to -> DEFINITION context

### Notes
- The parsing of code ignores files inside any folder called tests.

## Instructions
### Installation
This project uses Astral's UV to manage dependencies. Using UV, the both sstatic and dynamic dependencies are robustly handled by the uv.lock file.

To install the project dependencies simply execute from the command-line:
```bash
uv sync
```
UV will automatically create a virtual environment with the necessary dependencies.

### Configuration
- If desired, modify `src/utils/config/config.py` to modify the fields and properties for Vector Index and Code Embedding in Neo4j.
- The prompts for each chain can be modified for finer prompt engineering in the file `src/utils/config/prompts.yaml`

### Usage
- Run streamlit with uv from the root folder as 
    ```bash
    uv run streamlit run streamlit.py
    ```

## Packages



### Next steps
- Create unit tests
- Refactor project to divide in 3 to separately deployments; 
    1. Code database creation
    2. RAG LLMs 
    3. Frontend app 
- Refactor graph build and upload to Neo4j processes to asynchronous and parallel to make the RAG knowledge base creation faster. 
- Adapt for private LLM endpoint integration
- Add option to plug in official code documentation