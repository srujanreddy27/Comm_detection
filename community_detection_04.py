"""
Module 4: Community Detection
Identifies communities using Louvain and Label Propagation algorithms.
"""

import networkx as nx
import igraph as ig
from collections import Counter
import community.community_louvain as community_louvain


class CommunityDetector:
    """Detects and analyzes communities in social networks."""
    
    def __init__(self, graph: nx.Graph):
        """
        Initialize CommunityDetector.
        
        Args:
            graph: NetworkX graph object
        """
        self.graph = graph
        self.communities = {}
        
    def louvain_detection(self):
        """
        Detect communities using the Louvain algorithm.
        Returns a dictionary mapping node to community ID.
        """
        print("Running Louvain community detection...")
        
        # Convert to undirected for community detection
        if self.graph.is_directed():
            undirected_graph = self.graph.to_undirected()
        else:
            undirected_graph = self.graph
        
        # Apply Louvain algorithm
        partition = community_louvain.best_partition(undirected_graph)
        
        self.communities['louvain'] = partition
        
        num_communities = len(set(partition.values()))
        print(f"✓ Louvain detected {num_communities} communities")
        
        return partition
    
    def label_propagation_detection(self):
        """
        Detect communities using Label Propagation algorithm.
        Returns a dictionary mapping node to community ID.
        """
        print("Running Label Propagation community detection...")
        
        # Convert to undirected for community detection
        if self.graph.is_directed():
            undirected_graph = self.graph.to_undirected()
        else:
            undirected_graph = self.graph
        
        # Apply Label Propagation
        communities_generator = nx.algorithms.community.label_propagation_communities(undirected_graph)
        communities_list = list(communities_generator)
        
        # Convert to node -> community_id mapping
        partition = {}
        for idx, community_set in enumerate(communities_list):
            for node in community_set:
                partition[node] = idx
        
        self.communities['label_propagation'] = partition
        
        num_communities = len(communities_list)
        print(f"✓ Label Propagation detected {num_communities} communities")
        
        return partition
    
    def igraph_louvain_detection(self):
        """
        Detect communities using igraph's Louvain implementation.
        More efficient for large graphs.
        """
        print("Running igraph Louvain community detection...")
        
        try:
            # Convert NetworkX to igraph
            ig_graph = self._convert_to_igraph()
            
            # Run Louvain
            communities = ig_graph.community_multilevel()
            
            # Convert back to node -> community_id mapping
            partition = {}
            node_list = list(self.graph.nodes())
            for idx, community_nodes in enumerate(communities):
                for node_idx in community_nodes:
                    partition[node_list[node_idx]] = idx
            
            self.communities['igraph_louvain'] = partition
            
            num_communities = len(communities)
            print(f"✓ igraph Louvain detected {num_communities} communities")
            
            return partition
        except Exception as e:
            print(f"Warning: igraph Louvain failed: {e}")
            return None
    
    def _convert_to_igraph(self):
        """Convert NetworkX graph to igraph Graph."""
        # Create mapping from node IDs to indices
        nodes = list(self.graph.nodes())
        node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        
        # Convert edges
        edges = [(node_to_idx[u], node_to_idx[v]) for u, v in self.graph.edges()]
        
        # Create igraph
        ig_graph = ig.Graph(n=len(nodes), edges=edges, directed=self.graph.is_directed())
        
        return ig_graph
    
    def detect_all_communities(self):
        """Run all community detection algorithms."""
        print("\n=== Detecting Communities ===")
        print(f"Graph size: {self.graph.number_of_nodes():,} nodes")
        
        # For very large graphs (>1M nodes), only use Louvain (most efficient)
        if self.graph.number_of_nodes() > 1000000:
            print("Note: Using only Louvain algorithm for very large graph")
            self.louvain_detection()
        else:
            self.louvain_detection()
            self.label_propagation_detection()
            
            # Try igraph if available
            try:
                self.igraph_louvain_detection()
            except:
                pass
        
        print("\n✓ Community detection completed")
    
    def add_communities_to_graph(self, algorithm='louvain'):
        """
        Add community assignments as node attributes.
        
        Args:
            algorithm: Which algorithm's results to use ('louvain', 'label_propagation', etc.)
        """
        if algorithm not in self.communities:
            raise ValueError(f"Algorithm '{algorithm}' not found. Run detection first.")
        
        print(f"Adding {algorithm} communities to graph...")
        
        partition = self.communities[algorithm]
        nx.set_node_attributes(self.graph, partition, f'community_{algorithm}')
        
        print("✓ Communities added to graph")
    
    def get_community_statistics(self, algorithm='louvain'):
        """
        Get statistics about detected communities.
        
        Args:
            algorithm: Which algorithm's results to analyze
            
        Returns:
            Dictionary with community statistics
        """
        if algorithm not in self.communities:
            raise ValueError(f"Algorithm '{algorithm}' not found.")
        
        partition = self.communities[algorithm]
        community_counts = Counter(partition.values())
        
        stats = {
            'num_communities': len(community_counts),
            'largest_community_size': max(community_counts.values()),
            'smallest_community_size': min(community_counts.values()),
            'average_community_size': sum(community_counts.values()) / len(community_counts),
            'community_sizes': dict(community_counts)
        }
        
        return stats
    
    def get_community_members(self, community_id: int, algorithm='louvain'):
        """
        Get all members of a specific community.
        
        Args:
            community_id: The community ID
            algorithm: Which algorithm's results to use
            
        Returns:
            List of node IDs in the community
        """
        if algorithm not in self.communities:
            raise ValueError(f"Algorithm '{algorithm}' not found.")
        
        partition = self.communities[algorithm]
        members = [node for node, comm in partition.items() if comm == community_id]
        
        return members
    
    def calculate_modularity(self, algorithm='louvain'):
        """
        Calculate the modularity of the detected communities.
        
        Args:
            algorithm: Which algorithm's results to evaluate
            
        Returns:
            Modularity score (higher is better)
        """
        if algorithm not in self.communities:
            raise ValueError(f"Algorithm '{algorithm}' not found.")
        
        partition = self.communities[algorithm]
        
        # Convert to undirected for modularity calculation
        if self.graph.is_directed():
            undirected_graph = self.graph.to_undirected()
        else:
            undirected_graph = self.graph
        
        modularity = community_louvain.modularity(partition, undirected_graph)
        
        return modularity


