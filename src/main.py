import argparse
from src.utils.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, logger
from src.graph.graph_builder import GraphBuilder
from src.neo4j_integration.neo4j_client import push_graph_to_neo4j

def main(file_path):
    logger.info("Starting graph building process...")
    builder = GraphBuilder(file_path)
    graph = builder.build()
    print(f"Graph built with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")

    push_graph_to_neo4j(graph, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description="Graph building process")
    arg_parser.add_argument("--file_path",required=True, help="Path to the input root folder for graph building")
    args = arg_parser.parse_args()

    main(file_path=args.file_path)
