from neo4j import GraphDatabase
from src.utils.config import logger


class Neo4jClient:

    def __init__(self, uri:str, user:str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = self._database_connect()

    def _database_connect(self)-> object:
        try:
            driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            with driver.session() as session:
                session.run("RETURN 1")

        except Exception as e:
            logger.error(f"There was an error connecting to Neo4j: {e}. Make sure the database instance is running.")

        return driver
    
    def close(self):
        if self.driver:
            self.driver.close()
            logger.debug("Driver closed successfully.")


    def push_graph_to_neo4j(self, G: object, delete_previous: bool = False) -> None:
        """
        Push the NetworkX graph G to a Neo4j database.
        """
        with self.driver.session() as session:
            logger.info("Clearing existing data in Neo4j...")
            if delete_previous:
                session.run("MATCH (n) DETACH DELETE n")
            for node_id, data in G.nodes(data=True):
                label = (
                    "Class" if data.get('type') == 'class'
                    else "Method" if data.get('type') == 'method'
                    else "Function"
                )

                session.run(
                    f"CREATE (n:{label} {{id: $id, name: $name, file: $file, line: $line, code: $code, docstring: $docstring}})",
                    id=node_id,
                    name=data.get('name'),
                    file=data.get('file'),
                    line=data.get('line'),
                    code=data.get('code'),
                    docstring=data.get('docstring')
                )

            for source, target, data in G.edges(data=True):
                rel_type = data.get('relation', 'call').upper()
                session.run(
                    f"MATCH (a {{id: $source}}), (b {{id: $target}}) CREATE (a)-[r:{rel_type}]->(b)",
                    source=source,
                    target=target
                )

        logger.info("Graph successfully pushed to Neo4j.")
        


    def add_common_label(self,target_labels, common_label):
        """
        Adds a common label to nodes that have any of the specified target labels.

        :param driver: Neo4j driver instance.
        :param target_labels: List of target labels to match.
        :param common_label: The common label to add to matching nodes.
        """
        # Construct the Cypher query
        query = f"""
        WITH $target_labels AS targetLabels
        MATCH (n)
        WHERE ANY(label IN labels(n) WHERE label IN targetLabels)
        SET n:{common_label}
        """
        with self.driver.session() as session:
            session.run(query, 
                        target_labels=target_labels)


    def create_vector_index(self,  
                            index_name:str, 
                            node_label: str,
                            on_node_property: str = "code_embedding", 
                            embedding_dimensions: int= 1536, 
                            similarity_function: str = "cosine") -> None:

        query = f"""
            CREATE VECTOR INDEX `{index_name}` IF NOT EXISTS 
            FOR (node:{node_label}) ON (node.{on_node_property}) 
            OPTIONS {{ indexConfig: {{
                `vector.dimensions`: {embedding_dimensions},
                `vector.similarity_function`: '{similarity_function}'    
            }} }}
        """
        with self.driver.session() as session:
            session.run(query)

    def create_embeddings(self, 
                          node_label: str,
                          openai_api_key: str,
                          on_node_property: str = "code", 
                          embedding_property: str = "code_embedding",
                          endpoint: str = "https://api.openai.com/v1/embeddings",
                          model: str = None
                          ):
        if model:
            endpoint += f"?model={model}"

        query = f"""
            MATCH (node:{node_label}) WHERE node.{on_node_property} IS NOT NULL AND node.{on_node_property} <> ""
            WITH node, genai.vector.encode(
                node.{on_node_property}, 
                "OpenAI", 
                {{
                token: "{openai_api_key}",
                endpoint: "{endpoint}"
            }}) AS vector
            CALL db.create.setNodeVectorProperty(node, "{embedding_property}", vector)"""

        with self.driver.session() as session:
            session.run(query)