def main():
    """Example usage of CommunityDetector."""
    from importlib import import_module
    
    # Load graph
    graph_constructor = import_module('graph_construction_02')
    constructor = graph_constructor.GraphConstructor("data/edges.csv", "data/nodes.csv")
    graph = constructor.build_graph()
    
    # Detect communities
    detector = CommunityDetector(graph)
    detector.detect_all_communities()
    
    # Add to graph (using Louvain)
    detector.add_communities_to_graph(algorithm='louvain')
    
    # Show statistics
    print("\n=== Community Statistics (Louvain) ===")
    stats = detector.get_community_statistics('louvain')
    print(f"Number of communities: {stats['num_communities']}")
    print(f"Largest community: {stats['largest_community_size']} members")
    print(f"Smallest community: {stats['smallest_community_size']} members")
    print(f"Average community size: {stats['average_community_size']:.2f} members")
    
    # Calculate modularity
    modularity = detector.calculate_modularity('louvain')
    print(f"\nModularity: {modularity:.4f}")
    
    # Show top 5 largest communities
    print("\nTop 5 largest communities:")
    sorted_communities = sorted(stats['community_sizes'].items(), key=lambda x: x[1], reverse=True)[:5]
    for rank, (comm_id, size) in enumerate(sorted_communities, 1):
        print(f"  {rank}. Community {comm_id}: {size} members")


if __name__ == "__main__":
    main()
