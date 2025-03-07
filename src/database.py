import argparse
from src.utils.config import config, logger
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
    start = time.time()
    logger.info("Starting graph building process...")
    builder = GraphBuilder(file_path)
    graph = builder.build()
    end = time.time()
    logger.info(
        "Graph built with %d nodes and %d edges in %f seconds.",
        graph.number_of_nodes(),
        graph.number_of_edges(),
        end - start
    )
    return graph

def process_graph(graph) -> None:
    """
    Process the graph by pushing it to Neo4j and creating embeddings.

    Args:
        graph (Graph): The graph object to process.
    """

    client = Neo4jClient(uri=config.get("NEO4J_URI"), user=config.get("NEO4J_USER"), password=config.get("NEO4J_PASSWORD"))
    client.push_graph_to_neo4j(graph, 
                               delete_previous=True)
    
    logger.debug("Graph pushed to Neo4j.")
    
    common_label = "CodeEntity"
    client.add_common_label(
        target_labels=["Class", "Function", "Method"],
        common_label=common_label
    )
    
    client.create_vector_index(
        index_name="code_embedding",
        node_label=common_label
    )

    logger.debug("Vector index created. Creating embeddings...")

    properties = {
        "Method": "code",
        "Function": "code",
        "Class": "docstring"
    }
    
    for label, property_name in properties.items():
        client.create_embeddings(node_label=label, 
                                 openai_api_key=config.get("OPENAI_API_KEY"), 
                                 on_node_property=property_name)
        
        logger.debug(f"Embeddings for {label} created.")
    
    client.close()


def build_process_graph(file_path):
    """
    Orchestrate graph building and processing.

    Args:
        file_path (str): Path to the input root folder for graph building.
    """
    graph = build_graph(file_path)
    try:
        process_graph(graph)
    except Exception as e:
        logger.error(f"An error occurred during graph processing: {e}")


def main() -> None:
    """
    Main function to orchestrate graph building and processing from command-line parsed argument.
    """
    args = parse_arguments()
    graph = build_graph(args.file_path)
    try:
        process_graph(graph)
    except Exception as e:
        logger.error(f"An error occurred during graph processing: {e}")

if __name__ == '__main__':
    main()
