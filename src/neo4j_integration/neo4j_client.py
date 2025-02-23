from neo4j import GraphDatabase
from src.utils.config import logger

def push_graph_to_neo4j(G, uri, user, password):
    """
    Push the NetworkX graph G to a Neo4j database.
    """
    print(password)
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        logger.info("Clearing existing data in Neo4j...")
        session.run("MATCH (n) DETACH DELETE n")
        for node_id, data in G.nodes(data=True):
            label = (
                "Class" if data.get('type') == 'class'
                else "Method" if data.get('type') == 'method'
                else "Function"
            )
            session.run(
                f"CREATE (n:{label} {{id: $id, name: $name, file: $file, line: $line, code: $code}})",
                id=node_id,
                name=data.get('name'),
                file=data.get('file'),
                line=data.get('line'),
                code=data.get('code')
            )
        for source, target, data in G.edges(data=True):
            rel_type = data.get('relation', 'call').upper()
            session.run(
                f"MATCH (a {{id: $source}}), (b {{id: $target}}) CREATE (a)-[r:{rel_type}]->(b)",
                source=source,
                target=target
            )
    driver.close()
    logger.info("Graph successfully pushed to Neo4j.")
