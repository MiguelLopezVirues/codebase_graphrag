# Codebase GraphRAG
### Current state
- Only Class, function and method definitions and calls are modeled as nodes
- Calls and definitions are modeled as edges
- Explicit import links from within the project are ignored, modeled as a direct relationship from CALL context to -> DEFINITION context


### To-Do
- Connect LLM, with possibility to either add OPENAI_API_KEY or connect deployed model endpoint.
- Add text2Cypher QA chain
- Add docstrings and semantic relationships with LangGraph or Neo4j GraphRag Pipelines
- Create embeddings from code for semantic searches
- Add advanced augmentation techniques