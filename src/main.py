import argparse
from src.utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, OPENAI_API_KEY, logger
from src.graph.graph_builder import GraphBuilder
from src.neo4j_integration.neo4j_client import Neo4jClient
import time

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Graph building process")
    parser.add_argument(
        "--file_path",
        required=True,
        help="Path to the input root folder for graph building"
    )
    return parser.parse_args()

def build_graph(file_path: str) -> object:
    """
    Build the graph from the provided file path.

    Args:
        file_path (str): Path to the input root folder for graph building.

    Returns:
        Graph: The constructed graph object.
    """
    logger.info("Starting graph building process...")
    builder = GraphBuilder(file_path)
    graph = builder.build()
    logger.info(
        "Graph built with %d nodes and %d edges.",
        graph.number_of_nodes(),
        graph.number_of_edges()
    )
    return graph

def process_graph(graph) -> None:
    """
    Process the graph by pushing it to Neo4j and creating embeddings.

    Args:
        graph (Graph): The graph object to process.
    """

    client = Neo4jClient(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)
    client.push_graph_to_neo4j(graph, 
                               delete_previous=True)
    
    common_label = "CodeEntity"
    client.add_common_label(
        target_labels=["Class", "Function", "Method"],
        common_label=common_label
    )
    
    client.create_vector_index(
        index_name="code_embedding",
        node_label=common_label
    )
    
    for label in ["Method", "Function", "Class"]:
        property_name = "docstring" if label == "Class" else "code"
        client.create_embeddings(node_label=label, 
                                 openai_api_key=OPENAI_API_KEY, 
                                 on_node_property=property_name)
    
    client.close()

def main() -> None:
    """
    Main function to orchestrate graph building and processing.
    """
    args = parse_arguments()
    graph = build_graph(args.file_path)
    try:
        process_graph(graph)
    except Exception as e:
        logger.error(f"An error occurred during graph processing: {e}")

if __name__ == '__main__':
    main()
