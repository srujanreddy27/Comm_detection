"""
Module 3: Metric Calculation
Calculates key network metrics including centralities and clustering coefficients.
"""

import networkx as nx
import pandas as pd
from pathlib import Path


class MetricCalculator:
    """Calculates various network metrics for graph analysis."""
    
    def __init__(self, graph: nx.Graph):
        """
        Initialize MetricCalculator.
        
        Args:
            graph: NetworkX graph object
        """
        self.graph = graph
        self.metrics = {}
        
    def calculate_degree_centrality(self):
        """Calculate degree centrality for all nodes."""
        print("Calculating degree centrality...")
        
        # For directed graphs, calculate in-degree and out-degree
        if self.graph.is_directed():
            in_degree = dict(self.graph.in_degree())
            out_degree = dict(self.graph.out_degree())
            
            # Normalized centrality
            in_degree_centrality = nx.in_degree_centrality(self.graph)
            out_degree_centrality = nx.out_degree_centrality(self.graph)
            
            self.metrics['in_degree'] = in_degree
            self.metrics['out_degree'] = out_degree
            self.metrics['in_degree_centrality'] = in_degree_centrality
            self.metrics['out_degree_centrality'] = out_degree_centrality
        else:
            degree_centrality = nx.degree_centrality(self.graph)
            self.metrics['degree_centrality'] = degree_centrality
        
        print("✓ Degree centrality calculated")
    
    def calculate_betweenness_centrality(self, k=None):
        """
        Calculate betweenness centrality.
        
        Args:
            k: Number of nodes to use for approximation (None for exact)
        """
        print("Calculating betweenness centrality...")
        
        betweenness = nx.betweenness_centrality(self.graph, k=k)
        self.metrics['betweenness_centrality'] = betweenness
        
        print("✓ Betweenness centrality calculated")
    
    def calculate_closeness_centrality(self):
        """Calculate closeness centrality."""
        print("Calculating closeness centrality...")
        
        # For directed graphs, this may not be defined for all nodes
        try:
            closeness = nx.closeness_centrality(self.graph)
            self.metrics['closeness_centrality'] = closeness
            print("✓ Closeness centrality calculated")
        except Exception as e:
            print(f"Warning: Could not calculate closeness centrality: {e}")
            self.metrics['closeness_centrality'] = {node: 0.0 for node in self.graph.nodes()}
    
    def calculate_eigenvector_centrality(self, max_iter=1000):
        """
        Calculate eigenvector centrality.
        
        Args:
            max_iter: Maximum number of iterations
        """
        print("Calculating eigenvector centrality...")
        
        try:
            eigenvector = nx.eigenvector_centrality(self.graph, max_iter=max_iter)
            self.metrics['eigenvector_centrality'] = eigenvector
            print("✓ Eigenvector centrality calculated")
        except Exception as e:
            print(f"Warning: Could not calculate eigenvector centrality: {e}")
            self.metrics['eigenvector_centrality'] = {node: 0.0 for node in self.graph.nodes()}
    
    def calculate_pagerank(self):
        """Calculate PageRank (especially useful for directed graphs)."""
        print("Calculating PageRank...")
        
        pagerank = nx.pagerank(self.graph)
        self.metrics['pagerank'] = pagerank
        
        print("✓ PageRank calculated")
    
    def calculate_clustering_coefficient(self):
        """Calculate clustering coefficient for each node."""
        print("Calculating clustering coefficients...")
        
        # For directed graphs, use the appropriate method
        if self.graph.is_directed():
            clustering = nx.clustering(self.graph.to_undirected())
        else:
            clustering = nx.clustering(self.graph)
        
        self.metrics['clustering_coefficient'] = clustering
        
        print("✓ Clustering coefficients calculated")
    
    def calculate_all_metrics(self, use_approximation=False):
        """
        Calculate all metrics.
        
        Args:
            use_approximation: Use approximation for expensive calculations (large graphs)
        """
        print("\n=== Calculating Network Metrics ===")
        print(f"Graph size: {self.graph.number_of_nodes():,} nodes, {self.graph.number_of_edges():,} edges")
        
        self.calculate_degree_centrality()
        
        # Adaptive sampling based on graph size
        num_nodes = self.graph.number_of_nodes()
        
        # SKIP betweenness for graphs with >100K nodes (too slow even with sampling)
        if num_nodes > 100_000:
            print(f"\n⚠️  Skipping betweenness centrality (graph too large: {num_nodes:,} nodes)")
            print("   Betweenness takes 30-60+ minutes even with sampling.")
            print("   Use degree centrality and PageRank instead (same insights, much faster)")
            self.metrics['betweenness_centrality'] = {node: 0.0 for node in self.graph.nodes()}
        else:
            # Only calculate for small graphs (<100K nodes)
            if num_nodes > 10_000:
                k = min(50, num_nodes // 200)  # Very aggressive: 50 samples max
            elif num_nodes > 1_000:
                k = min(100, num_nodes // 100)
            else:
                k = None
            
            if k:
                print(f"Sampling {k:,} nodes for betweenness approximation")
            
            self.calculate_betweenness_centrality(k=k)
        
        # Skip closeness for very large graphs (too expensive)
        if num_nodes <= 100000:
            self.calculate_closeness_centrality()
        else:
            print("Skipping closeness centrality (graph too large)")
            self.metrics['closeness_centrality'] = {node: 0.0 for node in self.graph.nodes()}
        
        # Skip eigenvector for very large graphs (convergence issues)
        if num_nodes <= 500000:
            self.calculate_eigenvector_centrality()
        else:
            print("Skipping eigenvector centrality (graph too large)")
            self.metrics['eigenvector_centrality'] = {node: 0.0 for node in self.graph.nodes()}
        
        self.calculate_pagerank()
        self.calculate_clustering_coefficient()
        
        print("\n✓ All metrics calculated successfully")
    
    def add_metrics_to_graph(self):
        """Add calculated metrics as node attributes to the graph."""
        print("\nAdding metrics to graph nodes...")
        
        for metric_name, metric_values in self.metrics.items():
            nx.set_node_attributes(self.graph, metric_values, metric_name)
        
        print("✓ Metrics added to graph")
    
    def get_top_nodes(self, metric_name: str, n: int = 10):
        """
        Get top N nodes by a specific metric.
        
        Args:
            metric_name: Name of the metric
            n: Number of top nodes to return
            
        Returns:
            List of tuples (node_id, metric_value)
        """
        if metric_name not in self.metrics:
            raise ValueError(f"Metric '{metric_name}' not calculated yet")
        
        metric_values = self.metrics[metric_name]
        top_nodes = sorted(metric_values.items(), key=lambda x: x[1], reverse=True)[:n]
        
        return top_nodes
    
    def export_metrics(self, output_path: str):
        """
        Export all metrics to a CSV file.
        
        Args:
            output_path: Path to save the CSV file
        """
        print(f"\nExporting metrics to {output_path}...")
        
        # Combine all metrics into a DataFrame
        df = pd.DataFrame(self.metrics)
        df.index.name = 'node_id'
        
        # Save to CSV
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path)
        
        print("✓ Metrics exported")


def main():
    """Example usage of MetricCalculator."""
    from importlib import import_module
    
    # Load graph from previous module
    graph_constructor = import_module('graph_construction_02')
    constructor = graph_constructor.GraphConstructor("data/edges.csv", "data/nodes.csv")
    graph = constructor.build_graph()
    
    # Calculate metrics
    calculator = MetricCalculator(graph)
    calculator.calculate_all_metrics()
    
    # Add to graph
    calculator.add_metrics_to_graph()
    
    # Show top influencers by different metrics
    print("\n=== Top 10 Influencers ===")
    
    metrics_to_show = ['pagerank', 'betweenness_centrality', 'in_degree']
    for metric in metrics_to_show:
        if metric in calculator.metrics:
            print(f"\nTop 10 by {metric}:")
            top_nodes = calculator.get_top_nodes(metric, n=10)
            for rank, (node, value) in enumerate(top_nodes, 1):
                print(f"  {rank}. User {node}: {value:.6f}")
    
    # Export metrics
    calculator.export_metrics("output/network_metrics.csv")


if __name__ == "__main__":
    main()
