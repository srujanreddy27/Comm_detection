"""
Module 2: Graph Construction
Loads edge and user data to construct a directed social network graph.
"""

import pandas as pd
import networkx as nx
from pathlib import Path


class GraphConstructor:
    """Constructs and manages social network graphs."""
    
    def __init__(self, edges_path: str, users_path: str):
        """
        Initialize the GraphConstructor.
        
        Args:
            edges_path: Path to edges CSV file
            users_path: Path to users CSV file
        """
        self.edges_path = Path(edges_path)
        self.users_path = Path(users_path)
        self.graph = None
        self.user_df = None
        
    def load_data(self):
        """Load edges and users data from CSV files."""
        print("Loading data...")
        
        # Load edges (no header, two columns: follower, following)
        print("Reading edges.csv...")
        edges_df = pd.read_csv(self.edges_path, header=None, names=['source', 'target'])
        print(f"Loaded {len(edges_df):,} edges")
        
        # Load nodes (no header, single column of node IDs)
        print("Reading nodes.csv...")
        self.user_df = pd.read_csv(self.users_path, header=None, names=['id'])
        print(f"Loaded {len(self.user_df):,} nodes")
        
        return edges_df, self.user_df
    
    def build_graph(self, max_edges=None):
        """Construct the directed graph from edge data.
        
        Args:
            max_edges: Maximum number of edges to load (None = all edges)
                      Use smaller value for testing or limited RAM
        """
        print("\nConstructing graph...")
        
        edges_df, users_df = self.load_data()
        
        # Optionally limit edges for testing or RAM constraints
        if max_edges and len(edges_df) > max_edges:
            print(f"  Note: Limiting to first {max_edges:,} edges (out of {len(edges_df):,})")
            edges_df = edges_df.head(max_edges)
        
        # Create directed graph
        print("Creating directed graph...")
        self.graph = nx.DiGraph()
        
        # Add edges from the DataFrame efficiently (avoid list conversion)
        print(f"Adding {len(edges_df):,} edges to graph...")
        # Use itertuples for memory efficiency - no intermediate list created
        self.graph.add_edges_from(edges_df.itertuples(index=False, name=None))
        
        # Calculate follower/following counts from graph structure
        print("Calculating follower and following counts...")
        for node in self.graph.nodes():
            self.graph.nodes[node]['followers_count'] = self.graph.in_degree(node)
            self.graph.nodes[node]['following_count'] = self.graph.out_degree(node)
        
        print(f"Graph constructed with {self.graph.number_of_nodes():,} nodes and {self.graph.number_of_edges():,} edges")
        
        return self.graph
    
    def get_graph_statistics(self):
        """Return basic statistics about the graph."""
        if self.graph is None:
            raise ValueError("Graph not built yet. Call build_graph() first.")
        
        stats = {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_directed': self.graph.is_directed(),
        }
        
        # Check if weakly connected (for directed graphs)
        if self.graph.is_directed():
            stats['weakly_connected_components'] = nx.number_weakly_connected_components(self.graph)
            stats['strongly_connected_components'] = nx.number_strongly_connected_components(self.graph)
        
        return stats
    
    def save_graph(self, output_path: str):
        """Save the graph to a file."""
        if self.graph is None:
            raise ValueError("Graph not built yet. Call build_graph() first.")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        nx.write_graphml(self.graph, output_path)
        print(f"Graph saved to {output_path}")


def main():
    """Example usage of GraphConstructor."""
    # Paths
    edges_path = "data/edges.csv"
    users_path = "data/nodes.csv"  # Updated to nodes.csv
    output_path = "output/network_graph.graphml"
    
    # Build graph
    constructor = GraphConstructor(edges_path, users_path)
    graph = constructor.build_graph()
    
    # Print statistics
    stats = constructor.get_graph_statistics()
    print("\n=== Graph Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Save graph
    constructor.save_graph(output_path)


if __name__ == "__main__":
    main()
