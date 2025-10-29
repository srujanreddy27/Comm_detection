"""
Module 7: Visualization
Creates meaningful network visualizations for analysis.
"""

import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np


class NetworkVisualizer:
    """Creates visualizations for social network analysis."""
    
    def __init__(self, graph: nx.Graph, output_dir='output/visualizations'):
        """
        Initialize NetworkVisualizer.
        
        Args:
            graph: NetworkX graph with computed metrics and communities
            output_dir: Directory to save visualizations
        """
        self.graph = graph
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def plot_degree_distribution(self):
        """Plot the degree distribution of the network."""
        print("Creating degree distribution plot...")
        
        if self.graph.is_directed():
            in_degrees = [d for n, d in self.graph.in_degree()]
            out_degrees = [d for n, d in self.graph.out_degree()]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # In-degree distribution
            ax1.hist(in_degrees, bins=50, edgecolor='black', alpha=0.7)
            ax1.set_xlabel('In-Degree')
            ax1.set_ylabel('Frequency')
            ax1.set_title('In-Degree Distribution')
            ax1.set_yscale('log')
            
            # Out-degree distribution
            ax2.hist(out_degrees, bins=50, edgecolor='black', alpha=0.7, color='orange')
            ax2.set_xlabel('Out-Degree')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Out-Degree Distribution')
            ax2.set_yscale('log')
        else:
            degrees = [d for n, d in self.graph.degree()]
            
            plt.figure(figsize=(10, 6))
            plt.hist(degrees, bins=50, edgecolor='black', alpha=0.7)
            plt.xlabel('Degree')
            plt.ylabel('Frequency')
            plt.title('Degree Distribution')
            plt.yscale('log')
        
        plt.tight_layout()
        output_path = self.output_dir / 'degree_distribution.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved to {output_path}")
    
    def plot_community_network(self, community_attr='community_louvain', 
                               max_nodes=1000, layout='spring', show_edge_colors=True):
        """
        Visualize the network colored by communities.
        
        Args:
            community_attr: Name of community attribute
            max_nodes: Maximum nodes to display (default 1000 for large graphs)
            layout: Layout algorithm ('spring', 'kamada_kawai', 'circular')
            show_edge_colors: Color edges based on whether they connect same community
        """
        print(f"Creating community network visualization...")
        
        # For large graphs, always sample nodes
        if self.graph.number_of_nodes() > max_nodes:
            # Sample high-degree nodes for better visualization
            degrees = dict(self.graph.degree())
            top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph(top_nodes).copy()
            print(f"  Showing top {len(subgraph.nodes()):,} nodes (sampled from {self.graph.number_of_nodes():,})")
        else:
            subgraph = self.graph
            print(f"  Showing all {self.graph.number_of_nodes():,} nodes")
        
        # Get community colors
        communities = {}
        for node in subgraph.nodes():
            node_data = subgraph.nodes[node]
            communities[node] = node_data.get(community_attr, 0)
        
        # Create color map
        unique_communities = set(communities.values())
        color_palette = sns.color_palette('husl', len(unique_communities))
        comm_to_color = {comm: color_palette[i] for i, comm in enumerate(unique_communities)}
        node_colors = [comm_to_color[communities[node]] for node in subgraph.nodes()]
        
        # Calculate layout
        if layout == 'spring':
            pos = nx.spring_layout(subgraph, k=0.5, iterations=50, seed=42)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(subgraph)
        else:
            pos = nx.circular_layout(subgraph)
        
        # Calculate node sizes based on degree
        node_sizes = [subgraph.degree(node) * 10 + 20 for node in subgraph.nodes()]
        
        # Prepare edge colors based on community
        edge_colors = []
        intra_count = 0
        inter_count = 0
        
        if show_edge_colors:
            for u, v in subgraph.edges():
                u_comm = communities.get(u, -1)
                v_comm = communities.get(v, -1)
                if u_comm == v_comm and u_comm != -1:
                    edge_colors.append('#00ff00')  # Bright green for intra-community edges
                    intra_count += 1
                else:
                    edge_colors.append('#ff0000')  # Bright red for inter-community edges
                    inter_count += 1
            
            print(f"  Edge breakdown: {intra_count} intra-community (green), {inter_count} inter-community (red)")
        else:
            edge_colors = ['#3498db'] * subgraph.number_of_edges()  # Blue for all edges
        
        # Create plot
        plt.figure(figsize=(16, 12))
        
        # Draw edges with better visibility
        nx.draw_networkx_edges(subgraph, pos, 
                              alpha=0.4, 
                              width=1.5, 
                              arrows=True,
                              arrowsize=10,
                              edge_color=edge_colors,
                              arrowstyle='-|>',
                              connectionstyle='arc3,rad=0.1')
        
        # Draw nodes
        nx.draw_networkx_nodes(subgraph, pos, 
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8,
                              linewidths=0.5,
                              edgecolors='black')
        
        plt.title(f'Network Communities ({len(subgraph.nodes())} nodes, {len(unique_communities)} communities)', 
                 fontsize=16, fontweight='bold')
        
        # Add legend for edge colors
        if show_edge_colors:
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], color='#00ff00', lw=3, label=f'Intra-community ({intra_count} edges)'),
                Line2D([0], [0], color='#ff0000', lw=3, label=f'Inter-community ({inter_count} edges)')
            ]
            plt.legend(handles=legend_elements, loc='upper right', fontsize=12, framealpha=0.9)
        
        plt.axis('off')
        plt.tight_layout()
        
        output_path = self.output_dir / 'community_network.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved to {output_path}")
    
    def plot_top_influencers(self, metric='pagerank', top_n=20):
        """
        Visualize top influencers by a specific metric.
        
        Args:
            metric: Metric to use for ranking
            top_n: Number of top influencers to show
        """
        print(f"Creating top influencers visualization ({metric})...")
        
        # Get metric values
        metric_values = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            value = node_data.get(metric, 0)
            metric_values.append((node, value))
        
        # Sort and get top N
        top_influencers = sorted(metric_values, key=lambda x: x[1], reverse=True)[:top_n]
        
        # Create bar plot
        users = [f"User {user}" for user, _ in top_influencers]
        values = [value for _, value in top_influencers]
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(users, values)
        
        # Color bars by value
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(values)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        plt.xlabel(metric.replace('_', ' ').title(), fontsize=12)
        plt.ylabel('Users', fontsize=12)
        plt.title(f'Top {top_n} Influencers by {metric.replace("_", " ").title()}', 
                 fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        output_path = self.output_dir / f'top_influencers_{metric}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved to {output_path}")
    
    def plot_community_sizes(self, community_attr='community_louvain', top_n=15):
        """
        Visualize community size distribution.
        
        Args:
            community_attr: Name of community attribute
            top_n: Number of top communities to show
        """
        print("Creating community sizes visualization...")
        
        # Count community sizes
        from collections import Counter
        communities = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            comm = node_data.get(community_attr)
            if comm is not None:
                communities.append(comm)
        
        community_counts = Counter(communities)
        top_communities = community_counts.most_common(top_n)
        
        # Create plot
        comm_ids = [f"Community {comm}" for comm, _ in top_communities]
        sizes = [size for _, size in top_communities]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(comm_ids)), sizes, color=sns.color_palette('viridis', len(comm_ids)))
        
        plt.xlabel('Community', fontsize=12)
        plt.ylabel('Number of Members', fontsize=12)
        plt.title(f'Top {top_n} Largest Communities', fontsize=14, fontweight='bold')
        plt.xticks(range(len(comm_ids)), comm_ids, rotation=45, ha='right')
        plt.tight_layout()
        
        output_path = self.output_dir / 'community_sizes.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Saved to {output_path}")
    
    def plot_centrality_comparison(self):
        """Compare different centrality metrics."""
        print("Creating centrality comparison visualization...")
        
        # Get centrality values for sample of nodes
        sample_size = min(50, self.graph.number_of_nodes())
        sample_nodes = list(self.graph.nodes())[:sample_size]
        
        metrics = ['pagerank', 'betweenness_centrality', 'in_degree_centrality']
        available_metrics = []
        
        data = {metric: [] for metric in metrics}
        
        for node in sample_nodes:
            node_data = self.graph.nodes[node]
            for metric in metrics:
                if metric in node_data:
                    data[metric].append(node_data[metric])
                    if metric not in available_metrics:
                        available_metrics.append(metric)
        
        # Create correlation heatmap
        import pandas as pd
        df = pd.DataFrame(data)
        
        if len(df) > 0 and len(available_metrics) > 1:
            plt.figure(figsize=(8, 6))
            correlation = df[available_metrics].corr()
            sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=1, cbar_kws={"shrink": 0.8})
            plt.title('Centrality Metrics Correlation', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            output_path = self.output_dir / 'centrality_correlation.png'
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ Saved to {output_path}")
    
    def visualize_all(self):
        """Create all visualizations."""
        print("\n=== Creating Visualizations ===")
        print(f"Graph size: {self.graph.number_of_nodes():,} nodes, {self.graph.number_of_edges():,} edges")
        
        self.plot_degree_distribution()
        
        # For very large graphs, limit visualization complexity
        if self.graph.number_of_nodes() > 100000:
            print("\nNote: Skipping network plot for very large graph (>100k nodes)")
        else:
            self.plot_community_network(max_nodes=1000)
        
        self.plot_top_influencers(metric='pagerank')
        
        # Only plot betweenness if it was calculated
        has_betweenness = any(
            self.graph.nodes[node].get('betweenness_centrality', 0) > 0 
            for node in list(self.graph.nodes())[:100]
        )
        if has_betweenness:
            self.plot_top_influencers(metric='betweenness_centrality')
        
        self.plot_community_sizes()
        self.plot_centrality_comparison()
        
        print(f"\n✓ All visualizations saved to {self.output_dir}")


def main():
    """Example usage of NetworkVisualizer."""
    from importlib import import_module
    
    # Load and prepare graph
    graph_constructor = import_module('graph_construction_02')
    metric_calculator = import_module('metric_calculation_03')
    community_detector = import_module('community_detection_04')
    
    # Build graph
    constructor = graph_constructor.GraphConstructor("data/edges.csv", "data/nodes.csv")
    graph = constructor.build_graph()
    
    # Add metrics
    calculator = metric_calculator.MetricCalculator(graph)
    calculator.calculate_all_metrics()
    calculator.add_metrics_to_graph()
    
    # Add communities
    detector = community_detector.CommunityDetector(graph)
    detector.detect_all_communities()
    detector.add_communities_to_graph()
    
    # Create visualizations
    visualizer = NetworkVisualizer(graph)
    visualizer.visualize_all()


if __name__ == "__main__":
    main()
